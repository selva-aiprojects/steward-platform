# Enterprise Transformation Walkthrough: RBAC & User Management

This document details the technical implementation of the Role-Based Access Control (RBAC) system and the "Superadmin" capabilities added to StockSteward AI.

## 1. System Architecture: The "Who is Who" (Context)
We moved away from hardcoded user IDs (e.g., always fetching User 1) to a dynamic **User Context**.
- **File**: `frontend/src/context/UserContext.jsx`
- **What it does**: It acts as the "Identity Card" for the app. When you log in, it stores your `ID`, `Name`, and `Role` (ADMIN vs USER). Every other page checks this card before loading data.

## 2. The Gatekeeper (Authentication)
We replaced the direct access to the dashboard with a secure **Login Portal**.
- **File**: `frontend/src/pages/Login.jsx`
- **Features**:
  - **Simulation**: Allows you to instantly "Login as Super Admin" or "Login as Portfolio Manager" to test both experiences.
  - **Route Protection**: The `App.jsx` now checks if a user is logged in. If not, it kicks them back to `/login`.

## 3. The Backend "Brain" (Database & API)
We updated the Python backend to remember your new settings.

### A. Database Models
- **User Model**: Added `allowed_sectors` (for industry restrictions) and `trading_mode` (Auto vs Manual).
- **Audit Log Model**: Created a completely new table `audit_logs` to track *every* admin action.
  - *Why?* Compliance. If a user loses money because they were switched to "Manual", we need proof of who switched them and why.

### B. API Endpoints
- **Update User (`PUT /users/{id}`)**: modified to allow Admin to change `trading_mode` and `allowed_sectors`.
- **Audit (`POST /audit/`)**: A new endpoint that creates a permanent record of these changes.

## 4. The Admin Control Room (Frontend)
We built a dedicated **User Management Interface** for the Superadmin.
- **File**: `frontend/src/pages/Users.jsx`
- **New Features**:
  - **Policy Modal**: Clicking "Manage Configuration" opens a professional modal.
  - **Controls**: 
    - Toggle "Execution Mode" (Auto/Manual).
    - Select "Authorized Industries" (e.g., restrict a user to only Healthcare stocks).
    - **Reason for Change**: A mandatory text field for the Audit Log.
  - **Connectivity**: When you click "Confirm", it fires two API calls: one to update the user settings, and one to log the audit trail.

## 5. The User Experience (Trading Hub)
We made the user's view react to the Admin's decisions.
- **File**: `frontend/src/pages/TradingHub.jsx`
- **Transformation**:
  - If Admin sets **Auto Mode**: The "Manual Mode" buttons are locked/disabled. A visual "Lock" icon appears telling the user "Steward AI is managing this."
  - If Admin sets **Manual Mode**: The user sees "Manual Override Active" and gains control.

## How to Test It
1. **Login as Super Admin**.
2. Go to the new **User Mgmt** tab (sidebar).
3. Pick a user (e.g., Demo User).
4. **Change** them to "Manual Mode" and **Restrict** them to "Technology". Add a comment "User requested control".
5. **Logout**.
6. **Login as Portfolio Manager** (the user you just changed).
7. Go to **Trading Hub**. You will see "Manual Override Active" and the settings you applied.
