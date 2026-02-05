# RBAC Demo Users

Use the following demo users for login and role validation:

- **SUPERADMIN**: Arjun Malhotra — `admin@stocksteward.ai` / `admin123`
- **BUSINESS_OWNER**: Asha Iyer — `owner@stocksteward.ai` / `owner123`
- **TRADER**: Rahul Mehta — `trader@stocksteward.ai` / `trader123`
- **AUDITOR**: Kavya Nair — `auditor@stocksteward.ai` / `audit123`

## How to add users
1. **UI (User Mgmt)**: Navigate to `/users` as SUPERADMIN or BUSINESS_OWNER and use **Add User**.
2. **KYC Approval**: Submit a KYC application and approve it from the **KYC Desk**. A new user is auto-created.
3. **API**: `POST /api/v1/users/` with RBAC role and password.

