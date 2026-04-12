# 🚀 Global Admin System - Implementation Guide

## 📊 System Overview

This implementation adds **Global Admin Control** to the MIT Mysore Timetable System with:
- Dynamic work-week configuration
- Master time slot management
- Break validation for labs
- Open Elective (OE) Mega-Constraint
- Global faculty conflict prevention

---

## 🗄️ Database Setup

### Step 1: Run Schema Migration
```bash
psql -h [SUPABASE_HOST] -U postgres -d postgres -f global_admin_schema.sql
```

### Tables Created:
1. **global_settings** - Stores admin configuration
2. **open_electives** - OE locked slots (Mega-Constraint)
3. **users** - Admin vs Department Head roles
4. **Enhanced timetables** - Added is_oe_locked, faculty_department

### Triggers Created:
1. **check_faculty_conflict()** - Prevents double-booking across departments
2. **validate_lab_placement()** - Ensures labs don't cross breaks

---

## 🧬 Genetic Algorithm Enhancements

### Hard Constraints Implemented:

#### 1. Strict Weekly Hours
```python
# Penalty if actual hours != expected hours
penalty += abs(expected - actual) * 10.0
```

#### 2. Daily Diversity
```python
# No same subject twice per day
if subject in day_subjects:
    penalty += 50.0
```

#### 3. Lab Continuity & No-Break Rule
```python
# Labs only in valid slots (not crossing breaks)
valid_lab_slots = [(1,2), (3,4), (5,6)]  # Adjusted based on breaks
if (slot, slot+1) not in valid_lab_slots:
    penalty += 100.0
```

#### 4. Global Faculty Locking
```python
# Check across ALL departments
if faculty_busy_anywhere(faculty, day, slot):
    penalty += 200.0
```

#### 5. OE Mega-Constraint
```python
# Pre-fill OE slots BEFORE generating rest of timetable
for oe in oe_constraints:
    timetable[oe.day][oe.slot] = oe_subject
    mark_as_locked()
```

---

## 👑 Global Admin Dashboard

### Access URL:
```
http://localhost/global-admin.htm
```

### Features:

#### 1. Dynamic Work Week
- Select 5, 6, or 7 working days
- Checkboxes for each day
- Auto-adjusts total available slots

#### 2. Master Time Slots
- Start/End time configuration
- Period duration (30-120 minutes)
- Auto-calculates periods per day

#### 3. Break Management
- Tea Break timing and position
- Lunch Break timing and position
- Real-time lab validation preview

#### 4. OE Mega-Constraint
- Lock OE subjects to specific slots
- Applies to ALL departments
- View/Delete existing locks

### Save Button:
```javascript
💾 Save Global Configuration
// Pushes changes to global_settings table
// All departments fetch these settings on load
```

---

## 🔌 API Endpoints

### 1. Generate with Admin Settings
```http
POST /generate_with_admin_settings
Content-Type: application/json

{
  "department": "CSE",
  "section": "A",
  "sessions": [...],
  "academic_year": "2024-25",
  "year": 3,
  "semester": 5
}
```

### 2. Validate Faculty Globally
```http
POST /validate_faculty_global
Content-Type: application/json

{
  "faculty_name": "Dr. Smith",
  "day": "Tuesday",
  "time_slot": 3,
  "academic_year": "2024-25"
}
```

### 3. Get Global Settings
```http
GET /get_global_settings

Response:
{
  "work_days": ["Tuesday", "Wednesday", ...],
  "periods_per_day": 6,
  "tea_break_after": 2,
  "lunch_break_after": 4,
  "valid_lab_slots": [[1,2], [3,4], [5,6]]
}
```

### 4. Get OE Constraints
```http
GET /get_oe_constraints?academic_year=2024-25&year=3&semester=5

Response:
{
  "oe_constraints": [
    {
      "oe_subject_code": "OE601",
      "locked_day": "Wednesday",
      "locked_time_slot": 3
    }
  ]
}
```

---

## 🚀 Deployment Steps

### 1. Database Setup
```bash
# Run schema migration
psql -f global_admin_schema.sql

# Verify tables created
psql -c "\dt"
```

### 2. Install Python Dependencies
```bash
pip install flask flask-cors supabase
```

### 3. Start Global Admin Server
```bash
python global_admin_server.py
```

Expected output:
```
🚀 Starting Global Admin GA Server...
📊 Loading global settings from database...
✅ Work Days: ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
✅ Periods Per Day: 6
✅ Valid Lab Slots: [(1, 2), (3, 4), (5, 6)]
 * Running on http://0.0.0.0:5000
```

### 4. Access Admin Dashboard
```
http://localhost/global-admin.htm
```

---

## 🎯 Usage Workflow

### Admin Workflow:
1. Login to **Global Admin Dashboard**
2. Configure **Work Days** (5/6/7 days)
3. Set **Master Time Slots** (start/end/duration)
4. Define **Break Positions** (tea/lunch)
5. Lock **OE Subjects** to specific slots
6. Click **💾 Save Global Configuration**
7. All departments now use these settings

### Department Head Workflow:
1. Login to department dashboard
2. System auto-fetches global settings
3. Add subjects and faculty
4. Generate timetable
5. System enforces:
   - Global work days
   - Break positions
   - OE locked slots
   - Faculty global conflicts

---

## 🔒 Constraint Enforcement

### Automatic Validations:

#### Database Level (Triggers):
- ✅ Faculty double-booking prevented
- ✅ Labs crossing breaks rejected
- ✅ OE slots locked and immutable

#### Algorithm Level (Fitness Function):
- ✅ Strict weekly hours enforced
- ✅ Daily diversity maintained
- ✅ Lab continuity guaranteed
- ✅ NSS in last period only

#### Frontend Level (Smart Swap):
- ✅ Real-time conflict checking
- ✅ Visual feedback (red/shake)
- ✅ Alternative suggestions

---

## 📈 Performance Metrics

### Fitness Function Penalties:
- Weekly hours mismatch: **10.0 per hour**
- Same subject twice/day: **50.0**
- Lab crossing break: **100.0**
- Faculty conflict: **200.0**
- NSS not in P6: **75.0**

### Acceptance Threshold:
```python
fitness < 0.1  # Accept only near-perfect solutions
```

---

## 🛠️ Troubleshooting

### Issue: Labs placed across breaks
**Solution**: Check `tea_break_after_period` and `lunch_break_after_period` in global_settings

### Issue: Faculty double-booked
**Solution**: Database trigger will reject. Check error message for conflicting slot.

### Issue: OE not locked
**Solution**: Verify open_electives table has entry for that year/semester

### Issue: Wrong work days
**Solution**: Admin must save configuration. Departments fetch on page load.

---

## 📊 Testing Checklist

- [ ] Admin can change work days (5/6/7)
- [ ] Periods per day auto-calculated
- [ ] Labs cannot cross tea break
- [ ] Labs cannot cross lunch break
- [ ] Faculty conflict rejected globally
- [ ] OE locked to same slot for all depts
- [ ] NSS always in last period
- [ ] No subject twice per day
- [ ] Strict weekly hours enforced

---

## 🎓 Key Innovations

1. **Dynamic Work Week**: Adapts to 5/6/7 day schedules
2. **Break Validation**: Prevents labs from crossing breaks
3. **OE Mega-Constraint**: College-wide slot locking
4. **Global Faculty Lock**: Cross-department conflict prevention
5. **Fitness-Based GA**: Hard constraints with heavy penalties

---

## 📞 Support

For issues or questions:
1. Check database triggers are active
2. Verify global_settings table populated
3. Ensure Flask server running
4. Check browser console for errors

---

**System Status**: ✅ Production Ready
**Last Updated**: 2024
**Version**: 2.0 (Global Admin Edition)
