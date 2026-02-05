# StockSteward AI KYC System

This document describes the end-to-end KYC flow, backend APIs, schema, and compliance controls for the trading platform.

## Regulatory expectations (India)
- **SEBI KYC/AML**: Client Due Diligence (CDD), KYC verification, and audit trail for onboarding.
- **PMLA**: Identify and monitor higher-risk clients (PEP/sanctions flags), record retention, and escalation workflow.
- **CKYC alignment**: Capture PAN, identity/address proof references, and maintain a single KYC profile per client.
- **Privacy & security**: Minimize PII exposure, restrict access by role, log approvals, and use least-privilege.

This implementation provides the control points needed to satisfy these expectations, with placeholders for external KYC service integration.

## Workflow overview
1. **Investor submits KYC** via `/kyc` UI (public) or API.
2. **Application status** moves to `SUBMITTED`.
3. **Compliance reviewer** (SUPERADMIN/BUSINESS_OWNER) marks `UNDER_REVIEW`, adds notes.
4. **Approve or reject**:
   - Approve creates a user automatically with RBAC role + trading mode.
   - Reject stores review notes and closes the application.
5. **Auditability**: All review actions are persisted on the application record.

Statuses: `DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `APPROVED`, `REJECTED`.

## Database schema (SQL shape)
Table: `kyc_applications`
- `id` (PK)
- `full_name`, `email`, `phone`, `dob`
- `pan`, `aadhaar_last4`
- `address_line1`, `address_line2`, `city`, `state`, `pincode`, `country`
- `occupation`, `income_range`, `source_of_funds`
- `pep`, `sanctions`, `tax_residency`
- `bank_account_last4`, `ifsc`
- `desired_role`, `requested_trading_mode`, `risk_tolerance`
- `documents_json` (text JSON list)
- `status`, `reviewer_id`, `review_notes`, `reviewed_at`
- `created_at`, `updated_at`

## API endpoints
- `POST /api/v1/kyc/applications`
  - Creates a KYC application and sets status to `SUBMITTED`.
- `GET /api/v1/kyc/applications`
  - Lists applications (SUPERADMIN/BUSINESS_OWNER).
- `GET /api/v1/kyc/applications/{id}`
  - Retrieves one application (SUPERADMIN/BUSINESS_OWNER/AUDITOR).
- `POST /api/v1/kyc/applications/{id}/review`
  - Marks `UNDER_REVIEW`, `APPROVED`, or `REJECTED` with reviewer notes.
- `POST /api/v1/kyc/applications/{id}/approve`
  - Approves and auto-creates user with RBAC role and trading mode.
- `POST /api/v1/kyc/applications/{id}/reject`
  - Rejects with reviewer notes.

## Automatic user creation
When approved:
- Creates a user if the email does not already exist.
- Applies:
  - `role` = `desired_role`
  - `trading_mode` = `requested_trading_mode`
  - `risk_tolerance` = `risk_tolerance`
- Returns a **temporary password** for secure hand-off.

## Security controls
- Role-gated access for review/approval.
- Review metadata persisted (reviewer + notes + timestamp).
- Application data stored server-side only.
- Recommended: encrypt PII at rest and integrate a dedicated KYC provider in production.

## UI locations
- Public submission: `/kyc`
- Admin review: `/kyc` (visible to SUPERADMIN/BUSINESS_OWNER)

