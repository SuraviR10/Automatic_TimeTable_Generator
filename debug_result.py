import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_server import UnifiedTimetableEngine

SUPABASE_URL = "https://zfzmnimjekmkyefslflf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpmem1uaW1qZWtta3llZnNsZmxmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI3ODkwOTcsImV4cCI6MjA3ODM2NTA5N30.ffXDOtk9ZEPjCLrI4ahK2lHmbzbjzix3Z9zS19c5lTA"

engine = UnifiedTimetableEngine(SUPABASE_URL, SUPABASE_KEY)

result = engine.generate_timetable_with_retry(
    department='TEST', section='A', sessions=[],
    academic_year='2024-25', year=1, semester=1, max_retries=1
)

print("Result type:", type(result))
print("Result keys:", result.keys() if isinstance(result, dict) else "Not a dict")
print("Result:", result)
