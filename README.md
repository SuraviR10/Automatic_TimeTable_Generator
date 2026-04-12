# MIT Mysore Timetable Generator

Complete automated timetable generation system with all constraints enforced.

## Features

### ✅ All 5 Hard Constraints Enforced
1. **Strict Weekly Hours** - Each subject placed exactly `weekly_hours` times
2. **Daily Diversity** - Same subject cannot appear twice on same day
3. **Lab Continuity** - Labs always in 2 consecutive periods, never crossing breaks
4. **NSS/FREE → P6 Only** - These subjects only in last period
5. **Global Faculty Conflict** - Faculty cannot teach two classes simultaneously

### 🔬 Lab Management
- Department-specific lab rooms
- Lab room clash prevention across all sections
- Custom lab names and capacity tracking
- No lab can be used by multiple classes at same time

### 🎓 Open Elective (OE) Constraint
- OE subjects locked to SAME time slot across ALL departments
- Admin sets the locked day+slot for each OE
- Applies only to specific semester (e.g., 5th sem OE doesn't affect 3rd sem)

### 🔄 Retry Logic
- 5 automatic retry attempts if generation fails
- Randomized placement for better success rate

## Setup Instructions

### 1. Install Python
```bash
py --version  # Should show Python 3.11+
```

### 2. Install Dependencies
```bash
cd TT_final-main
pip install -r requirements.txt
```

### 3. Setup Database
1. Go to https://supabase.com
2. Open SQL Editor
3. Run `database_setup.sql` (creates all tables)
4. Default admin login: `admin` / `Admin@1234`

### 4. Start Server
```bash
py unified_server.py
```

Server runs at: http://localhost:5000

## Usage Flow

### For Admin
1. Login at http://localhost:5000 → Admin Login
2. Set working days (default: Tue-Sat)
3. Set periods per day, break timings
4. Lock Open Elective slots (e.g., OE601 → Thursday P3 for all depts)

### For Department
1. Login at http://localhost:5000 → Department Login
2. **Lab Management** → Add lab rooms (e.g., ISE-LAB-01, Database Lab, 30 capacity)
3. **Subject Database** → Add subjects
   - Mark cross-department subjects (faculty from other dept)
   - Mark Open Electives (admin will lock slot)
   - Set weekly hours (3 for theory, 2 for lab)
4. **Faculty Core** → Add faculty
5. **Timetable Generator** → Load subjects → Assign faculty → Generate
6. **Enhanced View** → Smart swap, PDF export, Finalize

## Constraints in Detail

### 1. Weekly Hours (Strict)
```
Subject: DBMS, Weekly Hours: 3
✓ Placed exactly 3 times in the week
✗ Placed 2 or 4 times = VIOLATION
```

### 2. Daily Diversity
```
Monday:
✓ P1: DBMS, P3: OS, P5: CN
✗ P1: DBMS, P3: DBMS = VIOLATION (same subject twice)
```

### 3. Lab Continuity (2 Hours)
```
Valid Lab Slots:
✓ P1-P2 (9:00-11:00)
✓ P3-P4 (11:15-13:15)
✓ P5-P6 (14:00-16:00)

Invalid:
✗ P2-P3 (crosses tea break at 11:00)
✗ P4-P5 (crosses lunch break at 13:15)
```

### 4. NSS/FREE → P6 Only
```
✓ Saturday P6: NSS
✗ Tuesday P3: NSS = VIOLATION
```

### 5. Global Faculty Conflict
```
Dr. Smith teaching:
- ISE Section A: Monday P1
✗ Cannot teach CSE Section B: Monday P1 = CONFLICT
```

### 6. Lab Room Clash Prevention
```
ISE-LAB-01:
- ISE Section A: Monday P1-P2 (DBMS Lab)
✗ ISE Section B: Monday P1-P2 = CLASH
✓ ISE Section B: Monday P3-P4 = OK
```

### 7. Open Elective Same-Slot
```
Admin locks: OE601 (Machine Learning) → Thursday P3

Result:
✓ ISE Section A: Thursday P3 = OE601
✓ CSE Section B: Thursday P3 = OE601
✓ ECE Section A: Thursday P3 = OE601
All departments MUST have OE at same time
```

## File Structure

```
TT_final-main/
├── unified_server.py          # Main Flask server (ALL LOGIC HERE)
├── database_setup.sql          # Complete DB schema
├── requirements.txt            # Python dependencies
├── START.bat                   # Quick start script
├── index.htm                   # Login (dept + admin)
├── global-admin.htm            # Admin dashboard
├── page.htm                    # Department dashboard
├── subject.htm                 # Subject management
├── faculty.htm                 # Faculty management
├── lab.htm                     # Lab room management
├── timetable-new.htm           # Generator UI
├── enhanced.htm                # View/edit/finalize
├── vault.htm                   # Saved timetables
└── README.md                   # This file
```

## API Endpoints

```
GET  /health                    # Server status
POST /generate                  # Generate timetable (with retry)
POST /finalize_timetable        # Mark as finalized
POST /validate_swap             # Check faculty conflicts
POST /get_safe_slots            # Get available slots for faculty
GET  /get_lab_rooms             # Get dept lab rooms
POST /add_lab_room              # Add new lab room
POST /delete_lab_room           # Soft delete lab room
```

## Troubleshooting

### Server won't start
```bash
# Check Python
py --version

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check port 5000 is free
netstat -ano | findstr :5000
```

### Generation fails
- Check all subjects have `weekly_hours` set
- Ensure enough time slots (5 days × 6 periods = 30 slots)
- Check lab rooms exist for department
- Verify faculty assigned to all subjects

### Faculty conflicts
- Use "Smart Swap" in enhanced.htm
- System suggests safe slots automatically
- Admin override available after finalization

## Database Tables

- `subjects` - Course subjects (with `is_open_elective` flag)
- `faculty` - Faculty members
- `lab_rooms` - Department lab rooms (with `is_active` flag)
- `timetables` - Generated schedules (with `is_finalized` flag)
- `global_settings` - Admin-controlled settings
- `open_electives` - OE locked slots
- `admin_users` - Admin credentials
- `users` - Department credentials

## Support

For issues:
1. Check server console for errors
2. Check browser console (F12)
3. Verify database tables exist
4. Ensure Supabase connection working

## License

MIT License - Maharaja Institute of Technology, Mysore
