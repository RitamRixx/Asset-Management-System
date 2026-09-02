# CLAUDE.md

## Current Status
**Active phase:** IAM upgrade — verify actual state before continuing (see note below).
**Confirmed done (from code):**
- Phase 1–2: auth audit, Group/PasswordResetToken models, User provider/lockout fields, migration `a1b2c3d4e5f6` applied.
- Entra SSO (msal, PKCE, backend-only token exchange, tenant enforcement) is implemented: `entra_service.py`, `api/sso.py`, frontend login button + `/sso/callback`, `test_sso.py` covers login/callback/tenant-rejection/invalid-state.
**Discrepancy to resolve:** prior notes said SSO was "upcoming" — code shows it built and tested. Confirm with Ritam which is accurate before planning next phase.
**Next up:** TBD — pick from remaining roadmap (backend `/organization` endpoint for branding/notifications, or continue the 17-phase IAM roadmap).

## Changelog
<!-- Append 2-4 line entries here after each phase. Don't rewrite old entries. -->
- **2026-09-02**: CLAUDE.md created. Flagged Entra SSO status discrepancy vs. prior session notes.

---

## Project
AMS Platform — Enterprise Asset Management System for Logarhythm. Tracks
employees, assets, components, software/licenses, assignments, repairs,
warranties, and audit history end-to-end.

## Tech Stack
- Backend: FastAPI + SQLAlchemy 2.0 (Mapped/mapped_column) + Alembic + PostgreSQL
- Frontend: Next.js (App Router) + TypeScript + Tailwind (semantic tokens only, no raw hex)
- Auth: JWT + Argon2 (local) + Microsoft Entra OIDC/PKCE via `msal` (SSO)
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
- Don't assume I want you editing files directly — give me the diff/snippet + reasoning unless I explicitly ask you to write it.
- If I paste a summary from my other Claude session, treat it as authoritative current state, not something to re-derive from code alone.