# CLAUDE.md

## Current Status
**Active phase:** IAM upgrade — Phase 4 (local auth hardening) just completed, pending Ritam's manual implementation + test run.
**Confirmed done (from code):**
- Phase 1–2: auth audit, Group/PasswordResetToken models, User provider/lockout fields, migration `a1b2c3d4e5f6` applied.
- Phase 3: Entra SSO (msal, PKCE, backend-only token exchange, tenant enforcement) — `entra_service.py`, `api/sso.py`, frontend login button + `/sso/callback`, `test_sso.py` covers login/callback/tenant-rejection/invalid-state.
- Phase 4 (specified, not yet applied to repo): account lockout enforcement wired into `auth_service.authenticate_user` using existing `failed_login_count`/`locked_until` columns; forgot/reset-password flow (`password_reset_service.py`, two new `/auth/*` endpoints) using existing `PasswordResetToken` table. No new migration — Phase 2's schema already covers this. Tests: `test_account_lockout.py`, `test_password_reset.py`.
**Next up:** TBD — once Phase 4 is applied and tests pass, pick from: backend `/organization` endpoint for branding/notifications, frontend forgot/reset-password pages (backend now supports them), or continuing further down the 17-phase IAM roadmap.

## Changelog
<!-- Append 2-4 line entries here after each phase. Don't rewrite old entries. -->
- **2026-09-02**: CLAUDE.md created. Flagged Entra SSO status discrepancy vs. prior session notes.
- **2026-09-02**: Phase 4 (account lockout + password reset) specified — code snippets given for `auth_service`, new `password_reset_service`, two new `/auth/*` endpoints, two new test files. Not yet applied to repo.

---

## Project
AMS Platform — Enterprise Asset Management System for Logarhythm. Tracks
employees, assets, components, software/licenses, assignments, repairs,
warranties, and audit history end-to-end.

## Tech Stack
- Backend: FastAPI + SQLAlchemy 2.0 (Mapped/mapped_column) + Alembic + PostgreSQL
- Frontend: Next.js (App Router) + TypeScript + Tailwind (semantic tokens only, no raw hex)
- Auth: JWT + Argon2 (local, with account lockout) + Microsoft Entra OIDC/PKCE via `msal` (SSO)
- Orchestration: Docker Compose

## Key Commands
- `docker compose up` — full stack
- `docker compose exec backend python -m app.scripts.seed_admin` — bootstrap admin (`admin@ams-platform.com` / `ChangeMe123!`), idempotent
- `cd backend && python -m pytest` — **never bare `pytest`** (Windows path issue)
- `cd backend && python -m pytest tests/test_account_lockout.py tests/test_password_reset.py -v` — Phase 4 tests only
- Windows venv: `venv\Scripts\activate.bat`, not the PowerShell script
- Local (non-Docker) backend needs its own `backend/.env` pointing at `localhost:5432`

## Coding Style & Architecture
- Layering is strict: `api/` (thin routers) → `services/` (business logic + audit calls) → `repositories/` (raw queries only). Don't blur these.
- Every mutating service call ends with `audit_service.log_action(...)` in the same transaction/commit as the change itself.
- RBAC via `require_role`/`require_self_or_role` in `api/deps.py` on every protected route — always enforce server-side even if the frontend already hides the UI.
- History-preserving pattern for anything mutable-but-auditable (components, assignments): close old row + insert new row, never overwrite in place. See `component_service.replace_component` as the reference implementation.
- Auth failure paths must never leak *why* they failed (unknown email vs. wrong password vs. locked vs. SSO-only account) — always collapse to one generic 401. See `auth_service.authenticate_user`.
- Frontend: Tailwind semantic tokens only (`text-ink`, `bg-card`, `border-border`) — this is what makes dark mode work without per-component changes.
- Migrations chain off `down_revision` — never create a second head casually.

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
- Don't store password reset or device-agent tokens raw — hash with SHA-256 and store only the hash (see `password_reset_service.py`, `agent_service.py`).
- Don't let `/auth/forgot-password` return different responses for known vs. unknown emails — always the same generic 202, to avoid enumeration.
- Don't assume I want you editing files directly — give me the diff/snippet + reasoning unless I explicitly ask you to write it.
- If I paste a summary from my other Claude session, treat it as authoritative current state, not something to re-derive from code alone.