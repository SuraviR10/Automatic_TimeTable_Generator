# MIT MYSORE TIMETABLE GENERATOR - COMPLETE DOCUMENTATION

## QUICK START

### 1. Start Server
```bash
cd c:\Users\surav\Downloads\TT_final-main
py unified_server.py
```

### 2. Open Browser
```
http://localhost:5000
```

### 3. Login Credentials
- **Username**: `MIT Mysore`
- **Password**: `mitm@1234`
- Works for both Department and Administrator

---

## SYSTEM FEATURES

### ✅ All 7 Constraints Enforced
1. **Strict Weekly Hours** - Each subject placed exactly as specified
2. **Daily Diversity** - No subject repeats on same day
3. **Lab Continuity** - Labs in 2-hour blocks (P1-P2, P3-P4, P5-P6)
4. **NSS/FREE → P6 Only** - Only in last period
5. **Global Faculty Conflict** - No double-booking across departments
6. **Lab Room Clash Prevention** - No room conflicts
7. **Open Elective Same-Slot** - Same slot across all departments

### 🔄 Retry Logic
- 5 automatic attempts if generation fails
- Randomized placement for better success rate

### 🎓 Department Features
- Subject management with Open Elective marking
- Faculty management
- Lab room management (department-specific)
- Timetable generation with faculty assignment
- Smart swap with conflict detection
- PDF export
- Finalize and save to vault

### ⚙️ Administrator Features
- Configure work days (default: Tue-Sat)
- Set periods per day (default: 6)
- Configure break timings
- Lock Open Elective slots (enforced globally)
- All settings apply to entire system

---

## USER FLOWS

### DEPARTMENT FLOW

1. **Login**
   - Click "Department"
   - Select department (e.g., ISE)
   - Enter: `MIT Mysore` / `mitm@1234`
   - Redirects to dashboard

2. **Setup**
   - **Subject Database**: Add subjects, mark Open Electives
   - **Faculty Core**: Add faculty members
   - **Lab Management**: Add lab rooms

3. **Generate Timetable**
   - Select year, semester, sections
   - Load subjects
   - Assign faculty to each subject
   - Click "Generate Timetable"
   - Wait 5-30 seconds

4. **View & Edit**
   - View generated timetable
   - Use Smart Swap to rearrange
   - Export to PDF
   - Finalize to vault

### ADMINISTRATOR FLOW

1. **Login**
   - Click "Administrator"
   - Enter: `MIT Mysore` / `mitm@1234`
   - Redirects to admin dashboard

2. **Configure System**
   - **Work Days**: Select working days (min 5)
   - **Time Slots**: Set periods, start/end times
   - **Breaks**: Configure tea and lunch breaks
   - **Open Electives**: Lock OE to specific day+slot

3. **Save Settings**
   - Click "Save Global Configuration"
   - Settings apply to all departments immediately

---

## FILE STRUCTURE

```
TT_final-main/
├── unified_server.py          # Main Flask server
├── database_setup.sql          # Database schema
├── requirements.txt            # Python dependencies
├── START.bat                   # Quick start script
├── README.md                   # This file
├── index.htm                   # Login page
├── page.htm                    # Department dashboard
├── global-admin.htm            # Admin dashboard
├── subject.htm                 # Subject management
├── faculty.htm                 # Faculty management
├── lab.htm                     # Lab room management
├── timetable-new.htm           # Timetable generator
├── enhanced.htm                # Timetable display/edit
├── vault.htm                   # Saved timetables
├── dashboard.htm               # Analytics
├── faculty-timetable.htm       # Faculty schedule
├── left-logo.png               # Logo
└── right-logo.png              # Logo
```

---

## DATABASE TABLES

- `subjects` - Course subjects with `is_open_elective` flag
- `faculty` - Faculty members per department
- `lab_rooms` - Department lab rooms with capacity
- `timetables` - Generated timetables with `is_finalized` flag
- `global_settings` - Admin settings (periods, breaks, work days)
- `open_electives` - OE constraints with locked day/slot
- `users` - Department login
- `admin_users` - Admin login

---

## API ENDPOINTS

- `GET /health` - Server status
- `POST /generate` - Generate timetable with retry
- `POST /finalize_timetable` - Save to vault
- `POST /validate_swap` - Check faculty conflicts
- `POST /get_safe_slots` - Get available slots
- `GET /get_lab_rooms` - Get department lab rooms
- `POST /add_lab_room` - Add new lab room
- `POST /delete_lab_room` - Soft delete lab room

---

## TROUBLESHOOTING

### Issue: Buttons Don't Work

**Solution 1**: Clear browser cache
```
1. Press Ctrl + Shift + Delete
2. Select "All time"
3. Check "Cached images and files"
4. Click "Clear data"
5. Refresh page (Ctrl + F5)
```

**Solution 2**: Check browser console
```
1. Press F12
2. Click "Console" tab
3. Look for RED errors
4. Common errors:
   - "selectUserType is not defined" → Refresh page
   - "Failed to fetch" → Server not running
   - "Supabase is not defined" → Wait for CDN to load
```

**Solution 3**: Try different browser
- Chrome (recommended)
- Firefox
- Edge

### Issue: Server Won't Start

**Solution**:
```bash
# Check Python installed
py --version

# Install dependencies
pip install flask flask-cors supabase

# Start server
py unified_server.py
```

### Issue: Timetable Generation Fails

**Solution**:
```
1. Check all subjects have faculty assigned
2. Verify lab rooms are added
3. Ensure enough time slots (5 days × 6 periods = 30 slots)
4. System retries 5 times automatically
5. Check server terminal for error messages
```

### Issue: Login Fails

**Solution**:
```
1. Check credentials (case-sensitive):
   - Username: MIT Mysore
   - Password: mitm@1234
2. Clear localStorage:
   - Press F12
   - Go to Application → Local Storage
   - Clear all
3. Try again
```

---

## ADMIN SETTINGS FLOW

### How Settings Are Applied

1. **Admin Saves Settings**
   - Settings saved to `global_settings` table
   - Includes work days, periods, breaks

2. **Engine Loads Settings**
   - On initialization, loads from database
   - Uses settings for timetable generation

3. **Settings Used in Generation**
   - Work days → Timetable structure
   - Periods per day → Slot count
   - Break positions → Lab slot exclusions
   - OE constraints → Pre-filled in STEP 0

---

## CONSTRAINT DETAILS

### 1. Strict Weekly Hours
- Each subject placed exactly `weekly_hours` times
- Validated after generation
- Example: Subject with 3 hours → Placed exactly 3 times

### 2. Daily Diversity
- Same subject cannot appear twice on same day
- Tracked via `subject_day_tracker`
- Example: DBMS on Monday P1 → Cannot be on Monday P3

### 3. Lab Continuity
- Labs always in 2 consecutive periods
- Valid slots: P1-P2, P3-P4, P5-P6
- Never crosses tea break (after P2) or lunch break (after P4)

### 4. NSS/FREE → P6 Only
- NSS and FREE subjects only in last period
- Enforced in STEP 1 of generation

### 5. Global Faculty Conflict
- Faculty cannot teach two classes simultaneously
- Tracked via `master_occupancy` set
- Checks finalized timetables in database

### 6. Lab Room Clash Prevention
- Same lab room cannot be used by multiple classes at same time
- Tracked via `lab_room_occupancy` set
- Department-specific lab rooms

### 7. Open Elective Same-Slot
- OE subjects locked to SAME day+slot across ALL departments
- Admin locks in global-admin.htm
- Pre-filled in STEP 0 before any other placement

---

## GENERATION ALGORITHM

### STEP 0: Pre-fill Open Electives
- Load OE constraints from database
- Place OE subjects at locked day+slot
- Mark as `is_oe_locked=true`
- Add faculty to global occupancy

### STEP 1: Place NSS/FREE
- Find available P6 slots
- Place NSS/FREE subjects
- Add faculty to global occupancy

### STEP 2: Place Labs
- Get valid lab slots (excluding breaks)
- For each lab:
  - Find available 2-hour block
  - Check faculty conflicts
  - Get available lab room
  - Place lab in both slots
  - Add to global occupancy

### STEP 3: Place Theory Subjects
- For each theory subject:
  - Place `weekly_hours` times
  - Ensure no same subject twice per day
  - Check faculty conflicts
  - Add to global occupancy

### STEP 4: Validate Constraints
- Check all 7 constraints
- Return violations if any
- If valid, save to database

---

## SUPPORT

### Common Questions

**Q: Can I change work days?**
A: Yes, admin can configure in global-admin.htm

**Q: Can I have more than 6 periods?**
A: Yes, admin can set up to 10 periods per day

**Q: Can labs be in any slot?**
A: No, labs must be in 2-hour blocks and cannot cross breaks

**Q: Can I swap classes after generation?**
A: Yes, use Smart Swap in enhanced.htm (checks faculty conflicts)

**Q: Can I edit finalized timetables?**
A: No, finalized timetables are locked. Generate new one if needed.

**Q: How do Open Electives work?**
A: Admin locks OE to specific day+slot. All departments must have OE at same time.

---

## SYSTEM REQUIREMENTS

- Python 3.11+
- Flask, Flask-CORS, Supabase
- Modern web browser (Chrome, Firefox, Edge)
- Internet connection (for Supabase)
- Port 5000 available

---

## LICENSE

MIT License - Maharaja Institute of Technology, Mysore

---

**Last Updated**: 2024  
**Version**: 1.0 - Production Ready  
**Status**: ✅ ALL SYSTEMS OPERATIONAL
