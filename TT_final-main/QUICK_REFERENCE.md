# MIT Mysore Timetable System - Quick Reference

## 🚀 Getting Started (30 seconds)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Start
START_SYSTEM.bat

# 3. Open
http://localhost:5000/dashboard.htm
```

---

## 📋 Common Operations

### Generate Timetable
1. Go to `timetable-new.htm`
2. Select: Department, Year, Semester, Academic Year
3. Add Section → Assign Faculty → Generate
4. Wait 2-5 seconds → View timetable

### Smart Swap
1. Open `enhanced.htm`
2. Click "Enable Smart Swap"
3. Click cell 1 → Click cell 2
4. 🟢 Green = Valid | 🔴 Red = Conflict
5. Confirm or Cancel

### View Faculty Timetable
1. Go to `faculty-timetable.htm`
2. Select Faculty Name
3. View schedule → Download PDF

### Configure Admin Settings
1. Go to `global-admin.htm`
2. Set Work Days → Set Breaks → Lock OE
3. Save Settings

---

## 🔒 5 Hard Constraints (Auto-Enforced)

| # | Constraint | Rule |
|---|------------|------|
| 1 | **Strict Weekly Hours** | Exact hours per subject |
| 2 | **Daily Diversity** | No subject twice per day |
| 3 | **Lab Continuity** | 2 continuous periods, no breaks |
| 4 | **Global Faculty Lock** | No double-booking across college |
| 5 | **NSS Placement** | Only in Period 6 |

---

## 🎨 Visual Indicators

| Color | Meaning |
|-------|---------|
| 🟢 Green | Valid swap / Safe slot |
| 🔴 Red | Conflict detected |
| 🟡 Yellow | Suggested safe slot |
| ⚪ White | Empty slot |

---

## 🐛 Quick Fixes

| Problem | Solution |
|---------|----------|
| Server won't start | `pip install -r requirements.txt` |
| Database error | Check internet connection |
| Generation fails | Reduce subjects or check constraints |
| Swap invalid | Check faculty availability |

---

## 📞 Help

- **Full Docs**: README.md
- **Deployment**: DEPLOYMENT_GUIDE.md
- **Admin Guide**: GLOBAL_ADMIN_IMPLEMENTATION.md
- **System Summary**: FINAL_SUMMARY.md
- **Validate**: `python validate_system.py`

---

## 🎓 MIT Mysore Schedule

- **Days**: Tue-Sat (5 days)
- **Periods**: 6 per day (09:00-16:00)
- **Tea Break**: After P2 (11:00-11:15)
- **Lunch Break**: After P4 (13:15-14:00)
- **Labs**: 2 continuous hours

---

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `unified_server.py` | Main server |
| `START_SYSTEM.bat` | Start script |
| `validate_system.py` | Test system |
| `dashboard.htm` | Main dashboard |
| `timetable-new.htm` | Generator |
| `enhanced.htm` | Smart swap |

---

## ✅ Pre-Flight Checklist

Before generating timetable:

- [ ] Server running (`START_SYSTEM.bat`)
- [ ] Database connected (check health)
- [ ] Subjects added to database
- [ ] Faculty added to database
- [ ] Academic year selected
- [ ] Faculty assigned to subjects

---

## 🎯 Workflow

```
1. Add Subjects (subject.htm)
   ↓
2. Add Faculty (faculty.htm)
   ↓
3. Generate Timetable (timetable-new.htm)
   ↓
4. Review & Swap (enhanced.htm)
   ↓
5. Finalize & Save
   ↓
6. View in Vault (vault.htm)
```

---

## 📊 API Quick Reference

```bash
# Health Check
curl http://localhost:5000/health

# Generate Timetable
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"department":"CSE","year":3,"semester":5,...}'

# Validate Swap
curl -X POST http://localhost:5000/validate_swap \
  -H "Content-Type: application/json" \
  -d '{"academic_year":"2024-25","swap_data":{...}}'

# Get Safe Slots
curl -X POST http://localhost:5000/get_safe_slots \
  -H "Content-Type: application/json" \
  -d '{"faculty_name":"Dr. Smith","academic_year":"2024-25"}'
```

---

## 🚨 Emergency Commands

```bash
# Restart Server
Ctrl+C → START_SYSTEM.bat

# Validate System
python validate_system.py

# Check Logs
# See console where START_SYSTEM.bat is running

# Clear Cache
# Close browser → Clear cache → Reopen
```

---

## 💡 Pro Tips

1. **Generate in batches**: 2-3 sections at a time
2. **Finalize early**: Lock timetables to prevent conflicts
3. **Use smart swap**: Let system suggest safe slots
4. **Check faculty load**: Use faculty timetable view
5. **Lock OE first**: Set OE constraints before generating

---

## 📈 Performance

- **Generation**: 2-5s per section
- **Validation**: <100ms
- **Conflict Check**: <50ms
- **Swap Suggestions**: <200ms

---

## 🎉 Success Indicators

✅ Server shows: "Unified Timetable Engine Running"
✅ Dashboard loads without errors
✅ Timetable generates successfully
✅ Smart swap shows green/red correctly
✅ Faculty conflicts detected
✅ NSS appears only in P6
✅ Labs in continuous slots
✅ No subject repeated on same day

---

**Version**: 3.0 - Unified Engine
**Status**: Production Ready ✅
**Support**: See README.md
