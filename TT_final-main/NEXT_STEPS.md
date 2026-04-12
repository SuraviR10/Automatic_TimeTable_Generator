# NEXT STEPS - Complete Setup Guide

## Current Status
- Python: INSTALLED
- Dependencies: INSTALLED
- Supabase: SETUP COMPLETE

---

## Step 1: Configure Database Schema

### 1.1 Login to Supabase
Go to: https://bkmzyhroignpjebfpqug.supabase.co

### 1.2 Run Core Schema
1. Click "SQL Editor" in left sidebar
2. Click "New Query"
3. Copy and paste content from `complete_database_setup.sql`
4. Click "Run"

Expected tables created:
- departments
- subjects
- faculty
- timetables
- faculty_assignments

### 1.3 Run Global Admin Schema
1. Click "New Query" again
2. Copy and paste content from `global_admin_schema.sql`
3. Click "Run"

Expected tables created:
- global_settings
- open_electives
- users

### 1.4 Insert Default Settings
Run this SQL:
```sql
INSERT INTO global_settings (setting_key, setting_value) VALUES
('work_days', '["Tuesday","Wednesday","Thursday","Friday","Saturday"]'),
('periods_per_day', '6'),
('tea_break_after_period', '2'),
('lunch_break_after_period', '4');
```

### 1.5 Verify Tables
Run this SQL:
```sql
SELECT * FROM global_settings;
```

Expected output: 4 rows with settings

---

## Step 2: Add Sample Data

### 2.1 Add Department
```sql
INSERT INTO departments (name, code) VALUES
('Computer Science', 'CSE'),
('Electronics', 'ECE'),
('Mechanical', 'MECH');
```

### 2.2 Add Subjects
```sql
INSERT INTO subjects (department, sub_code, name, type, weekly_hours, classes_per_week) VALUES
('CSE', 'CS501', 'Artificial Intelligence', 'theory', 3, 3),
('CSE', 'CS502', 'Machine Learning', 'theory', 3, 3),
('CSE', 'CS503L', 'AI Lab', 'lab', 2, 1),
('CSE', 'CS504', 'Data Science', 'theory', 3, 3),
('CSE', 'NSS', 'NSS', 'free', 1, 1);
```

### 2.3 Add Faculty
```sql
INSERT INTO faculty (department, name, email) VALUES
('CSE', 'Dr. Smith', 'smith@mit.edu'),
('CSE', 'Dr. Jones', 'jones@mit.edu'),
('CSE', 'Dr. Brown', 'brown@mit.edu');
```

---

## Step 3: Start the Server

### 3.1 Open Terminal
Navigate to project folder:
```bash
cd c:\Users\surav\Downloads\TT_final-main\TT_final-main
```

### 3.2 Start Server
```bash
py unified_server.py
```

Expected output:
```
🚀 MIT Mysore Unified Timetable Engine
✅ All constraints enforced
✅ Global faculty conflict detection
✅ Smart swap with suggestions
✅ OE Mega-Constraint support

Server: http://localhost:5000
 * Running on http://0.0.0.0:5000
```

---

## Step 4: Access Dashboard

### 4.1 Open Browser
Go to: http://localhost:5000/dashboard.htm

### 4.2 Navigate to Generator
Click "Generate Timetable" or go to:
http://localhost:5000/timetable-new.htm

---

## Step 5: Generate First Timetable

### 5.1 Select Parameters
- Department: CSE
- Year: 3
- Semester: 5
- Academic Year: 2024-25

### 5.2 Add Section
- Click "Add Section"
- Enter: A

### 5.3 Assign Faculty
For each subject, select faculty:
- CS501 (AI) → Dr. Smith
- CS502 (ML) → Dr. Jones
- CS503L (AI Lab) → Dr. Smith
- CS504 (Data Science) → Dr. Brown
- NSS → Kiran Kumar (or any faculty)

### 5.4 Generate
- Click "Generate Timetable"
- Wait 2-5 seconds
- View generated timetable

---

## Step 6: Verify Constraints

Check the generated timetable:

### Constraint 1: Strict Weekly Hours
- CS501: Should appear exactly 3 times
- CS502: Should appear exactly 3 times
- CS503L: Should appear exactly 2 times (continuous)
- CS504: Should appear exactly 3 times
- NSS: Should appear exactly 1 time

### Constraint 2: Daily Diversity
- No subject should appear twice on same day
- Example: If CS501 is on Tuesday P1, it should NOT be on Tuesday P2/P3/P4/P5/P6

### Constraint 3: Lab Continuity
- CS503L should be in 2 continuous periods
- Valid slots: P1-P2, P3-P4, P5-P6
- Should NOT cross breaks (after P2 or P4)

### Constraint 4: NSS Placement
- NSS should ONLY be in Period 6
- Never in P1, P2, P3, P4, or P5

### Constraint 5: Faculty Conflicts
- Dr. Smith should not be in two places at same time
- Check: If Dr. Smith teaches CS501 on Tuesday P1, he should NOT teach CS503L on Tuesday P1

---

## Step 7: Test Smart Swap

### 7.1 Open Enhanced View
Go to: http://localhost:5000/enhanced.htm

### 7.2 Enable Smart Swap
Click "Enable Smart Swap" button

### 7.3 Swap Two Cells
1. Click on any cell (e.g., Tuesday P1)
2. Click on another cell (e.g., Wednesday P2)
3. System will show:
   - Green border = Valid swap
   - Red border = Conflict detected
   - Yellow pulse = Suggested safe slot

### 7.4 Confirm or Cancel
- If green: Click "Confirm Swap"
- If red: Click "Cancel" and try different cells

---

## Step 8: Finalize Timetable

### 8.1 Review Timetable
Check all constraints are satisfied

### 8.2 Click Finalize
Click "Finalize & Save" button

### 8.3 Verify in Vault
Go to: http://localhost:5000/vault.htm
Your timetable should appear in the list

---

## Troubleshooting

### Issue: Server won't start
**Solution**:
```bash
py -m pip install -r requirements.txt
```

### Issue: Database connection error
**Solution**:
1. Check internet connection
2. Verify Supabase URL and key in `unified_server.py`
3. Ensure database tables are created

### Issue: Timetable generation fails
**Solution**:
1. Check if subjects have correct weekly_hours
2. Verify faculty are assigned
3. Ensure academic year is selected
4. Try with fewer subjects first

### Issue: Constraints violated
**Solution**:
1. Check global_settings table has correct values
2. Verify break times don't conflict with lab slots
3. Ensure NSS is marked as type='free'

---

## Quick Test Commands

### Test Server Health
```bash
curl http://localhost:5000/health
```

Expected: `{"status":"ok","message":"Unified Timetable Engine Running"}`

### Test Constraint Logic
```bash
py test_simple.py
```

Expected: All 5 constraints should PASS

---

## Configuration Options

### Change Work Days
1. Go to: http://localhost:5000/global-admin.htm
2. Check/uncheck days
3. Click "Save Work Days"

### Change Break Times
1. Go to: http://localhost:5000/global-admin.htm
2. Modify tea break and lunch break times
3. Click "Save Time Slots"

### Lock Open Electives
1. Go to: http://localhost:5000/global-admin.htm
2. Select OE subject
3. Select day and period
4. Click "Lock OE Slot"

---

## Success Indicators

✅ Server starts without errors
✅ Dashboard loads in browser
✅ Can select department and academic year
✅ Can add sections and assign faculty
✅ Timetable generates successfully
✅ All 5 constraints are satisfied
✅ Smart swap shows green/red correctly
✅ Can finalize and save timetable
✅ Timetable appears in vault

---

## Next Actions

1. **Complete database setup** (Step 1)
2. **Add sample data** (Step 2)
3. **Start server** (Step 3)
4. **Generate first timetable** (Step 5)
5. **Verify all constraints** (Step 6)
6. **Test smart swap** (Step 7)
7. **Finalize timetable** (Step 8)

---

## Support

If you encounter issues:
1. Check MANUAL_VERIFICATION.md
2. Review DEPLOYMENT_GUIDE.md
3. Run: `py test_simple.py`
4. Check server console for errors
5. Verify database tables exist

---

**System Status**: Ready for Use ✅
**Next Step**: Complete database setup (Step 1)
