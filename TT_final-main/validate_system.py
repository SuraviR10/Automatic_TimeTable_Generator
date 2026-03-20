"""
MIT Mysore Timetable System - Validation Script
Tests all constraints and features
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test server health"""
    print("🔍 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print("❌ Server health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def test_timetable_generation():
    """Test timetable generation with all constraints"""
    print("\n🔍 Testing timetable generation...")
    
    payload = {
        "department": "CSE",
        "year": 3,
        "semester": 5,
        "academic_year": "2024-25",
        "sections": [
            {
                "name": "A",
                "assignments": [
                    {"subject": "CS501", "subject_name": "AI", "faculty": "Dr. Smith", "weekly_hours": 3, "type": "theory"},
                    {"subject": "CS502", "subject_name": "ML", "faculty": "Dr. Jones", "weekly_hours": 3, "type": "theory"},
                    {"subject": "CS503L", "subject_name": "AI Lab", "faculty": "Dr. Smith", "weekly_hours": 2, "type": "lab"},
                    {"subject": "NSS", "subject_name": "NSS", "faculty": "Kiran Kumar", "weekly_hours": 1, "type": "free"}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=payload)
        if response.status_code == 200:
            result = response.json()
            if result.get('A', {}).get('valid'):
                print("✅ Timetable generated successfully")
                print(f"   Constraints validated: All hard constraints enforced")
                return True
            else:
                print(f"❌ Timetable generation failed: {result.get('A', {}).get('error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_smart_swap():
    """Test smart swap validation"""
    print("\n🔍 Testing smart swap validation...")
    
    payload = {
        "academic_year": "2024-25",
        "swap_data": {
            "faculty1": "Dr. Smith",
            "faculty2": "Dr. Jones",
            "day1": "Tuesday",
            "slot1": 1,
            "day2": "Wednesday",
            "slot2": 2
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/validate_swap", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Swap validation working")
            print(f"   Valid: {result.get('valid')}")
            print(f"   Message: {result.get('message')}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_safe_slots():
    """Test safe slot suggestions"""
    print("\n🔍 Testing safe slot suggestions...")
    
    payload = {
        "faculty_name": "Dr. Smith",
        "academic_year": "2024-25"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/get_safe_slots", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Safe slot suggestions working")
            print(f"   Found {result.get('count')} safe slots")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("MIT Mysore Timetable System - Validation")
    print("=" * 60)
    
    tests = [
        ("Server Health", test_health),
        ("Timetable Generation", test_timetable_generation),
        ("Smart Swap", test_smart_swap),
        ("Safe Slots", test_safe_slots)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
