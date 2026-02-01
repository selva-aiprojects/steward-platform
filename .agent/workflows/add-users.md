---
description: How to add new users to the StockSteward AI platform
---

# User Onboarding Workflow

This workflow describes the process for a Superadmin to add new users (e.g., Investors, Auditors, or Business Owners) to the platform.

### Prerequisites
- Logged in as a **SUPERADMIN**.
- Access to the **User Management** section (simulated via the Dashboard User Selector).

### Steps

1. **Navigate to Executive Dashboard**
   - Access the main Dashboard at `/dashboard`.

2. **Access User Scope Management**
   - Locate the **"Scope"** selector in the header (available only to ADMIN roles).
   - In the current database-backed simulation, users are pre-provisioned, but you can "Switch Scope" to act on behalf of specific user types.

3. **Simulated User Addition (API)**
   - To add a new user to the database, use the following command structure in the terminal:
   // turbo
   ```powershell
   # Example: Adding an 'Investor' user
   curl -X POST "http://localhost:8000/users/" -H "Content-Type: application/json" -d '{
     "name": "Jane Doe",
     "email": "jane@example.com",
     "role": "INVESTOR",
     "trading_mode": "AUTO"
   }'
   ```

4. **Verify Onboarding**
   - Refresh the Dashboard.
   - The new user should now appear in the **Scope Selector** dropdown.
   - Select the new user to verify their dedicated data workspace is initialized.
