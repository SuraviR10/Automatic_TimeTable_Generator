import os
import sys
import json
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import List, Dict, Any, Optional, Tuple, Set

try:
    from supabase._sync.client import create_client
except ImportError:
    from supabase.client import create_client

os.environ.pop('http_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTPS_PROXY', None)

app = Flask(__name__)
CORS(app)

class UnifiedTimetableEngine:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase = create_client(supabase_url, supabase_key)
        self.global_settings = self._load_global_settings()
        self.work_days = eval(self.global_settings.get('work_days', "['Tuesday','Wednesday','Thursday','Friday','Saturday']"))
        self.periods_per_day = int(self.global_settings.get('periods_per_day', 6))
        self.tea_break_after = int(self.global_settings.get('tea_break_after_period', 2))
        self.lunch_break_after = int(self.global_settings.get('lunch_break_after_period', 4))
        self.master_occupancy: Set[Tuple[str, str, int]] = set()
        
    def _load_global_settings(self) -> Dict[str, str]:
        try:
            response = self.supabase.table('global_settings').select('*').execute()
            return {row['setting_key']: row['setting_value'] for row in response.data}
        except:
            return {}
    
    def _get_valid_lab_slots(self) -> List[Tuple[int, int]]:
        """Get valid 2-hour continuous slots avoiding breaks"""
        valid = []
        for i in range(1, self.periods_per_day):
            # Check if lab would cross tea break (between P2 and P3)
            if i <= self.tea_break_after < i + 1:
                continue
            # Check if lab would cross lunch break (between P4 and P5)
            if i <= self.lunch_break_after < i + 1:
                continue
            valid.append((i, i + 1))
        return valid
    
    def _load_oe_constraints(self, academic_year: str, year: int, semester: int) -> List[Dict]:
        try:
            response = self.supabase.table('open_electives').select('*')\
                .eq('academic_year', academic_year).eq('year', year).eq('semester', semester).execute()
            return response.data or []
        except:
            return []
    
    def check_faculty_conflict_global(self, faculty_name: str, day: str, slot: int, academic_year: str) -> Optional[Dict]:
        if not faculty_name or faculty_name == 'N/A':
            return None
        
        if (faculty_name, day, slot) in self.master_occupancy:
            return {'source': 'current_batch', 'faculty': faculty_name, 'day': day, 'slot': slot}
        
        try:
            response = self.supabase.table('timetables').select('*')\
                .eq('faculty_name', faculty_name).eq('day', day).eq('time_slot', slot)\
                .eq('academic_year', academic_year).eq('is_finalized', True).execute()
            
            if response.data:
                conflict = response.data[0]
                return {
                    'source': 'database',
                    'faculty': faculty_name,
                    'day': day,
                    'slot': slot,
                    'department': conflict.get('department'),
                    'section': conflict.get('section'),
                    'subject': conflict.get('subject_name')
                }
        except:
            pass
        
        return None
    
    def get_safe_slots_for_faculty(self, faculty_name: str, academic_year: str) -> List[Dict]:
        safe_slots = []
        for day in self.work_days:
            for slot in range(1, self.periods_per_day + 1):
                if not self.check_faculty_conflict_global(faculty_name, day, slot, academic_year):
                    safe_slots.append({'day': day, 'slot': slot})
        return safe_slots
    
    def validate_swap_with_suggestions(self, swap_data: Dict, academic_year: str) -> Dict:
        faculty1 = swap_data.get('faculty1')
        faculty2 = swap_data.get('faculty2')
        day1, slot1 = swap_data.get('day1'), swap_data.get('slot1')
        day2, slot2 = swap_data.get('day2'), swap_data.get('slot2')
        
        conflicts = []
        
        conflict1 = self.check_faculty_conflict_global(faculty1, day2, slot2, academic_year)
        if conflict1:
            conflicts.append({
                'faculty': faculty1,
                'target_day': day2,
                'target_slot': slot2,
                'conflict_details': conflict1,
                'safe_slots': self.get_safe_slots_for_faculty(faculty1, academic_year)
            })
        
        conflict2 = self.check_faculty_conflict_global(faculty2, day1, slot1, academic_year)
        if conflict2:
            conflicts.append({
                'faculty': faculty2,
                'target_day': day1,
                'target_slot': slot1,
                'conflict_details': conflict2,
                'safe_slots': self.get_safe_slots_for_faculty(faculty2, academic_year)
            })
        
        return {
            'valid': len(conflicts) == 0,
            'conflicts': conflicts,
            'message': 'Swap is valid' if len(conflicts) == 0 else 'Conflicts detected - see suggestions'
        }
    
    def generate_timetable(self, department: str, section: str, sessions: List[Dict], 
                          academic_year: str, year: int, semester: int) -> Dict:
        
        timetable = {day: {slot: None for slot in range(1, self.periods_per_day + 1)} 
                    for day in self.work_days}
        
        subject_day_tracker = {}
        
        # STEP 0: Pre-fill OE Mega-Constraints
        oe_constraints = self._load_oe_constraints(academic_year, year, semester)
        for oe in oe_constraints:
            day, slot = oe['locked_day'], oe['locked_time_slot']
            oe_session = next((s for s in sessions if s['subject_code'] == oe['oe_subject_code']), None)
            
            if oe_session and day in timetable:
                timetable[day][slot] = {
                    'subject_code': oe['oe_subject_code'],
                    'subject_name': oe['oe_subject_name'],
                    'faculty_name': oe_session.get('faculty_name', 'TBD'),
                    'type': 'theory',
                    'is_oe_locked': True,
                    'room': f'Room-{section}01'
                }
                self.master_occupancy.add((oe_session.get('faculty_name'), day, slot))
        
        # STEP 1: Place NSS/FREE in Period 6 only
        nss_sessions = [s for s in sessions if s['subject_code'].upper() in ['NSS', 'FREE']]
        for nss in nss_sessions:
            available_days = [d for d in self.work_days if timetable[d][self.periods_per_day] is None]
            if not available_days:
                return {'valid': False, 'error': f"No available P6 slot for {nss['subject_code']}"}
            
            nss_day = random.choice(available_days)
            timetable[nss_day][self.periods_per_day] = {
                'subject_code': nss['subject_code'],
                'subject_name': nss['subject_name'],
                'faculty_name': nss.get('faculty_name', 'N/A'),
                'type': 'free',
                'room': f'Room-{section}01'
            }
            if nss.get('faculty_name') and nss.get('faculty_name') != 'N/A':
                self.master_occupancy.add((nss['faculty_name'], nss_day, self.periods_per_day))
        
        # STEP 2: Place labs in valid continuous slots
        labs = [s for s in sessions if s.get('type', '').lower() == 'lab']
        valid_lab_slots = self._get_valid_lab_slots()
        
        for lab in labs:
            placed = False
            attempts = 0
            max_attempts = 100
            
            while not placed and attempts < max_attempts:
                attempts += 1
                day = random.choice(self.work_days)
                slot_pair = random.choice(valid_lab_slots)
                
                if timetable[day][slot_pair[0]] is None and timetable[day][slot_pair[1]] is None:
                    if lab['subject_code'] in subject_day_tracker.get(day, []):
                        continue
                    
                    conflicts = [self.check_faculty_conflict_global(lab['faculty_name'], day, s, academic_year) 
                                for s in slot_pair]
                    
                    if not any(conflicts):
                        for s in slot_pair:
                            timetable[day][s] = {
                                'subject_code': lab['subject_code'],
                                'subject_name': lab['subject_name'],
                                'faculty_name': lab['faculty_name'],
                                'type': 'lab',
                                'room': f'Lab-{section}01',
                                'is_cross_dept': lab.get('is_cross_dept', False),
                                'teaching_dept': lab.get('teaching_dept')
                            }
                            self.master_occupancy.add((lab['faculty_name'], day, s))
                        
                        if day not in subject_day_tracker:
                            subject_day_tracker[day] = []
                        subject_day_tracker[day].append(lab['subject_code'])
                        placed = True
            
            if not placed:
                return {'valid': False, 'error': f"Could not place lab {lab['subject_code']} - no valid slots"}
        
        # STEP 3: Place theory subjects with strict constraints
        theory = [s for s in sessions if s.get('type', '').lower() == 'theory' 
                 and s['subject_code'].upper() not in ['NSS', 'FREE']]
        
        for session in theory:
            weekly_hours = session.get('weekly_hours', 3)
            hours_placed = 0
            
            available_days = list(self.work_days)
            random.shuffle(available_days)
            
            for day in available_days:
                if hours_placed >= weekly_hours:
                    break
                
                if session['subject_code'] in subject_day_tracker.get(day, []):
                    continue
                
                available_slots = [s for s in range(1, self.periods_per_day + 1) 
                                  if timetable[day][s] is None]
                random.shuffle(available_slots)
                
                for slot in available_slots:
                    conflict = self.check_faculty_conflict_global(session['faculty_name'], day, slot, academic_year)
                    
                    if not conflict:
                        timetable[day][slot] = {
                            'subject_code': session['subject_code'],
                            'subject_name': session['subject_name'],
                            'faculty_name': session['faculty_name'],
                            'type': 'theory',
                            'room': f'Room-{section}01',
                            'is_cross_dept': session.get('is_cross_dept', False),
                            'teaching_dept': session.get('teaching_dept')
                        }
                        self.master_occupancy.add((session['faculty_name'], day, slot))
                        
                        if day not in subject_day_tracker:
                            subject_day_tracker[day] = []
                        subject_day_tracker[day].append(session['subject_code'])
                        
                        hours_placed += 1
                        break
            
            if hours_placed < weekly_hours:
                return {'valid': False, 'error': f"Could not place all hours for {session['subject_code']} ({hours_placed}/{weekly_hours})"}
        
        violations = self._validate_all_constraints(timetable, sessions)
        
        if violations:
            return {'valid': False, 'error': 'Constraint violations', 'violations': violations}
        
        return {'valid': True, 'timetable': timetable, 'section_name': section, 'department': department}
    
    def _validate_all_constraints(self, timetable: Dict, sessions: List[Dict]) -> List[str]:
        violations = []
        
        # CONSTRAINT 1: Strict weekly hours
        subject_hours = {}
        for day in self.work_days:
            for slot in range(1, self.periods_per_day + 1):
                entry = timetable[day].get(slot)
                if entry:
                    code = entry['subject_code']
                    subject_hours[code] = subject_hours.get(code, 0) + 1
        
        for session in sessions:
            expected = session.get('weekly_hours', 3)
            actual = subject_hours.get(session['subject_code'], 0)
            if actual != expected:
                violations.append(f"{session['subject_code']}: Expected {expected} hours, got {actual}")
        
        # CONSTRAINT 2: No same subject twice per day
        for day in self.work_days:
            day_subjects = []
            for slot in range(1, self.periods_per_day + 1):
                entry = timetable[day].get(slot)
                if entry and entry['subject_code'] not in ['FREE', 'NSS']:
                    if entry['subject_code'] in day_subjects:
                        violations.append(f"{entry['subject_code']} repeated on {day}")
                    day_subjects.append(entry['subject_code'])
        
        # CONSTRAINT 3: Labs in valid continuous slots
        valid_lab_slots = self._get_valid_lab_slots()
        for day in self.work_days:
            for slot in range(1, self.periods_per_day):
                entry = timetable[day].get(slot)
                if entry and entry.get('type') == 'lab':
                    if (slot, slot + 1) not in valid_lab_slots:
                        violations.append(f"Lab {entry['subject_code']} at invalid slot {day} P{slot}")
        
        # CONSTRAINT 4: NSS/FREE only in last period
        for day in self.work_days:
            for slot in range(1, self.periods_per_day):
                entry = timetable[day].get(slot)
                if entry and entry['subject_code'] in ['NSS', 'FREE']:
                    violations.append(f"NSS/FREE found in P{slot} on {day}, must be in P{self.periods_per_day}")
        
        return violations
    
    def save_to_database(self, timetable: Dict, section: str, department: str,
                        academic_year: str, year: int, semester: int) -> None:
        rows = []
        processed_labs = set()
        
        for day in self.work_days:
            for slot in range(1, self.periods_per_day + 1):
                entry = timetable[day].get(slot)
                
                if not entry:
                    continue
                
                if entry.get('type') == 'lab':
                    lab_key = f"{day}-{entry['subject_code']}-{section}"
                    if lab_key in processed_labs:
                        continue
                    processed_labs.add(lab_key)
                
                faculty_dept = entry.get('teaching_dept') if entry.get('is_cross_dept') else department
                
                rows.append({
                    'department': department,
                    'section': section,
                    'day': day,
                    'time_slot': slot,
                    'subject_code': entry['subject_code'],
                    'subject_name': entry['subject_name'],
                    'faculty_name': entry['faculty_name'],
                    'faculty_department': faculty_dept,
                    'room': entry['room'],
                    'academic_year': academic_year,
                    'year': year,
                    'semester': semester,
                    'type': entry.get('type', 'theory'),
                    'is_cross_dept': entry.get('is_cross_dept', False),
                    'teaching_dept': entry.get('teaching_dept'),
                    'is_finalized': False,
                    'is_oe_locked': entry.get('is_oe_locked', False)
                })
        
        self.supabase.table('timetables').delete()\
            .eq('department', department).eq('section', section)\
            .eq('academic_year', academic_year).eq('year', year).eq('semester', semester).execute()
        
        if rows:
            self.supabase.table('timetables').insert(rows).execute()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://bkmzyhroignpjebfpqug.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJrbXp5aHJvaWducGplYmZwcXVnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc0MjA1NDUsImV4cCI6MjA3Mjk5NjU0NX0.ICE2eYzFZvz0dtNpAa5YlJTZD-idc2J76wn1ZeHwwck")

@app.route('/generate', methods=['POST'])
def generate_timetable():
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'JSON required'}), 400
        
        department = payload.get('department')
        semester = int(payload.get('semester'))
        year = int(payload.get('year'))
        academic_year = payload.get('academic_year') or payload.get('academicYear')
        sections = payload.get('sections', [])
        
        engine = UnifiedTimetableEngine(SUPABASE_URL, SUPABASE_KEY)
        results = {}
        
        for sec in sections:
            sec_name = sec.get('name') or sec.get('section')
            assignments = sec.get('assignments') or sec.get('data')
            
            sessions = []
            for a in assignments:
                sessions.append({
                    'subject_code': a.get('subject') or a.get('subject_code'),
                    'subject_name': a.get('subject_name') or a.get('subject'),
                    'faculty_name': a.get('faculty') or a.get('faculty_name'),
                    'weekly_hours': int(a.get('weekly_hours', 3)),
                    'type': a.get('type', 'theory').lower(),
                    'is_cross_dept': a.get('is_cross_dept', False),
                    'teaching_dept': a.get('teaching_dept')
                })
            
            result = engine.generate_timetable(department, sec_name, sessions, academic_year, year, semester)
            
            if result['valid']:
                engine.save_to_database(result['timetable'], sec_name, department, academic_year, year, semester)
            
            results[sec_name] = result
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/validate_swap', methods=['POST'])
def validate_swap():
    try:
        payload = request.get_json()
        academic_year = payload.get('academic_year')
        swap_data = payload.get('swap_data')
        
        engine = UnifiedTimetableEngine(SUPABASE_URL, SUPABASE_KEY)
        result = engine.validate_swap_with_suggestions(swap_data, academic_year)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/finalize_timetable', methods=['POST'])
def finalize_timetable():
    try:
        payload = request.get_json()
        department = payload.get('department')
        academic_year = payload.get('academic_year')
        year = payload.get('year')
        semester = payload.get('semester')
        timetable_data = payload.get('timetable_data')

        if not all([department, academic_year, year, semester, timetable_data]):
             return jsonify({'error': 'Missing required fields'}), 400

        engine = UnifiedTimetableEngine(SUPABASE_URL, SUPABASE_KEY)
        
        # Clean up existing finalized data for this batch to prevent duplicates
        # This overwrites the finalized schedule for this specific semester batch
        engine.supabase.table('timetables').delete()\
            .eq('department', department)\
            .eq('academic_year', academic_year)\
            .eq('year', year)\
            .eq('semester', semester)\
            .eq('is_finalized', True)\
            .execute()

        # Prepare data for insertion
        rows = []
        for entry in timetable_data:
            entry['is_finalized'] = True
            # Ensure defaults for optional fields if missing from frontend payload
            if 'faculty_department' not in entry:
                entry['faculty_department'] = department
            if 'is_oe_locked' not in entry:
                entry['is_oe_locked'] = False
            rows.append(entry)

        # Insert in batches to handle database limits
        batch_size = 100
        for i in range(0, len(rows), batch_size):
            engine.supabase.table('timetables').insert(rows[i:i+batch_size]).execute()

        return jsonify({'success': True, 'saved_count': len(rows)})

    except Exception as e:
        print(f"Error finalizing: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_safe_slots', methods=['POST'])
def get_safe_slots():
    try:
        payload = request.get_json()
        faculty_name = payload.get('faculty_name')
        academic_year = payload.get('academic_year')
        
        engine = UnifiedTimetableEngine(SUPABASE_URL, SUPABASE_KEY)
        safe_slots = engine.get_safe_slots_for_faculty(faculty_name, academic_year)
        
        return jsonify({'safe_slots': safe_slots, 'count': len(safe_slots)})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Unified Timetable Engine Running'})

if __name__ == '__main__':
    print("🚀 MIT Mysore Unified Timetable Engine")
    print("✅ All constraints enforced")
    print("✅ Global faculty conflict detection")
    print("✅ Smart swap with suggestions")
    print("✅ OE Mega-Constraint support")
    print("\nServer: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
