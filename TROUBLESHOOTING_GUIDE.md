# TROUBLESHOOTING GUIDE - Subject Database & Faculty Core

## ⚠️ IMPORTANT: Browser Cache Issue

If you're still seeing the old behavior, it's likely a **browser caching issue**. Follow these steps:

### Step 1: Clear Browser Cache (CRITICAL)

**Option A: Hard Refresh (Recommended)**
1. Open the page (subject.htm or faculty.htm)
2. Press `Ctrl + Shift + Delete` (Windows) or `Cmd + Shift + Delete` (Mac)
3. Select "Cached images and files"
4. Click "Clear data"
5. Close browser completely
6. Reopen and try again

**Option B: Force Reload**
1. Open the page
2. Press `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)
3. This forces browser to reload from server

**Option C: Incognito/Private Mode**
1. Open browser in Incognito/Private mode
2. Navigate to `http://localhost:5000/subject.htm?dept=ISE`
3. Test functionality

### Step 2: Verify Server is Running

1. Open Command Prompt
2. Navigate to project folder:
   ```
   cd c:\Users\surav\Downloads\TT_final-main
   ```
3. Start server:
   ```
   py unified_server.py
   ```
4. Wait for message: "Server: http://localhost:5000"
5. Keep this window open

### Step 3: Test Subject Database

1. Open browser (preferably Chrome or Edge)
2. Go to: `http://localhost:5000/subject.htm?dept=ISE`
3. Open Developer Tools (F12)
4. Go to Console tab
5. Test Year Dropdown:
   - Select "1st Year"
   - **Expected**: Console shows "Year selected: 1"
   - **Expected**: Semester dropdown shows "Semester 1" and "Semester 2"
6. Test Back Button:
   - Click "← Back to Dashboard" (green button)
   - **Expected**: Navigates to `http://localhost:5000/page.htm?dept=ISE`

### Step 4: Test Faculty Core

1. Go to: `http://localhost:5000/faculty.htm?dept=ISE`
2. Open Developer Tools (F12)
3. Go to Console tab
4. Test Back Button:
   - Click "← Back to Home" (blue button at top left)
   - **Expected**: Console shows "Back button clicked, navigating to: page.htm?dept=ISE"
   - **Expected**: Navigates to dashboard

### Step 5: Verify Database Connection

1. Open browser console (F12)
2. Go to Network tab
3. Add a subject or faculty
4. Look for POST request to Supabase
5. **Expected**: Status 200 or 201
6. **If fails**: Check Supabase URL and API key

---

## 🔍 Detailed Testing Steps

### Subject Database - Year/Semester Dropdown

**Test Case 1: Year 1**
1. Select "1st Year" from Year dropdown
2. ✅ Semester dropdown should show:
   - "Semester 1"
   - "Semester 2"
3. ❌ If empty: Clear cache and try again

**Test Case 2: Year 2**
1. Select "2nd Year" from Year dropdown
2. ✅ Semester dropdown should show:
   - "Semester 3"
   - "Semester 4"

**Test Case 3: Year 3**
1. Select "3rd Year" from Year dropdown
2. ✅ Semester dropdown should show:
   - "Semester 5"
   - "Semester 6"

**Test Case 4: Year 4**
1. Select "4th Year" from Year dropdown
2. ✅ Semester dropdown should show:
   - "Semester 7"
   - "Semester 8"

### Subject Database - Back Button

**Test Case 1: Navigation**
1. Click "← Back to Dashboard" button (green button at top)
2. ✅ Should navigate to: `http://localhost:5000/page.htm?dept=ISE`
3. ✅ Dashboard should load with all tiles visible
4. ❌ If nothing happens: Check console for errors

### Subject Database - Add Subject

**Test Case 1: Add Theory Subject**
1. Enter Academic Year: "2024-25"
2. Select Year: "3rd Year"
3. Select Semester: "Semester 5"
4. Enter Subject Code: "IS501"
5. Enter Subject Name: "Database Management Systems"
6. Set Credits: 4
7. Set Type: Theory
8. Set Weekly Hours: 3
9. Click "➕ Add Subject"
10. ✅ Success toast should appear
11. ✅ Subject should appear in table
12. ✅ Check Supabase subjects table for new row

**Test Case 2: Add Lab Subject**
1. Follow steps above but:
2. Set Type: Lab (2 consecutive hours)
3. Set Weekly Hours: 2
4. ✅ Should save successfully

### Subject Database - Delete Subject

**Test Case 1: Delete**
1. Add a test subject
2. Click "🗑️ Delete" button on that row
3. ✅ Confirmation dialog should appear
4. Click "OK"
5. ✅ Success toast should appear
6. ✅ Subject should disappear from table
7. ✅ Check Supabase - row should be deleted

### Faculty Core - Back Button

**Test Case 1: Navigation**
1. Click "← Back to Home" button (blue button at top left)
2. ✅ Console should show: "Back button clicked, navigating to: page.htm?dept=ISE"
3. ✅ Should navigate to dashboard
4. ❌ If nothing happens: Check if button is visible and clickable

### Faculty Core - Add Faculty

**Test Case 1: Add Professor**
1. Enter Faculty Name: "Dr. John Smith"
2. Enter Initials: "Dr. JS"
3. Select Designation: "Professor"
4. Click "Add Faculty"
5. ✅ Success toast should appear
6. ✅ Faculty should appear in table
7. ✅ Statistics should update
8. ✅ Check Supabase faculty table

### Faculty Core - Edit Faculty

**Test Case 1: Edit**
1. Click "Edit" button on any faculty row
2. ✅ Modal should appear with current data
3. Change name to "Dr. Jane Doe"
4. Click "Save"
5. ✅ Success toast should appear
6. ✅ Table should update
7. ✅ Check Supabase for update

### Faculty Core - Delete Faculty

**Test Case 1: Delete**
1. Click "Delete" button on any faculty row
2. ✅ Confirmation dialog should appear
3. Click "OK"
4. ✅ Success toast should appear
5. ✅ Faculty should disappear
6. ✅ Statistics should update
7. ✅ Check Supabase - row should be deleted

---

## 🐛 Common Issues and Solutions

### Issue 1: Semester dropdown is empty
**Cause**: Browser cache or JavaScript not loading
**Solution**:
1. Clear browser cache (Ctrl + Shift + Delete)
2. Hard refresh (Ctrl + F5)
3. Check console for JavaScript errors
4. Try test_dropdown.html to verify logic works

### Issue 2: Back button does nothing
**Cause**: JavaScript error or button not clickable
**Solution**:
1. Open console (F12)
2. Click back button
3. Check for errors in console
4. Verify button is visible (not hidden behind other elements)
5. Check if onclick handler is attached

### Issue 3: Add subject/faculty doesn't save
**Cause**: Supabase connection issue
**Solution**:
1. Check Network tab in browser
2. Look for failed requests
3. Verify Supabase URL and API key in code
4. Check Supabase dashboard for connection status
5. Verify RLS policies allow inserts

### Issue 4: Changes not appearing
**Cause**: Browser cache
**Solution**:
1. Close browser completely
2. Reopen in Incognito mode
3. Test functionality
4. If works in Incognito, clear cache in normal mode

### Issue 5: Console shows errors
**Cause**: Various
**Solution**:
1. Read error message carefully
2. Check if Supabase client is loaded
3. Verify all IDs match between HTML and JavaScript
4. Check for typos in function names

---

## 📋 Verification Checklist

### Before Testing
- [ ] Server is running (py unified_server.py)
- [ ] Browser cache is cleared
- [ ] Developer tools are open (F12)
- [ ] Console tab is visible
- [ ] Network tab is ready

### Subject Database
- [ ] Year dropdown shows 4 options
- [ ] Selecting Year 1 shows Semester 1, 2
- [ ] Selecting Year 2 shows Semester 3, 4
- [ ] Selecting Year 3 shows Semester 5, 6
- [ ] Selecting Year 4 shows Semester 7, 8
- [ ] Back button navigates to dashboard
- [ ] Add subject saves to database
- [ ] Delete subject removes from database
- [ ] Clear all works correctly
- [ ] Toast notifications appear

### Faculty Core
- [ ] Back button navigates to dashboard
- [ ] Console shows navigation message
- [ ] Add faculty saves to database
- [ ] Edit faculty updates database
- [ ] Delete faculty removes from database
- [ ] Clear all works correctly
- [ ] View all displays correctly
- [ ] Statistics update correctly
- [ ] Toast notifications appear

---

## 🔧 Advanced Troubleshooting

### Check if files are being served correctly

1. Open browser
2. Go to: `http://localhost:5000/subject.htm?dept=ISE`
3. Right-click → View Page Source
4. Search for "Back to Dashboard"
5. ✅ Should find: `<button onclick="goBackToDashboard()" class="btn-success">← Back to Dashboard</button>`
6. ❌ If not found: Server is serving old file

### Check JavaScript console for errors

1. Open console (F12)
2. Look for red error messages
3. Common errors:
   - "supabase is not defined" → Supabase library not loaded
   - "Cannot read property of undefined" → Element ID mismatch
   - "Failed to fetch" → Server not running or wrong URL

### Verify Supabase connection

1. Open console (F12)
2. Type: `supabase`
3. Press Enter
4. ✅ Should show object with methods
5. ❌ If undefined: Supabase library not loaded

### Test with simple HTML file

1. Open: `http://localhost:5000/test_dropdown.html`
2. Select a year
3. ✅ Semester dropdown should populate
4. ✅ Result div should show selected values
5. This proves the logic works

---

## 📞 If Still Not Working

1. **Take screenshots** of:
   - Browser console (F12 → Console tab)
   - Network tab showing requests
   - The actual page showing the issue

2. **Check these files exist**:
   - subject.htm (should have "Back to Dashboard")
   - faculty.htm (should have "Back to Home")
   - unified_server.py (should be running)

3. **Verify URLs**:
   - Subject: `http://localhost:5000/subject.htm?dept=ISE`
   - Faculty: `http://localhost:5000/faculty.htm?dept=ISE`
   - Dashboard: `http://localhost:5000/page.htm?dept=ISE`

4. **Check server console** for errors

5. **Try different browser** (Chrome, Edge, Firefox)

---

## ✅ Success Indicators

When everything is working correctly, you should see:

### Subject Database
- ✅ Year dropdown has 4 options
- ✅ Semester dropdown populates when year selected
- ✅ Back button navigates to dashboard
- ✅ Add button saves to database
- ✅ Delete button removes from database
- ✅ Toast notifications appear
- ✅ No console errors

### Faculty Core
- ✅ Back button navigates to dashboard
- ✅ Console shows navigation message
- ✅ Add button saves to database
- ✅ Edit button opens modal and updates
- ✅ Delete button removes from database
- ✅ Toast notifications appear
- ✅ No console errors

---

**Last Updated**: $(date)
**Status**: All fixes applied, awaiting user testing
