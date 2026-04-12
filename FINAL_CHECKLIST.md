# ✅ FINAL VERIFICATION CHECKLIST

## Before Starting

### 1. Database Setup
- [ ] Open Supabase: https://supabase.com
- [ ] Go to SQL Editor
- [ ] Run `database_setup.sql` completely
- [ ] Verify all tables created (subjects, faculty, lab_rooms, timetables, global_settings, open_electives, admin_users, users)

### 2. Python Environment
- [ ] Run: `py --version` (should show 3.11+)
- [ ] Run: `pip install -r requirements.txt`
- [ ] All packages installed without errors

### 3. Start Server
- [ ] Run: `START.bat` or `py unified_server.py`
- [ ] Server starts at http://localhost:5000
- [ ] No errors in console

## Testing Flow

### Admin Setup
- [ ] Open http://localhost:5000
- [ ] Click "Admin Login"
- [ ] Login: admin / Admin@1234
- [ ] Set working days (default: Tue-Sat)
- [ ] Set periods per day: 6
- [ ] Set tea break after period: 2
- [ ] Set lunch break after period: 4
- [ ] Click "Save Global Configuration"
- [ ] Add Open Elective: OE601, Machine Learning, Thursday, Period 3
- [ ] Click "Lock OE Slot"

### Department Setup (ISE Example)
- [ ] Logout from admin
- [ ] Click "Department Login"
- [ ] Register: ISE department with password
- [ ] Login with ISE credentials
- [ ] Dashboard opens

#### Lab Management
- [ ] Click "Lab Management"
- [ ] Add lab: Room Code = ISE-LAB-01, Lab Name = Database Lab, Capacity = 30
- [ ] Add lab: Room Code = ISE-LAB-02, Lab Name = Networks Lab, Capacity = 30
- [ ] Add lab: Room Code = ISE-LAB-03, Lab Name = Programming Lab, Capacity = 30
- [ ] Verify all 3 labs appear in table

#### Subject Management
- [ ] Click "Subject Database"
- [ ] Select: Academic Year = 2024-25, Year = 3, Semester = 5
- [ ] Add subject: IS501, DBMS, 4 credits, Theory, 3 hours/week
- [ ] Add subject: IS502, DBMS Lab, 2 credits, Lab, 2 hours/week
- [ ] Add subject: IS503, OS, 4 credits, Theory, 3 hours/week
- [ ] Add subject: IS504, OS Lab, 2 credits, Lab, 2 hours/week
- [ ] Add subject: IS505, CN, 4 credits, Theory, 3 hours/week
- [ ] Add subject: IS506, CN Lab, 2 credits, Lab, 2 hours/week
- [ ] Add subject: OE601, Machine Learning, 3 credits, Theory, 3 hours/week, CHECK "Open Elective"
- [ ] Add subject: NSS, NSS, 1 credit, Free, 1 hour/week
- [ ] Verify all 8 subjects appear

#### Faculty Management
- [ ] Click "Faculty Core"
- [ ] Add faculty: Dr. Smith, Initials: DS, Department: ISE
- [ ] Add faculty: Dr. Jones, Initials: DJ, Department: ISE
- [ ] Add faculty: Dr. Brown, Initials: DB, Department: ISE
- [ ] Add faculty: Dr. Wilson, Initials: DW, Department: ISE
- [ ] Verify all 4 faculty appear

#### Timetable Generation
- [ ] Click "Timetable Generator"
- [ ] Academic Year: 2024-25
- [ ] Year: 3
- [ ] Semester: 5
- [ ] Number of Sections: 2
- [ ] Click "Load Subjects"
- [ ] Verify all 8 subjects loaded
- [ ] Click "Assign Faculty"
- [ ] Assign faculty to each subject for Section A and Section B
- [ ] Click "Generate Timetable"
- [ ] Wait for generation (may take 10-30 seconds with retry logic)
- [ ] Success message appears
- [ ] Redirects to enhanced.htm

#### Verification
- [ ] Timetable displays for Section A
- [ ] Click "Next Section" → Section B displays
- [ ] Verify OE601 (Machine Learning) is at Thursday P3 for BOTH sections
- [ ] Verify all labs are in 2 consecutive periods
- [ ] Verify no lab crosses tea break (P2-P3) or lunch break (P4-P5)
- [ ] Verify NSS is in P6 only
- [ ] Verify no subject appears twice on same day
- [ ] Click "Finalize & Save"
- [ ] Success message appears

## Constraint Verification

### 1. Weekly Hours
- [ ] Count DBMS appearances in timetable = 3 (matches weekly_hours)
- [ ] Count OS appearances = 3
- [ ] Count CN appearances = 3
- [ ] Count each lab = 1 (but occupies 2 periods)

### 2. Daily Diversity
- [ ] Check Monday: No subject appears twice
- [ ] Check Tuesday: No subject appears twice
- [ ] Check all days: No duplicates

### 3. Lab Continuity
- [ ] DBMS Lab: 2 consecutive periods (e.g., P1-P2 or P3-P4 or P5-P6)
- [ ] OS Lab: 2 consecutive periods
- [ ] CN Lab: 2 consecutive periods
- [ ] No lab at P2-P3 (crosses tea break)
- [ ] No lab at P4-P5 (crosses lunch break)

### 4. NSS/FREE → P6
- [ ] NSS appears only in P6
- [ ] NSS not in P1, P2, P3, P4, or P5

### 5. Faculty Conflict
- [ ] No faculty teaching two classes at same time
- [ ] Check Section A Monday P1 faculty ≠ Section B Monday P1 faculty (if same faculty assigned)

### 6. Lab Room Clash
- [ ] Section A Monday P1-P2: Uses ISE-LAB-01
- [ ] Section B Monday P1-P2: Uses ISE-LAB-02 or ISE-LAB-03 (NOT ISE-LAB-01)
- [ ] No two sections use same lab at same time

### 7. Open Elective Same-Slot
- [ ] Section A: OE601 at Thursday P3
- [ ] Section B: OE601 at Thursday P3
- [ ] Both sections have OE at SAME time

## Final Tests

### PDF Export
- [ ] Click "Export PDF"
- [ ] PDF downloads with all sections
- [ ] PDF shows correct schedule

### Smart Swap
- [ ] Click "Smart Swap"
- [ ] Click two theory classes
- [ ] System validates faculty conflicts
- [ ] Swap completes or shows conflict message

### Vault
- [ ] Click "Timetable Vault" from dashboard
- [ ] Finalized timetable appears
- [ ] Click "View" → Opens in enhanced.htm

## Success Criteria

✅ All checkboxes above are checked
✅ No errors in browser console (F12)
✅ No errors in server console
✅ All 7 constraints verified
✅ Timetable generated successfully
✅ Finalization completed

## If Any Issues

1. Check server console for errors
2. Check browser console (F12) for errors
3. Verify database tables exist in Supabase
4. Verify Supabase URL and key are correct
5. Re-run `database_setup.sql` if tables missing
6. Restart server: Ctrl+C then `py unified_server.py`

## System Status

- [ ] All tests passed
- [ ] System ready for production use

**Date Tested**: _______________
**Tested By**: _______________
**Result**: ✅ PASS / ❌ FAIL
