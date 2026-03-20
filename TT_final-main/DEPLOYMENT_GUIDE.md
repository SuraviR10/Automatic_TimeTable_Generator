# MIT Mysore Timetable System - Deployment Guide

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection (for Supabase)
- Modern web browser (Chrome, Firefox, Edge)

---

## 🚀 Step-by-Step Deployment

### Step 1: Install Python Dependencies

```bash
cd TT_final-main
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed flask-3.0.0 flask-cors-4.0.0 supabase-2.3.0 ...
```

---

### Step 2: Setup Database

1. **Login to Supabase Dashboard**
   - URL: https://bkmzyhroignpjebfpqug.supabase.co

2. **Run Core Schema**
   ```sql
   -- Execute complete_database_setup.sql in SQL Editor
   ```

3. **Run Global Admin Schema**
   ```sql
   -- Execute global_admin_schema.sql in SQL Editor
   ```

4. **Verify Tables Created**
   - timetables
   - subjects
   - faculty
   - departments
   - global_settings
   - open_electives
   - users

---

### Step 3: Configure Global Settings

1. **Insert Default Settings**
   ```sql
   INSERT INTO global_settings (setting_key, setting_value) VALUES
   ('work_days', "['Tuesday','Wednesday','Thursday','Friday','Saturday']"),
   ('periods_per_day', '6'),
   ('tea_break_after_period', '2'),
   ('lunch_break_after_period', '4');
   ```

2. **Verify Settings**
   ```sql
   SELECT * FROM global_settings;
   ```

---

### Step 4: Start the Server

**Windows:**
```bash
START_SYSTEM.bat
```

**Linux/Mac:**
```bash
python unified_server.py
```

**Expected Output:**
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

### Step 5: Validate System

**Open new terminal and run:**
```bash
python validate_system.py
```

**Expected Output:**
```
✅ PASS - Server Health
✅ PASS - Timetable Generation
✅ PASS - Smart Swap
✅ PASS - Safe Slots

Total: 4/4 tests passed
🎉 All tests passed! System is ready.
```

---

### Step 6: Access Dashboard

1. **Open Browser**
   ```
   http://localhost:5000/dashboard.htm
   ```

2. **Login** (if authentication enabled)
   - Default credentials in users table

3. **Navigate to Timetable Generator**
   ```
   http://localhost:5000/timetable-new.htm
   ```

---

## 🎯 Usage Workflow

### Creating a Timetable

1. **Go to Timetable Generator** (`timetable-new.htm`)

2. **Select Parameters**
   - Department: CSE, ECE, MECH, etc.
   - Year: 1-4
   - Semester: 1-8
   - Academic Year: 2024-25

3. **Add Sections**
   - Click "Add Section"
   - Enter section name (A, B, C)

4. **Assign Faculty to Subjects**
   - Select subject from dropdown
   - Select faculty from dropdown
   - Click "Add Assignment"

5. **Generate Timetable**
   - Click "Generate Timetable"
   - Wait 2-5 seconds per section
   - View generated timetable

6. **Review and Edit**
   - Use Smart Swap to adjust slots
   - System highlights conflicts in red
   - System suggests safe slots in yellow

7. **Finalize and Save**
   - Click "Finalize & Save"
   - Timetable locked to database
   - Appears in Vault

---

### Using Smart Swap

1. **Open Enhanced View** (`enhanced.htm`)

2. **Enable Swap Mode**
   - Click "Enable Smart Swap"

3. **Select Two Cells**
   - Click first cell (source)
   - Click second cell (target)

4. **Review Validation**
   - ✅ Green border = Valid swap
   - ❌ Red border = Conflict detected
   - 💡 Yellow pulse = Suggested safe slot

5. **Confirm or Cancel**
   - Click "Confirm Swap" if valid
   - Click "Cancel" to try different slots

---

### Configuring Global Admin

1. **Go to Admin Panel** (`global-admin.htm`)

2. **Configure Work Week**
   - Check/uncheck days
   - Click "Save Work Days"

3. **Configure Time Slots**
   - Set period start/end times
   - Set break times
   - Click "Save Time Slots"

4. **Lock Open Electives**
   - Select OE subject
   - Select day and period
   - Click "Lock OE Slot"
   - All departments inherit this constraint

5. **Validate Lab Slots**
   - System shows valid lab slots
   - Red = Invalid (crosses break)
   - Green = Valid

---

## 🔒 Constraint Enforcement

### Automatic Validation

The system automatically enforces these constraints:

1. **Strict Weekly Hours**
   - Each subject gets EXACTLY specified hours
   - Generation fails if hours don't match

2. **Daily Diversity**
   - No subject appears twice on same day
   - Applies to theory and lab

3. **Lab Continuity**
   - Labs are 2 continuous periods
   - Never cross tea or lunch break
   - Valid slots: P1-P2, P3-P4, P5-P6

4. **Global Faculty Locking**
   - Faculty cannot be double-booked
   - Checked across ALL departments
   - Includes finalized timetables

5. **NSS/FREE Placement**
   - Only in Period 6 (last hour)
   - Never in P1-P5

---

## 🐛 Troubleshooting

### Issue: Server won't start

**Symptoms:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
pip install -r requirements.txt
```

---

### Issue: Database connection failed

**Symptoms:**
```
Error: Unable to connect to Supabase
```

**Solution:**
1. Check internet connection
2. Verify SUPABASE_URL and SUPABASE_KEY in unified_server.py
3. Test connection: `python -c "from supabase import create_client; print('OK')"`

---

### Issue: Timetable generation fails

**Symptoms:**
```
{"valid": false, "error": "Could not place lab CS503L"}
```

**Solution:**
1. Check if lab has 2 continuous hours available
2. Verify break times don't conflict with lab slots
3. Ensure faculty is not double-booked
4. Try different section or reduce subjects

---

### Issue: Smart swap shows false conflicts

**Symptoms:**
- Swap marked as invalid but no visible conflict

**Solution:**
1. Check if faculty is assigned in another department
2. Verify academic_year parameter matches
3. Check if timetable is finalized in database
4. Use "Get Safe Slots" to see faculty availability

---

### Issue: OE constraint not working

**Symptoms:**
- OE subjects not locked to same slot

**Solution:**
1. Verify open_electives table has entries
2. Check academic_year, year, semester match
3. Ensure locked_day and locked_time_slot are valid
4. Regenerate timetable after adding OE constraint

---

## 📊 Performance Optimization

### For Large Departments (10+ sections)

1. **Generate in Batches**
   - Generate 2-3 sections at a time
   - Finalize before generating next batch

2. **Use Database Indexes**
   ```sql
   CREATE INDEX idx_faculty_schedule ON timetables(faculty_name, day, time_slot, academic_year);
   CREATE INDEX idx_finalized ON timetables(is_finalized);
   ```

3. **Clear Old Timetables**
   ```sql
   DELETE FROM timetables WHERE academic_year < '2023-24' AND is_finalized = false;
   ```

---

## 🔐 Security Best Practices

1. **Change Default Credentials**
   ```sql
   UPDATE users SET password = 'new_secure_password' WHERE role = 'admin';
   ```

2. **Use Environment Variables**
   ```bash
   # Create .env file
   SUPABASE_URL=your_url
   SUPABASE_KEY=your_key
   ```

3. **Enable Row Level Security (RLS)**
   ```sql
   ALTER TABLE timetables ENABLE ROW LEVEL SECURITY;
   CREATE POLICY dept_isolation ON timetables FOR SELECT USING (department = current_user_dept());
   ```

---

## 📈 Monitoring

### Check System Health

```bash
curl http://localhost:5000/health
```

**Expected:**
```json
{"status": "ok", "message": "Unified Timetable Engine Running"}
```

### Monitor Logs

**Windows:**
- Check console output where START_SYSTEM.bat is running

**Linux:**
```bash
tail -f unified_server.log
```

---

## 🆘 Support Checklist

Before reporting an issue:

- [ ] Ran `pip install -r requirements.txt`
- [ ] Executed both SQL schema files
- [ ] Server starts without errors
- [ ] `validate_system.py` passes all tests
- [ ] Checked browser console for errors (F12)
- [ ] Verified database connection
- [ ] Reviewed this deployment guide

---

## ✅ Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database schema executed (both SQL files)
- [ ] Global settings configured
- [ ] Server starts successfully
- [ ] Validation tests pass
- [ ] Dashboard accessible
- [ ] Timetable generation works
- [ ] Smart swap functional
- [ ] Faculty conflict detection working
- [ ] OE constraints enforced

---

## 🎓 Training Resources

### For HODs
- How to generate timetables
- How to assign faculty
- How to use smart swap
- How to finalize timetables

### For Faculty
- How to view personal timetable
- How to download PDF
- How to check schedule conflicts

### For Admin
- How to configure work week
- How to set break times
- How to lock OE slots
- How to manage users

---

## 📞 Contact

For technical support:
- Check README.md
- Review GLOBAL_ADMIN_IMPLEMENTATION.md
- Run validate_system.py
- Check server logs

---

**Version**: 3.0 - Unified Engine
**Last Updated**: 2024
**Status**: Production Ready ✅
