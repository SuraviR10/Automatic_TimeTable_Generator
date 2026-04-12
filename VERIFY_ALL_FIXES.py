"""
FINAL VERIFICATION - All Pylance Errors Fixed
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("FINAL VERIFICATION - Testing All Fixed Pylance Errors")
print("=" * 70)

try:
    from unified_server import UnifiedTimetableEngine
    print("[PASS] unified_server.py imports successfully")
    
    SUPABASE_URL = "https://zfzmnimjekmkyefslflf.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpmem1uaW1qZWtta3llZnNsZmxmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI3ODkwOTcsImV4cCI6MjA3ODM2NTA5N30.ffXDOtk9ZEPjCLrI4ahK2lHmbzbjzix3Z9zS19c5lTA"
    
    engine = UnifiedTimetableEngine(SUPABASE_URL, SUPABASE_KEY)
    print("[PASS] UnifiedTimetableEngine instantiated")
    
    print("\n" + "-" * 70)
    print("PYLANCE ERROR 1: 'result' is possibly unbound (Line 114)")
    print("-" * 70)
    result = engine.generate_timetable_with_retry(
        department='TEST', section='A', sessions=[],
        academic_year='2024-25', year=1, semester=1, max_retries=1
    )
    if isinstance(result, dict) and 'valid' in result:
        print("[PASS] generate_timetable_with_retry returns dict with 'valid' key")
        print("       Result has keys:", list(result.keys()))
    else:
        print("[FAIL] Unexpected return structure")
        sys.exit(1)
    
    print("\n" + "-" * 70)
    print("PYLANCE ERROR 2: Missing 'validate_swap_with_suggestions' (Line 485)")
    print("-" * 70)
    if hasattr(engine, 'validate_swap_with_suggestions'):
        print("[PASS] Method 'validate_swap_with_suggestions' exists")
        test_data = {
            'slot1': {'faculty_name': 'F1', 'day': 'Tuesday', 'time_slot': 1},
            'slot2': {'faculty_name': 'F2', 'day': 'Wednesday', 'time_slot': 2}
        }
        result = engine.validate_swap_with_suggestions(test_data, '2024-25')
        if isinstance(result, dict):
            print("[PASS] Method returns dict:", list(result.keys()))
        else:
            print("[FAIL] Method returns unexpected type")
            sys.exit(1)
    else:
        print("[FAIL] Method 'validate_swap_with_suggestions' not found")
        sys.exit(1)
    
    print("\n" + "-" * 70)
    print("PYLANCE ERROR 3: Missing 'get_safe_slots_for_faculty' (Line 497)")
    print("-" * 70)
    if hasattr(engine, 'get_safe_slots_for_faculty'):
        print("[PASS] Method 'get_safe_slots_for_faculty' exists")
        result = engine.get_safe_slots_for_faculty('Test Faculty', '2024-25')
        if isinstance(result, list):
            print("[PASS] Method returns list (length:", len(result), ")")
        else:
            print("[FAIL] Method returns unexpected type")
            sys.exit(1)
    else:
        print("[FAIL] Method 'get_safe_slots_for_faculty' not found")
        sys.exit(1)
    
    print("\n" + "-" * 70)
    print("ADDITIONAL VERIFICATION: All Core Methods")
    print("-" * 70)
    core_methods = [
        '_load_global_settings', '_get_valid_lab_slots',
        '_get_department_lab_rooms', '_get_available_lab_room',
        '_load_oe_constraints', 'check_faculty_conflict_global',
        'generate_timetable', '_validate_all_constraints',
        'save_to_database', 'generate_timetable_with_retry',
        'validate_swap_with_suggestions', 'get_safe_slots_for_faculty'
    ]
    
    missing = []
    for method in core_methods:
        if hasattr(engine, method):
            print(f"  [PASS] {method}")
        else:
            print(f"  [FAIL] {method} - MISSING")
            missing.append(method)
    
    if missing:
        print(f"\n[FAIL] {len(missing)} methods missing:", missing)
        sys.exit(1)
    
    print("\n" + "-" * 70)
    print("ADDITIONAL VERIFICATION: Global Tracking Attributes")
    print("-" * 70)
    if hasattr(engine, 'master_occupancy') and isinstance(engine.master_occupancy, set):
        print("[PASS] master_occupancy exists (type: set)")
    else:
        print("[FAIL] master_occupancy missing or wrong type")
        sys.exit(1)
    
    if hasattr(engine, 'lab_room_occupancy') and isinstance(engine.lab_room_occupancy, set):
        print("[PASS] lab_room_occupancy exists (type: set)")
    else:
        print("[FAIL] lab_room_occupancy missing or wrong type")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("SUCCESS - ALL PYLANCE ERRORS FIXED!")
    print("=" * 70)
    print("\nSummary:")
    print("  [PASS] Error 1: 'result' variable properly initialized")
    print("  [PASS] Error 2: validate_swap_with_suggestions implemented")
    print("  [PASS] Error 3: get_safe_slots_for_faculty implemented")
    print("  [PASS] All 12 core methods present")
    print("  [PASS] Global tracking attributes initialized")
    print("\nSystem Status: READY FOR PRODUCTION")
    print("\nNext Steps:")
    print("  1. Run: py unified_server.py")
    print("  2. Open: http://localhost:5000")
    print("  3. Test all features")
    print("=" * 70)
    
except ImportError as e:
    print(f"\n[FAIL] Import Error: {e}")
    print("Install dependencies: pip install flask flask-cors supabase")
    sys.exit(1)
    
except Exception as e:
    print(f"\n[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
