# Dreambook Salon - Quick Start Testing Guide

**Last Updated**: November 21, 2025
**Status**: Ready to Test ✅

---

## 🚀 30-Second Setup

```bash
# 1. Ensure virtual environment is active
python --version  # Should be 3.8+

# 2. Dependencies are installed
pip list | grep django  # Should be 5.2.8

# 3. Database migrated (already done)
python manage.py showmigrations audit_log
# Output should show: [X] 0001_initial

# 4. Start server
python manage.py runserver
# Opens at http://localhost:8000
```

---

## ✅ Feature Testing Workflow

### Test 1: User Management (5 minutes)

**Step 1: Access User List**
```
URL: http://localhost:8000/users/
Expected:
  ✅ User list page loads
  ✅ Shows existing users
  ✅ "Create User" button visible
  ✅ Search bar present
  ✅ Role filter dropdown present
```

**Step 2: Create New User**
```
1. Click "+ Create User" button
2. Fill form:
   - Email: john@salon.com
   - First Name: John
   - Last Name: Doe
   - Role: STAFF
3. Click "✨ Create User"

Expected:
  ✅ Success message: "User john@salon.com created successfully!"
  ✅ Redirects to user list
  ✅ New user appears in list
  ✅ New user visible in search
```

**Step 3: Edit User**
```
1. Find created user "john@salon.com"
2. Click "Edit" link
3. Change: Role to ADMIN
4. Click "💾 Save Changes"

Expected:
  ✅ Success message: "User john@salon.com updated successfully!"
  ✅ Role changes to ADMIN
  ✅ User list updates
  ✅ Audit log records change
```

**Step 4: View User Details**
```
1. Click "View" link for John Doe
2. Expected to see:
   ✅ Full user profile displayed
   ✅ Account Information section
   ✅ Quick Actions sidebar
   ✅ Activity History table (if any actions)
```

**Step 5: Deactivate User**
```
1. On user detail page
2. Click "⏸️ Deactivate User"
3. Confirm action
4. Click "⏸️ Deactivate User" button

Expected:
  ✅ Warning message: "User john@salon.com has been deactivated."
  ✅ User still in list but marked Inactive
  ✅ Detail button changes to "✅ Reactivate User"
  ✅ Audit log records deactivation
```

**Step 6: Test Search & Filter**
```
1. Go back to /users/
2. Type in Search: "john"
3. Expected: List filters to show only John

4. Test role filter:
   - Select "STAFF" from Role dropdown
   - Click Search
   Expected: Shows only STAFF users
```

---

### Test 2: Audit Logging (5 minutes)

**Step 1: Access Audit Dashboard**
```
URL: http://localhost:8000/audit/dashboard/
Expected:
  ✅ Dashboard loads
  ✅ Recent audit entries visible
  ✅ 50 entries per page
  ✅ Filter controls present
  ✅ Search box present
  ✅ Export button visible
```

**Step 2: Verify User Creation Was Logged**
```
1. On audit dashboard
2. Look for entry with:
   - Action: "✨ Created"
   - Description: "Created user john@salon.com"

Expected:
  ✅ Audit entry exists
  ✅ Shows correct timestamp
  ✅ Shows correct user (you)
  ✅ Shows correct description
```

**Step 3: Filter by Action Type**
```
1. Check "USER_CREATE" in action types
2. Click Apply filters

Expected:
  ✅ Only user creation entries shown
  ✅ Count decreases
  ✅ All entries are type "USER_CREATE"
```

**Step 4: Filter by Date Range**
```
1. Set date_from: Today
2. Set date_to: Today
3. Click Apply filters

Expected:
  ✅ Only today's entries shown
  ✅ Entries match current date
```

**Step 5: Test Search**
```
1. Search: "john@salon.com"
2. Click Search

Expected:
  ✅ Entries matching email shown
  ✅ Count decreases
  ✅ Description highlights match
```

**Step 6: Export to CSV**
```
1. Click "Export" button
2. File downloads

Expected:
  ✅ CSV file downloads
  ✅ Open in Excel/Sheets
  ✅ Contains audit entries
  ✅ Columns: timestamp, user, action, description, ip_address
```

---

### Test 3: Interactive Charts (5 minutes)

**Step 1: Access Charts**
```
URL: http://localhost:8000/analytics/charts/
Expected:
  ✅ Page loads
  ✅ 4 chart areas visible
  ✅ Charts labeled clearly
```

**Step 2: Weekly Seasonal Chart**
```
Look for:
  ✅ Line chart with 7 data points
  ✅ Gold-colored line
  ✅ Vertical dashed line for "TODAY"
  ✅ Points are labeled with dates
  ✅ Hover shows tooltip with value

Note: If no payment data exists, chart shows $0 values (normal)
```

**Step 3: Monthly Service Demand Chart**
```
Look for:
  ✅ Line chart with multiple colored lines
  ✅ One line per service
  ✅ 12 months of data on X-axis
  ✅ Legend shows service names
  ✅ Hover shows service and count

Note: If no appointment data exists, shows 0 counts (normal)
```

**Step 4: Revenue vs Cancellations Chart**
```
Look for:
  ✅ Bar chart side-by-side bars
  ✅ Gold bars for revenue
  ✅ Red bars for cancellations
  ✅ 12 months labeled
  ✅ Legend shows both metrics

Note: If no data, shows empty chart (normal)
```

**Step 5: Stylist Utilization Chart**
```
Look for:
  ✅ Horizontal bar chart
  ✅ Stylist names on Y-axis
  ✅ Percentage values (0-100%)
  ✅ Gold-colored bars
  ✅ Values sorted descending

Note: If less than 2 stylists, shows limited data (normal)
```

**Step 6: Test Chart Responsiveness**
```
1. Resize browser window (make narrow)
2. Expected: Charts adapt to width
3. Check on mobile (F12 → Toggle device toolbar)
4. Expected: Charts still readable
```

---

### Test 4: Security & Permissions (3 minutes)

**Step 1: Test Role-Based Access**
```
1. If logged in as CUSTOMER (not ADMIN/STAFF)
2. Try to access /users/
3. Expected:
   ✅ Permission denied or redirect
   ✅ Cannot access user management

Note: This tests StaffOrAdminRequiredMixin
```

**Step 2: Test Form Validation**
```
1. Go to /users/create/
2. Try to create user without email
3. Expected: Error message
4. Try to use existing email
5. Expected: "Email already in use" error
```

**Step 3: Test CSRF Protection**
```
1. View page source (F12 → Elements)
2. Search for "csrf" or "token"
3. Expected: Hidden CSRF token field in forms
```

---

## 📊 Data Integrity Tests

### Test 5: Database Verification (2 minutes)

**Check Audit Log Table**
```bash
python manage.py shell
>>> from audit_log.models import AuditLog
>>> AuditLog.objects.count()
# Should show number of audit entries

>>> logs = AuditLog.objects.all()[:3]
>>> for log in logs:
...     print(f"{log.user} - {log.action_type}")
```

**Check User Model**
```bash
python manage.py shell
>>> from core.models import User
>>> User.objects.count()
# Should show total users

>>> john = User.objects.filter(email='john@salon.com').first()
>>> print(john.role)
# Should print: ADMIN (what we set)
```

**Verify Migrations**
```bash
python manage.py migrate --plan
# Should show all migrations applied including audit_log
```

---

## 🎨 Theme Verification Tests

### Test 6: Black & Gold Theme (2 minutes)

**Color Check**:
```
1. Open any user management page
2. Look for:
   ✅ Gold buttons (#d4af37)
   ✅ Black text on cream backgrounds
   ✅ Gold/Black badges and pills
   ✅ Consistent spacing
   ✅ Professional appearance

3. Check chart colors:
   ✅ Charts use gold primary color
   ✅ Red for negative metrics
   ✅ Green for positive metrics
   ✅ Black grids and text
```

**Responsive Design Check**:
```
1. Test on desktop (1920px)
   ✅ All content visible
   ✅ Tables properly formatted
   ✅ Buttons easily clickable

2. Test on tablet (768px)
   ✅ Layout adapts
   ✅ Navigation still accessible
   ✅ Forms readable

3. Test on mobile (375px)
   ✅ Single column layout
   ✅ Hamburger menu (if applicable)
   ✅ Touch-friendly buttons
   ✅ Charts still visible
```

---

## 🐛 Known Limitations & Notes

**If you see these, it's normal:**

```
1. Empty charts:
   → Reason: No payment/appointment data yet
   → Fix: Create some test appointments first

2. No "Activity History" on user detail:
   → Reason: No audit logs for that user
   → Fix: Perform an action on the user

3. "Email already in use" on creation:
   → Reason: Email must be unique
   → Fix: Use a different email address

4. Chart tooltips cut off:
   → Reason: Limited space in viewport
   → Fix: Scroll or resize window

5. CSV export is plain text:
   → Expected: CSV format by design
   → Fix: Open in Excel to format properly
```

---

## 🎯 Test Completion Checklist

Mark each as you complete:

```
USER MANAGEMENT:
☐ Create user
☐ Edit user
☐ View user details
☐ Search users
☐ Filter by role
☐ Deactivate user
☐ Pagination works

AUDIT LOGGING:
☐ Audit dashboard loads
☐ User creation logged
☐ Filter by action type
☐ Filter by date
☐ Search functionality
☐ CSV export works

CHARTS:
☐ Weekly seasonal chart
☐ Service demand chart
☐ Revenue vs cancellations
☐ Utilization chart
☐ Charts responsive
☐ Charts interactive

SECURITY:
☐ Permission checks work
☐ Form validation works
☐ CSRF protection present
☐ Audit logs created

THEME:
☐ Colors are black & gold
☐ Layout is responsive
☐ Typography is consistent
☐ Professional appearance

INTEGRATION:
☐ No console errors
☐ No network errors
☐ All links work
☐ Navigation consistent
```

---

## 🚨 Troubleshooting Quick Fixes

**Problem**: "PermissionError" when accessing /users/
```
Solution: Ensure logged-in user is ADMIN or STAFF role
```

**Problem**: Charts not loading
```
Solution:
1. Open DevTools (F12)
2. Check Console for errors
3. Verify /analytics/api/... endpoints work
4. Check Chart.js CDN is loaded
```

**Problem**: Database errors
```
Solution:
1. Run: python manage.py migrate audit_log
2. Check: python manage.py migrate --plan
3. Reset if needed: python manage.py migrate audit_log zero
                     python manage.py migrate audit_log
```

**Problem**: Form says "Email already in use"
```
Solution: Check if user already exists
Run: python manage.py shell
     from core.models import User
     print(User.objects.filter(email='your@email.com').exists())
```

---

## 📈 Next Steps After Testing

1. **Create Test Data**:
   - Add 5-10 test users
   - Create some appointments
   - Record some payments
   - This populates charts with real data

2. **Test in Production**:
   - Deploy to staging server
   - Run full test suite
   - Get user feedback
   - Make minor adjustments

3. **Go Live**:
   - Deploy to production
   - Monitor for errors
   - Back up database regularly
   - Archive old audit logs

---

## 📞 Support

If you encounter issues:

1. **Check Documentation**:
   - IMPLEMENTATION_COMPLETE.md
   - IMPLEMENTATION_GUIDE.md
   - COMPLETION_SUMMARY.md

2. **Review Code Comments**:
   - User management views well-documented
   - Chart utilities clearly explained
   - Audit models have docstrings

3. **Check Logs**:
   - Django error logs
   - Browser console (F12)
   - Database error logs

---

**Time to Complete All Tests**: ~20-30 minutes

**All tests passing?** → System is ready for production! 🎉
