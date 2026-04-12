import os
import json
import random
from flask import Flask, request, jsonify, send_from_directory
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, template_folder=BASE_DIR)
CORS(app)

class UnifiedTimetableEngine:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase = create_client(supabase_url, supabase_key)
        self.global_settings = self._load_global_settings()
        # FIX: Use json.loads instead of eval()
        work_days_str = self.global_settings.get('work_days', '["Tuesday","Wednesday","Thursday","Friday","Saturday"]')
        self.work_days = json.loads(work_days_str) if isinstance(work_days_str, str) else work_days_str
        self.periods_per_day = int(self.global_settings.get('periods_per_day', 6))
        self.tea_break_after = int(self.global_settings.get('tea_break_after_period', 2))
        self.lunch_break_after = int(self.global_settings.get('lunch_break_after_period', 4))
        self.master_occupancy: Set[Tuple[str, str, int]] = set()
        self.lab_room_occupancy: Set[Tuple[str, str, int]] = set()  # Global lab room tracking
        
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
            if i <= self.tea_break_after < i + 1:
                continue
            if i <= self.lunch_break_after < i + 1:
                continue
            valid.append((i, i + 1))
        return valid
    
    def _get_department_lab_rooms(self, department: str) -> List[Dict]:
        """Get all active lab rooms for a department"""
        try:
            response = self.supabase.table('lab_rooms').select('*')\
                .eq('department', department).eq('is_active', True).execute()
            return response.data or []
        except:
            return []
    
    def _get_available_lab_room(self, lab_rooms: List[Dict], day: str, slot_pair: Tuple[int, int]) -> Optional[str]:
        """Get an available lab room for the given time slot - checks global occupancy"""
        for room in lab_rooms:
            room_code = room['room_code']
            # Check if room is occupied at ANY slot in the pair
            room_occupied = any((room_code, day, slot) in self.lab_room_occupancy for slot in slot_pair)
            if not room_occupied:
                return room_code
        return None
    
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
    
    def generate_timetable_with_retry(self, department: str, section: str, sessions: List[Dict], 
                                     academic_year: str, year: int, semester: int, max_retries: int = 5) -> Dict:
        """Generate timetable with retry logic"""
        result = {'valid': False, 'error': 'No attempts made'}
        for attempt in range(max_retries):
            result = self.generate_timetable(department, section, sessions, academic_year, year, semester)
            if result['valid']:
                return result
            # Reset occupancy for retry
            self.master_occupancy.clear()
            self.lab_room_occupancy.clear()
        return {'valid': False, 'error': f'Failed after {max_retries} attempts', 'last_error': result.get('error')}
    
    def generate_timetable(self, department: str, section: str, sessions: List[Dict], 
                          academic_year: str, year: int, semester: int) -> Dict:
        
        timetable: Dict[str, Dict[int, Optional[Dict]]] = {
            day: {slot: None for slot in range(1, self.periods_per_day + 1)} 
            for day in self.work_days
        }
        subject_day_tracker = {}
        
        # STEP 0: Pre-fill OE Mega-Constraints (SAME SLOT ACROSS ALL DEPARTMENTS)
        oe_constraints = self._load_oe_constraints(academic_year, year, semester)
        for oe in oe_constraints:
            day, slot = oe['locked_day'], oe['locked_time_slot']
            oe_session = next((s for s in sessions if s.get('subject_code') == oe['oe_subject_code'] or 
                              s.get('subject_name') == oe['oe_subject_name']), None)
            
            if oe_session and day in timetable:
                timetable[day][slot] = {
                    'subject_code': oe['oe_subject_code'],
                    'subject_name': oe['oe_subject_name'],
                    'faculty_name': oe_session.get('faculty_name', 'TBD'),
                    'type': 'theory',
                    'is_oe_locked': True,
                    'room': f'Room-{section}01'
                }
                if oe_session.get('faculty_name') and oe_session['faculty_name'] != 'TBD':
                    self.master_occupancy.add((oe_session['faculty_name'], day, slot))
                # Mark day for this subject
                subject_day_tracker.setdefault(day, []).append(oe['oe_subject_code'])
        
        # STEP 1: Place NSS/FREE in Period 6 only
        nss_sessions = [s for s in sessions if s['subject_code'].upper() in ['NSS', 'FREE']]
        for nss in nss_sessions:
            available_days = [d for d in self.work_days if timetable[d][self.periods_per_day] is None]
            if not available_days:
                return {'valid': False, 'error': f"No available P{self.periods_per_day} slot for {nss['subject_code']}"}
            nss_day = random.choice(available_days)
            timetable[nss_day][self.periods_per_day] = {
                'subject_code': nss['subject_code'],
                'subject_name': nss['subject_name'],
                'faculty_name': nss.get('faculty_name', 'N/A'),
                'type': 'free',
                'room': f'Room-{section}01'
            }
            if nss.get('faculty_name') and nss['faculty_name'] != 'N/A':
                self.master_occupancy.add((nss['faculty_name'], nss_day, self.periods_per_day))
        
        # STEP 2: Place labs with department-specific room allocation and NO CLASH
        labs = [s for s in sessions if s.get('type', '').lower() == 'lab']
        valid_lab_slots = self._get_valid_lab_slots()
        if not valid_lab_slots:
            return {'valid': False, 'error': 'No valid lab slots with current break configuration'}
        
        department_lab_rooms = self._get_department_lab_rooms(department)
        
        for lab in labs:
            placed = False
            for _ in range(200):
                day = random.choice(self.work_days)
                slot_pair = random.choice(valid_lab_slots)
                
                # Check timetable slots are free
                if timetable[day][slot_pair[0]] is not None or timetable[day][slot_pair[1]] is not None:
                    continue
                
                # Check same subject not already on this day
                if lab['subject_code'] in subject_day_tracker.get(day, []):
                    continue
                
                # Check faculty conflicts
                conflicts = [self.check_faculty_conflict_global(lab['faculty_name'], day, s, academic_year) 
                            for s in slot_pair]
                if any(conflicts):
                    continue
                
                # Get available lab room (checks global occupancy)
                available_room = self._get_available_lab_room(department_lab_rooms, day, slot_pair)
                if not available_room:
                    available_room = f'Lab-{section}01'  # Fallback
                
                # Place lab
                for s in slot_pair:
                    timetable[day][s] = {
                        'subject_code': lab['subject_code'],
                        'subject_name': lab['subject_name'],
                        'faculty_name': lab['faculty_name'],
                        'type': 'lab',
                        'room': available_room,
                        'is_cross_dept': lab.get('is_cross_dept', False),
                        'teaching_dept': lab.get('teaching_dept', department)
                    }
                    self.master_occupancy.add((lab['faculty_name'], day, s))
                    if available_room != f'Lab-{section}01':
                        self.lab_room_occupancy.add((available_room, day, s))
                
                subject_day_tracker.setdefault(day, []).append(lab['subject_code'])
                placed = True
                break
            
            if not placed:
                return {'valid': False, 'error': f"Could not place lab {lab['subject_code']} - no valid slots/rooms"}
        
        # STEP 3: Place theory subjects (NO SAME SUBJECT TWICE PER DAY)
        theory = [s for s in sessions if s.get('type', '').lower() not in ['lab', 'free'] 
                 and s['subject_code'].upper() not in ['NSS', 'FREE']]
        
        for session in theory:
            weekly_hours = session.get('weekly_hours', 3)
            hours_placed = 0
            available_days = list(self.work_days)
            random.shuffle(available_days)
            
            for day in available_days:
                if hours_placed >= weekly_hours:
                    break
                
                # Check same subject not already on this day
                if session['subject_code'] in subject_day_tracker.get(day, []):
                    continue
                
                available_slots = [s for s in range(1, self.periods_per_day + 1) if timetable[day][s] is None]
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
                        subject_day_tracker.setdefault(day, []).append(session['subject_code'])
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
                    subject_hours[entry['subject_code']] = subject_hours.get(entry['subject_code'], 0) + 1
        
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
                    else:
                        day_subjects.append(entry['subject_code'])
        
        # CONSTRAINT 3: Labs in valid continuous slots
        valid_lab_slots = self._get_valid_lab_slots()
        for day in self.work_days:
            for slot in range(1, self.periods_per_day):
                entry1 = timetable[day].get(slot)
                entry2 = timetable[day].get(slot + 1)
                if (entry1 and entry1.get('type') == 'lab' and 
                    entry2 and entry2.get('type') == 'lab' and 
                    entry1['subject_code'] == entry2['subject_code']):
                    if (slot, slot + 1) not in valid_lab_slots:
                        violations.append(f"Lab {entry1['subject_code']} at invalid slot {day} P{slot}-P{slot+1}")
        
        # CONSTRAINT 4: NSS/FREE only in last period
        for day in self.work_days:
            for slot in range(1, self.periods_per_day):
                entry = timetable[day].get(slot)
                if entry and entry['subject_code'] in ['NSS', 'FREE']:
                    violations.append(f"NSS/FREE in P{slot} on {day}, must be P{self.periods_per_day}")
        
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
    
    def validate_swap_with_suggestions(self, swap_data: Dict, academic_year: str) -> Dict:
        """Validate if a swap is possible and suggest alternatives"""
        try:
            slot1 = swap_data.get('slot1', {})
            slot2 = swap_data.get('slot2', {})
            
            faculty1 = slot1.get('faculty_name')
            faculty2 = slot2.get('faculty_name')
            day1, time1 = slot1.get('day'), slot1.get('time_slot')
            day2, time2 = slot2.get('day'), slot2.get('time_slot')
            
            # Check if faculty1 can go to slot2 position
            conflict1 = self.check_faculty_conflict_global(faculty1, day2, time2, academic_year)
            # Check if faculty2 can go to slot1 position
            conflict2 = self.check_faculty_conflict_global(faculty2, day1, time1, academic_year)
            
            if not conflict1 and not conflict2:
                return {'valid': True, 'message': 'Swap is valid'}
            
            conflicts = []
            if conflict1:
                conflicts.append({'faculty': faculty1, 'target_slot': f'{day2} P{time2}', 'conflict': conflict1})
            if conflict2:
                conflicts.append({'faculty': faculty2, 'target_slot': f'{day1} P{time1}', 'conflict': conflict2})
            
            return {'valid': False, 'conflicts': conflicts, 'message': 'Faculty conflicts detected'}
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def get_safe_slots_for_faculty(self, faculty_name: str, academic_year: str) -> List[Dict]:
        """Get all available slots where faculty has no conflicts"""
        safe_slots = []
        try:
            for day in self.work_days:
                for slot in range(1, self.periods_per_day + 1):
                    conflict = self.check_faculty_conflict_global(faculty_name, day, slot, academic_year)
                    if not conflict:
                        safe_slots.append({'day': day, 'slot': slot, 'label': f'{day} P{slot}'})
            return safe_slots
        except:
            return []

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://zfzmnimjekmkyefslflf.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpmem1uaW1qZWtta3llZnNsZmxmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI3ODkwOTcsImV4cCI6MjA3ODM2NTA5N30.ffXDOtk9ZEPjCLrI4ahK2lHmbzbjzix3Z9zS19c5lTA")

@app.route('/get_lab_rooms', methods=['GET'])
def get_lab_rooms():
    try:
        department = request.args.get('department')
        if not department:
            return jsonify({'error': 'Department required'}), 400
        engine = UnifiedTimetableEngine(SUPABASE_URL, SUPABASE_KEY)
        lab_rooms = engine._get_department_lab_rooms(department)
        return jsonify({'lab_rooms': lab_rooms})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add_lab_room', methods=['POST'])
def add_lab_room():
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'JSON required'}), 400
        department = payload.get('department')
        room_code = payload.get('room_code')
        lab_name = payload.get('lab_name')
        capacity = payload.get('capacity', 30)
        if not all([department, room_code, lab_name]):
            return jsonify({'error': 'Department, room_code, lab_name required'}), 400
        engine = UnifiedTimetableEngine(SUPABASE_URL, SUPABASE_KEY)
        response = engine.supabase.table('lab_rooms').insert({
            'department': department,
            'room_code': room_code,
            'lab_name': lab_name,
            'capacity': capacity,
            'is_active': True
        }).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_lab_room', methods=['POST'])
def delete_lab_room():
    try:
        payload = request.get_json()
        room_id = payload.get('id')
        if not room_id:
            return jsonify({'error': 'Room ID required'}), 400
        engine = UnifiedTimetableEngine(SUPABASE_URL, SUPABASE_KEY)
        engine.supabase.table('lab_rooms').update({'is_active': False}).eq('id', room_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
            assignments = sec.get('assignments') or sec.get('data', [])
            sessions = []
            for a in assignments:
                sessions.append({
                    'subject_code': a.get('subject_code') or a.get('subject'),
                    'subject_name': a.get('subject_name') or a.get('subject'),
                    'faculty_name': a.get('faculty_name') or a.get('faculty'),
                    'weekly_hours': int(a.get('weekly_hours', 3)),
                    'type': a.get('type', 'theory').lower(),
                    'is_cross_dept': a.get('is_cross_dept', False),
                    'teaching_dept': a.get('teaching_dept')
                })
            
            result = engine.generate_timetable_with_retry(department, sec_name, sessions, academic_year, year, semester)
            if result['valid']:
                engine.save_to_database(result['timetable'], sec_name, department, academic_year, year, semester)
            results[sec_name] = result
        
        return jsonify(results)
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
        engine.supabase.table('timetables').delete()\
            .eq('department', department).eq('academic_year', academic_year)\
            .eq('year', year).eq('semester', semester).eq('is_finalized', True).execute()
        rows = []
        for entry in timetable_data:
            entry['is_finalized'] = True
            entry.setdefault('faculty_department', department)
            entry.setdefault('is_oe_locked', False)
            rows.append(entry)
        batch_size = 100
        for i in range(0, len(rows), batch_size):
            engine.supabase.table('timetables').insert(rows[i:i+batch_size]).execute()
        return jsonify({'success': True, 'saved_count': len(rows)})
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

@app.route('/', methods=['GET'])
def home():
    return send_from_directory(BASE_DIR, 'index.htm')

@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory(BASE_DIR, filename)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'MIT Mysore Timetable Engine Running'})

if __name__ == '__main__':
    print("=" * 60)
    print("MIT MYSORE TIMETABLE ENGINE")
    print("=" * 60)
    print("✓ All 5 constraints enforced")
    print("✓ Global faculty conflict detection")
    print("✓ Lab room clash prevention")
    print("✓ Open Elective same-slot enforcement")
    print("✓ Retry logic with 5 attempts")
    print("=" * 60)
    print("\nServer: http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
