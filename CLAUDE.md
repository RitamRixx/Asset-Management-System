# CLAUDE.md

## Current Status
**Active phase:** IAM upgrade — Phases 1–8 complete per code + this session.
**Confirmed done:**
- Phase 1–2: auth audit, Group/PasswordResetToken models, User provider/lockout fields, migration `a1b2c3d4e5f6`.
- Phase 3: Entra SSO (msal, PKCE, backend-only token exchange, tenant enforcement) — `entra_service.py`, `api/sso.py`, frontend login button + `/sso/callback`, `test_sso.py`.
- Phase 4: password reset flow — `password_reset_service.py`, `/auth/forgot-password`, `/auth/reset-password`. Generic responses regardless of account state; single-use SHA-256-hashed tokens, 30-min expiry.
- Phase 5: local-auth lockout — `auth_service.authenticate_user` increments `failed_login_count`, sets `locked_until` after `MAX_FAILED_LOGIN_ATTEMPTS` (default 5, 15 min lockout). Cleared on success or password reset. MICROSOFT-provider accounts unaffected.
- Phase 6: Group CRUD (`/groups`) + `Employee.group_id` finally exposed in schemas (existed on the model since Phase 2, unused until now).
- Phase 7: status-specific 403 messages for SUSPENDED/PENDING + matching audit action names (`USER_SUSPENDED`, `USER_SET_PENDING`) on `PATCH /users/{id}/status`.
- Phase 8: `/organization` endpoint — singleton `organization_settings` table (migration `b2c3d4e5f6a7`), GET open to all authenticated users, PATCH Admin-only.

**Known follow-up, not yet done:** frontend `BrandContext.tsx` / `settings/page.tsx` still read/write localStorage instead of calling `/api/v1/organization` — flagged in Phase 8 above pending a UX decision (read-only vs hidden branding form for non-Admins). Also unaddressed: MFA, refresh-token rotation, per-permission ACLs, SCIM — none of these were confirmed as in-scope; ask before building.

## Changelog
<!-- Append 2-4 line entries here after each phase. Don't rewrite old entries. -->
- **2026-09-02**: CLAUDE.md created. Flagged Entra SSO status discrepancy vs. prior session notes.
- **2026-09-02**: Phases 4–8 designed and drafted in one session (password reset, lockout, Group CRUD, SUSPENDED/PENDING wiring, `/organization`). Not yet applied to the repo by Ritam. Frontend org-settings wiring intentionally left as a follow-up.

---

## Project
AMS Platform — Enterprise Asset Management System for Logarhythm. Tracks
employees, assets, components, software/licenses, assignments, repairs,
warranties, and audit history end-to-end.

## Tech Stack
- Backend: FastAPI + SQLAlchemy 2.0 (Mapped/mapped_column) + Alembic + PostgreSQL
- Frontend: Next.js (App Router) + TypeScript + Tailwind (semantic tokens only, no raw hex)
- Auth: JWT + Argon2 (local, with lockout) + Microsoft Entra OIDC/PKCE via `msal` (SSO)
- Orchestration: Docker Compose

## Key Commands
- `docker compose up` — full stack
- `docker compose exec backend python -m app.scripts.seed_admin` — bootstrap admin (`admin@ams-platform.com` / `ChangeMe123!`), idempotent
- `cd backend && python -m pytest` — **never bare `pytest`** (Windows path issue)
- Windows venv: `venv\Scripts\activate.bat`, not the PowerShell script
- Local (non-Docker) backend needs its own `backend/.env` pointing at `localhost:5432`

## Coding Style & Architecture
- Layering is strict: `api/` (thin routers) → `services/` (business logic + audit calls) → `repositories/` (raw queries only). Don't blur these.
- Every mutating service call ends with `audit_service.log_action(...)` in the same transaction/commit as the change itself.
- RBAC via `require_role`/`require_self_or_role` in `api/deps.py` on every protected route — always enforce server-side even if the frontend already hides the UI.
- History-preserving pattern for anything mutable-but-auditable (components, assignments): close old row + insert new row, never overwrite in place. See `component_service.replace_component` as the reference implementation.
- Security-sensitive tokens (device agent, password reset) are never stored raw — only a SHA-256 hash, with the raw value handed to the user exactly once.
- Frontend: Tailwind semantic tokens only (`text-ink`, `bg-card`, `border-border`) — this is what makes dark mode work without per-component changes.
- Migrations chain off `down_revision` — never create a second head casually. Current head: `b2c3d4e5f6a7`.

## Project Structure
- `backend/app/api/` — routers
- `backend/app/services/` — business logic
- `backend/app/repositories/` — queries
- `backend/app/models/` — ORM models (register new ones in `models/__init__.py`)
- `backend/alembic/versions/` — chained migrations
- `frontend/src/app/(app)/` — authenticated pages
- `frontend/src/services/` — one file per API resource
- `frontend/src/types/index.ts` — mirrors backend schemas; update both together

## Rules (with alternatives, not just "never")
- Don't set `AssetStatus.ASSIGNED`/`UNDER_REPAIR` directly — route through `assignment_service`/`repair_service` instead.
- Don't query Entra identity by `oid` alone — pair with `entra_tenant_id` (`oid` is tenant-scoped, not global).
- Don't leak account-state info from auth-adjacent public endpoints — `/auth/login`, `/auth/forgot-password` all return generic responses regardless of whether the account exists, its provider, or its lock state. Status-specific messages (SUSPENDED/PENDING) only appear *post*-auth in `get_current_user`.
- Don't assume I want you editing files directly — give me the diff/snippet + reasoning unless I explicitly ask you to write it.
- If I paste a summary from my other Claude session, treat it as authoritative current state, not something to re-derive from code alone.