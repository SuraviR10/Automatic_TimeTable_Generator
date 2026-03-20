"""
Comprehensive Constraint Validation Test
Tests all 5 hard constraints with detailed verification
"""

def test_all_constraints():
    """Test all 5 hard constraints"""
    
    print("=" * 70)
    print("COMPREHENSIVE CONSTRAINT VALIDATION TEST")
    print("=" * 70)
    
    # Sample timetable data
    timetable = {
        'Tuesday': {
            1: {'subject_code': 'CS501', 'faculty_name': 'Dr. Smith', 'type': 'theory'},
            2: {'subject_code': 'CS502', 'faculty_name': 'Dr. Jones', 'type': 'theory'},
            3: {'subject_code': 'CS503L', 'faculty_name': 'Dr. Smith', 'type': 'lab'},
            4: {'subject_code': 'CS503L', 'faculty_name': 'Dr. Smith', 'type': 'lab'},
            5: {'subject_code': 'CS504', 'faculty_name': 'Dr. Brown', 'type': 'theory'},
            6: {'subject_code': 'NSS', 'faculty_name': 'N/A', 'type': 'free'}
        },
        'Wednesday': {
            1: {'subject_code': 'CS501', 'faculty_name': 'Dr. Smith', 'type': 'theory'},
            2: {'subject_code': 'CS502', 'faculty_name': 'Dr. Jones', 'type': 'theory'},
            3: {'subject_code': 'CS504', 'faculty_name': 'Dr. Brown', 'type': 'theory'},
            4: None,
            5: None,
            6: None
        },
        'Thursday': {
            1: {'subject_code': 'CS501', 'faculty_name': 'Dr. Smith', 'type': 'theory'},
            2: {'subject_code': 'CS502', 'faculty_name': 'Dr. Jones', 'type': 'theory'},
            3: {'subject_code': 'CS504', 'faculty_name': 'Dr. Brown', 'type': 'theory'},
            4: None,
            5: None,
            6: None
        },
        'Friday': {
            1: None,
            2: None,
            3: None,
            4: None,
            5: None,
            6: None
        },
        'Saturday': {
            1: None,
            2: None,
            3: None,
            4: None,
            5: None,
            6: None
        }
    }
    
    sessions = [
        {'subject_code': 'CS501', 'weekly_hours': 3},
        {'subject_code': 'CS502', 'weekly_hours': 3},
        {'subject_code': 'CS503L', 'weekly_hours': 2, 'type': 'lab'},
        {'subject_code': 'CS504', 'weekly_hours': 3},
        {'subject_code': 'NSS', 'weekly_hours': 1, 'type': 'free'}
    ]
    
    work_days = ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    periods_per_day = 6
    tea_break_after = 2
    lunch_break_after = 4
    
    violations = []
    
    # CONSTRAINT 1: Strict Weekly Hours
    print("\n1️⃣  Testing CONSTRAINT 1: Strict Weekly Hours")
    subject_hours = {}
    for day in work_days:
        for slot in range(1, periods_per_day + 1):
            entry = timetable[day].get(slot)
            if entry:
                code = entry['subject_code']
                subject_hours[code] = subject_hours.get(code, 0) + 1
    
    constraint1_pass = True
    for session in sessions:
        expected = session['weekly_hours']
        actual = subject_hours.get(session['subject_code'], 0)
        if actual != expected:
            violations.append(f"   ❌ {session['subject_code']}: Expected {expected} hours, got {actual}")
            constraint1_pass = False
        else:
            print(f"   ✅ {session['subject_code']}: {actual}/{expected} hours")
    
    if constraint1_pass:
        print("   ✅ CONSTRAINT 1 PASSED: All subjects have exact weekly hours")
    else:
        print("   ❌ CONSTRAINT 1 FAILED")
    
    # CONSTRAINT 2: No Same Subject Twice Per Day
    print("\n2️⃣  Testing CONSTRAINT 2: Daily Diversity (No same subject twice per day)")
    constraint2_pass = True
    for day in work_days:
        day_subjects = []
        for slot in range(1, periods_per_day + 1):
            entry = timetable[day].get(slot)
            if entry and entry['subject_code'] not in ['FREE', 'NSS']:
                if entry['subject_code'] in day_subjects:
                    violations.append(f"   ❌ {entry['subject_code']} repeated on {day}")
                    constraint2_pass = False
                day_subjects.append(entry['subject_code'])
        
        if day_subjects:
            print(f"   ✅ {day}: {', '.join(set(day_subjects))} (no duplicates)")
    
    if constraint2_pass:
        print("   ✅ CONSTRAINT 2 PASSED: No subject repeated on same day")
    else:
        print("   ❌ CONSTRAINT 2 FAILED")
    
    # CONSTRAINT 3: Lab Continuity (2 continuous periods, no breaks)
    print("\n3️⃣  Testing CONSTRAINT 3: Lab Continuity (2 continuous, no breaks)")
    valid_lab_slots = []
    for i in range(1, periods_per_day):
        if i <= tea_break_after < i + 1:
            continue
        if i <= lunch_break_after < i + 1:
            continue
        valid_lab_slots.append((i, i + 1))
    
    print(f"   Valid lab slots: {valid_lab_slots}")
    
    constraint3_pass = True
    for day in work_days:
        for slot in range(1, periods_per_day):
            entry = timetable[day].get(slot)
            if entry and entry.get('type') == 'lab':
                if (slot, slot + 1) not in valid_lab_slots:
                    violations.append(f"   ❌ Lab {entry['subject_code']} at invalid slot {day} P{slot}")
                    constraint3_pass = False
                else:
                    print(f"   ✅ Lab {entry['subject_code']} at {day} P{slot}-P{slot+1} (valid)")
    
    if constraint3_pass:
        print("   ✅ CONSTRAINT 3 PASSED: All labs in valid continuous slots")
    else:
        print("   ❌ CONSTRAINT 3 FAILED")
    
    # CONSTRAINT 4: NSS/FREE Only in Period 6
    print("\n4️⃣  Testing CONSTRAINT 4: NSS/FREE Only in Period 6")
    constraint4_pass = True
    for day in work_days:
        for slot in range(1, periods_per_day):
            entry = timetable[day].get(slot)
            if entry and entry['subject_code'] in ['NSS', 'FREE']:
                violations.append(f"   ❌ NSS/FREE found in P{slot} on {day}, must be in P{periods_per_day}")
                constraint4_pass = False
        
        # Check P6
        entry = timetable[day].get(periods_per_day)
        if entry and entry['subject_code'] in ['NSS', 'FREE']:
            print(f"   ✅ {entry['subject_code']} correctly placed in {day} P{periods_per_day}")
    
    if constraint4_pass:
        print("   ✅ CONSTRAINT 4 PASSED: NSS/FREE only in Period 6")
    else:
        print("   ❌ CONSTRAINT 4 FAILED")
    
    # CONSTRAINT 5: No Faculty Conflicts
    print("\n5️⃣  Testing CONSTRAINT 5: No Faculty Conflicts")
    faculty_schedule = {}
    constraint5_pass = True
    for day in work_days:
        for slot in range(1, periods_per_day + 1):
            entry = timetable[day].get(slot)
            if entry and entry['faculty_name'] != 'N/A':
                key = f"{entry['faculty_name']}-{day}-{slot}"
                if key in faculty_schedule:
                    violations.append(f"   ❌ Faculty {entry['faculty_name']} conflict on {day} P{slot}")
                    constraint5_pass = False
                faculty_schedule[key] = True
    
    # Count faculty assignments
    faculty_counts = {}
    for day in work_days:
        for slot in range(1, periods_per_day + 1):
            entry = timetable[day].get(slot)
            if entry and entry['faculty_name'] != 'N/A':
                faculty_counts[entry['faculty_name']] = faculty_counts.get(entry['faculty_name'], 0) + 1
    
    for faculty, count in faculty_counts.items():
        print(f"   ✅ {faculty}: {count} periods (no conflicts)")
    
    if constraint5_pass:
        print("   ✅ CONSTRAINT 5 PASSED: No faculty conflicts detected")
    else:
        print("   ❌ CONSTRAINT 5 FAILED")
    
    # SUMMARY
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    all_constraints = [
        ("Strict Weekly Hours", constraint1_pass),
        ("Daily Diversity", constraint2_pass),
        ("Lab Continuity", constraint3_pass),
        ("NSS/FREE Placement", constraint4_pass),
        ("No Faculty Conflicts", constraint5_pass)
    ]
    
    passed = sum(1 for _, result in all_constraints if result)
    total = len(all_constraints)
    
    for name, result in all_constraints:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} constraints passed")
    
    if violations:
        print("\n⚠️  VIOLATIONS FOUND:")
        for v in violations:
            print(v)
    
    if passed == total:
        print("\n🎉 ALL CONSTRAINTS PASSED! System is working correctly.")
        return True
    else:
        print("\n❌ SOME CONSTRAINTS FAILED! Review violations above.")
        return False

if __name__ == "__main__":
    test_all_constraints()
