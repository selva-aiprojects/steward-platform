# StockSteward AI - End-to-End Test Script for Investment Reports

## Test Scenario: Investment Reports & Performance Analysis

### Prerequisites
- StockSteward AI application running
- Test user accounts prepared:
  - Trader: trader@stocksteward.ai / trader123
  - Business Owner: owner@stocksteward.ai / owner123
  - Super Admin: admin@stocksteward.ai / admin123
  - Auditor: auditor@stocksteward.ai / audit123

## Test Case 1: Trader User Journey

### Step 1: Login as Trader
- Navigate to: http://localhost:3000/login
- Email: trader@stocksteward.ai
- Password: trader123
- Click "Login"

### Step 2: Navigate to Investment Reports
- Click on "Reports" in sidebar
- Click on "Investment Reports" in sidebar
- OR Navigate to: http://localhost:3000/reports/investment

### Step 3: Verify Dashboard Loads
- Verify page title: "Investment Performance Reports"
- Verify sub-title: "Algorithmic vs Manual Trading Performance Analysis"
- Verify time range selector appears
- Verify refresh button appears

### Step 4: Verify Performance Summary Cards
- Verify "Total Return" card displays value
- Verify "Win Rate" card displays value
- Verify "Sharpe Ratio" card displays value
- Verify "Max Drawdown" card displays value

### Step 5: Verify Performance Difference Highlights
- Verify "Return Advantage" card displays positive value
- Verify "Win Rate Advantage" card displays positive value
- Verify "Risk-Adjusted Advantage" card displays positive value

### Step 6: Test Tab Navigation
- Click "Performance Overview" tab (verify active)
- Click "Algo vs Manual" tab (verify active)
- Click "Transaction Statement" tab (verify active)

### Step 7: Test Performance Overview Tab
- Verify "Portfolio Growth Comparison" chart displays
- Hover over chart to verify tooltips work
- Verify "Algorithmic Performance" metrics display
- Verify "Manual Performance" metrics display

### Step 8: Test Algo vs Manual Tab
- Verify detailed comparison table displays
- Verify all metrics columns appear (Total Return, Win Rate, etc.)
- Verify "Key Performance Insights" section displays

### Step 9: Test Transaction Statement Tab
- Verify transaction table displays
- Verify filter buttons work (All Trades, Algorithmic, Manual)
- Verify sorting controls work
- Verify summary stats display correctly

### Step 10: Test Time Range Filtering
- Change time range to "30d"
- Verify data updates
- Change time range to "90d"
- Verify data updates

### Step 11: Test Refresh Functionality
- Click refresh button
- Verify data reloads
- Verify no errors occur

### Step 12: Logout
- Click logout button
- Verify redirected to login page

---

## Test Case 2: Business Owner User Journey

### Step 1: Login as Business Owner
- Navigate to: http://localhost:3000/login
- Email: owner@stocksteward.ai
- Password: owner123
- Click "Login"

### Step 2: Navigate to Investment Reports
- Click on "Reports" in sidebar
- Click on "Investment Reports" in sidebar

### Step 3: Verify Executive-Focused View
- Verify page title: "Investment Performance Reports"
- Verify executive-level metrics display
- Verify ROI-focused insights available

### Step 4: Test All Dashboard Features
- Repeat Steps 4-11 from Trader test case
- Verify all functionality works identically

### Step 5: Verify Business Owner Specific Elements
- Verify any business owner specific metrics
- Verify revenue-focused reporting elements

### Step 6: Logout
- Click logout button

---

## Test Case 3: Super Admin User Journey

### Step 1: Login as Super Admin
- Navigate to: http://localhost:3000/login
- Email: admin@stocksteward.ai
- Password: admin123
- Click "Login"

### Step 2: Navigate to Investment Reports
- Click on "Reports" in sidebar
- Click on "Investment Reports" in sidebar

### Step 3: Verify Admin-Focused View
- Verify page title: "Investment Performance Reports"
- Verify administrative controls available
- Verify system-level metrics display

### Step 4: Test All Dashboard Features
- Repeat Steps 4-11 from Trader test case
- Verify all functionality works identically

### Step 5: Verify Admin Specific Elements
- Verify any admin-specific controls
- Verify system oversight capabilities

### Step 6: Logout
- Click logout button

---

## Test Case 4: Auditor User Journey

### Step 1: Login as Auditor
- Navigate to: http://localhost:3000/login
- Email: auditor@stocksteward.ai
- Password: audit123
- Click "Login"

### Step 2: Navigate to Investment Reports
- Click on "Reports" in sidebar
- Click on "Investment Reports" in sidebar

### Step 3: Verify Audit-Focused View
- Verify page title: "Investment Performance Reports"
- Verify compliance-focused metrics display
- Verify audit trail elements available

### Step 4: Test All Dashboard Features
- Repeat Steps 4-11 from Trader test case
- Verify all functionality works identically

### Step 5: Verify Audit Specific Elements
- Verify any audit-specific reporting
- Verify compliance metrics display
- Verify regulatory reporting elements

### Step 6: Logout
- Click logout button

---

## Test Case 5: Cross-User Consistency Check

### Step 1: Verify Feature Consistency
- Login as each user type
- Navigate to investment reports
- Verify identical core functionality
- Verify role-appropriate customizations

### Step 2: Verify Data Isolation
- Login as one user type
- Note specific data points
- Login as different user type
- Verify different user data appears
- Verify no cross-user data leakage

### Step 3: Verify Permission Boundaries
- Verify each user type has appropriate access
- Verify no unauthorized features accessible
- Verify role-based UI elements correct

---

## Expected Results

### Functional Requirements
- [ ] All user types can access investment reports
- [ ] Performance comparison charts display correctly
- [ ] All metrics calculate and display accurately
- [ ] Filtering and sorting work properly
- [ ] Navigation works consistently
- [ ] Responsive design functions on all devices

### Performance Requirements
- [ ] Page loads in < 3 seconds
- [ ] Charts render smoothly
- [ ] Data updates quickly
- [ ] No performance degradation with filters

### Security Requirements
- [ ] Proper authentication required
- [ ] Role-based access enforced
- [ ] Data isolation maintained
- [ ] No privilege escalation possible

### Usability Requirements
- [ ] Intuitive navigation
- [ ] Clear performance indicators
- [ ] Professional appearance
- [ ] Accessible design elements

---

## Test Data

### Sample Performance Data
- Algorithmic Total Return: 12.5%
- Manual Total Return: 6.8%
- Return Difference: +5.7%
- Algorithmic Win Rate: 87%
- Manual Win Rate: 62%
- Win Rate Difference: +25%

### Sample Transaction Data
- Trade ID: 1-5
- Symbols: RELIANCE, HDFCBANK, INFY, TCS, SBIN
- Actions: BUY, SELL
- Strategies: ALGO, MANUAL
- P&L Values: -200 to +300 range

---

## Success Criteria
- All test cases pass for all user types
- No critical or high severity defects
- Performance meets requirements
- Security controls function properly
- User experience is consistent and professional