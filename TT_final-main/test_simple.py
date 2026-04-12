"""
Constraint Validation Test - Simple Version
"""

def test_constraints():
    print("=" * 70)
    print("CONSTRAINT VALIDATION TEST")
    print("=" * 70)
    
    # Sample timetable
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
            4: None, 5: None, 6: None
        },
        'Thursday': {
            1: {'subject_code': 'CS501', 'faculty_name': 'Dr. Smith', 'type': 'theory'},
            2: {'subject_code': 'CS502', 'faculty_name': 'Dr. Jones', 'type': 'theory'},
            3: {'subject_code': 'CS504', 'faculty_name': 'Dr. Brown', 'type': 'theory'},
            4: None, 5: None, 6: None
        },
        'Friday': {1: None, 2: None, 3: None, 4: None, 5: None, 6: None},
        'Saturday': {1: None, 2: None, 3: None, 4: None, 5: None, 6: None}
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
    
    # CONSTRAINT 1: Strict Weekly Hours
    print("\n[1] Testing: Strict Weekly Hours")
    subject_hours = {}
    for day in work_days:
        for slot in range(1, periods_per_day + 1):
            entry = timetable[day].get(slot)
            if entry:
                code = entry['subject_code']
                subject_hours[code] = subject_hours.get(code, 0) + 1
    
    c1_pass = True
    for session in sessions:
        expected = session['weekly_hours']
        actual = subject_hours.get(session['subject_code'], 0)
        if actual != expected:
            print(f"    FAIL: {session['subject_code']} - Expected {expected}, got {actual}")
            c1_pass = False
        else:
            print(f"    PASS: {session['subject_code']} - {actual}/{expected} hours")
    
    # CONSTRAINT 2: Daily Diversity
    print("\n[2] Testing: Daily Diversity (No same subject twice per day)")
    c2_pass = True
    for day in work_days:
        day_subjects = []
        for slot in range(1, periods_per_day + 1):
            entry = timetable[day].get(slot)
            if entry and entry['subject_code'] not in ['FREE', 'NSS']:
                if entry['subject_code'] in day_subjects:
                    print(f"    FAIL: {entry['subject_code']} repeated on {day}")
                    c2_pass = False
                day_subjects.append(entry['subject_code'])
        if day_subjects:
            print(f"    PASS: {day} - {', '.join(set(day_subjects))}")
    
    # CONSTRAINT 3: Lab Continuity
    print("\n[3] Testing: Lab Continuity (2 continuous, no breaks)")
    valid_lab_slots = []
    for i in range(1, periods_per_day):
        if i <= tea_break_after < i + 1:
            continue
        if i <= lunch_break_after < i + 1:
            continue
        valid_lab_slots.append((i, i + 1))
    
    print(f"    Valid lab slots: {valid_lab_slots}")
    c3_pass = True
    for day in work_days:
        for slot in range(1, periods_per_day):
            entry = timetable[day].get(slot)
            if entry and entry.get('type') == 'lab':
                if (slot, slot + 1) not in valid_lab_slots:
                    print(f"    FAIL: Lab at {day} P{slot}")
                    c3_pass = False
                else:
                    print(f"    PASS: Lab {entry['subject_code']} at {day} P{slot}-P{slot+1}")
    
    # CONSTRAINT 4: NSS/FREE Only in P6
    print("\n[4] Testing: NSS/FREE Only in Period 6")
    c4_pass = True
    for day in work_days:
        for slot in range(1, periods_per_day):
            entry = timetable[day].get(slot)
            if entry and entry['subject_code'] in ['NSS', 'FREE']:
                print(f"    FAIL: NSS/FREE in P{slot} on {day}")
                c4_pass = False
        entry = timetable[day].get(periods_per_day)
        if entry and entry['subject_code'] in ['NSS', 'FREE']:
            print(f"    PASS: {entry['subject_code']} in {day} P{periods_per_day}")
    
    # CONSTRAINT 5: No Faculty Conflicts
    print("\n[5] Testing: No Faculty Conflicts")
    faculty_schedule = {}
    c5_pass = True
    for day in work_days:
        for slot in range(1, periods_per_day + 1):
            entry = timetable[day].get(slot)
            if entry and entry['faculty_name'] != 'N/A':
                key = f"{entry['faculty_name']}-{day}-{slot}"
                if key in faculty_schedule:
                    print(f"    FAIL: {entry['faculty_name']} conflict on {day} P{slot}")
                    c5_pass = False
                faculty_schedule[key] = True
    
    faculty_counts = {}
    for day in work_days:
        for slot in range(1, periods_per_day + 1):
            entry = timetable[day].get(slot)
            if entry and entry['faculty_name'] != 'N/A':
                faculty_counts[entry['faculty_name']] = faculty_counts.get(entry['faculty_name'], 0) + 1
    
    for faculty, count in faculty_counts.items():
        print(f"    PASS: {faculty} - {count} periods")
    
    # SUMMARY
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    results = [
        ("Strict Weekly Hours", c1_pass),
        ("Daily Diversity", c2_pass),
        ("Lab Continuity", c3_pass),
        ("NSS/FREE Placement", c4_pass),
        ("No Faculty Conflicts", c5_pass)
    ]
    
    passed = sum(1 for _, r in results if r)
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {name}")
    
    print(f"\nTotal: {passed}/5 constraints passed")
    
    if passed == 5:
        print("\nSUCCESS: All constraints working correctly!")
        return True
    else:
        print("\nFAILURE: Some constraints failed!")
        return False

if __name__ == "__main__":
    test_constraints()
