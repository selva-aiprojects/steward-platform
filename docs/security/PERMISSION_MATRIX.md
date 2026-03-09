# API Permission Matrix

## Purpose
Role-based access baseline for core endpoints in production.

## Roles
- `SUPERADMIN`
- `BUSINESS_OWNER`
- `TRADER`
- `AUDITOR`

## Matrix

| Endpoint Area | SUPERADMIN | BUSINESS_OWNER | TRADER | AUDITOR |
|---|---|---|---|---|
| `POST /api/v1/auth/login` | Allow | Allow | Allow | Allow |
| `GET /api/v1/users/*` | Allow | Allow | Self/Restricted | Read-only restricted |
| `POST /api/v1/users/*` | Allow | Allow | Deny | Deny |
| `GET /api/v1/trades` | Allow | Allow | Self | Read-only |
| `POST /api/v1/trades` | Allow | Allow | Self | Deny |
| `POST /api/v1/trades/paper/order` | Allow | Allow | Self | Deny |
| `POST /api/v1/trades/paper/seed-all` | Allow | Allow | Deny | Deny |
| `GET /api/v1/approvals` | Allow | Allow | Deny | Read-only |
| `POST /api/v1/approvals/{id}/approve` | Allow | Allow | Deny | Deny |
| `POST /api/v1/approvals/{id}/reject` | Allow | Allow | Deny | Deny |
| `GET /api/v1/kyc/applications` | Allow | Allow | Self submissions only | Read-only |
| `POST /api/v1/kyc/applications/{id}/approve` | Allow | Allow | Deny | Deny |
| `POST /api/v1/kyc/applications/{id}/reject` | Allow | Allow | Deny | Deny |
| `GET /api/v1/logs/*` | Allow | Allow | Deny | Allow (read-only) |
| `GET /api/v1/admin/*` | Allow | Allow | Deny | Deny |

## Notes
- In `PROD`, bearer-token identity is mandatory.
- Header/query identity fallback is for non-prod debugging only.
- Live-trading execution requires approved KYC status.

