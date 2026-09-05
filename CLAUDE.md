# CLAUDE.md

## Current Status
**Active phase:** IAM upgrade — Phases 1–9 complete (auth core, SSO, reset, lockout, groups, status wiring, org settings, self-service password/logout). See "Known follow-up" below before assuming logout is a full session-kill.

**Confirmed done:**
- Phase 1–2: auth audit, Group/PasswordResetToken models, User provider/lockout fields, migration `a1b2c3d4e5f6`.
- Phase 3: Entra SSO (msal, PKCE, backend-only token exchange, tenant enforcement).
- Phase 4: password reset flow — `/auth/forgot-password`, `/auth/reset-password`. Generic responses, single-use hashed tokens, 30-min expiry.
- Phase 5: local-auth lockout — `MAX_FAILED_LOGIN_ATTEMPTS` (default 5), `LOCKOUT_DURATION_MINUTES` (default 15). Cleared on success or reset.
- Phase 6: Group CRUD (`/groups`) + `Employee.group_id` exposed in schemas.
- Phase 7: status-specific 403 messages (SUSPENDED/PENDING) + matching audit actions.
- Phase 8: `/organization` endpoint — singleton table, migration `b2c3d4e5f6a7`.
- **Phase 9 (this session): password strength, self-service change-password, logout/token revocation.**
  - `core/password_policy.py` — min 10 chars, upper/lower/digit/special, common-password blocklist. Enforced via Pydantic `field_validator` on `UserCreate`, `ResetPasswordRequest`, and the new `ChangePasswordRequest` — one source of truth, three entry points.
  - `POST /users/me/change-password` — requires current password; rejects MICROSOFT-provider accounts (no local password to change).
  - `POST /auth/logout` + `revoked_tokens` table (migration `c3d4e5f6a7b8`) — access tokens now carry a `jti` claim; logout inserts it into a denylist checked on every `get_current_user` call.

**Known follow-up / explicit limitation:** logout only revokes the *specific token used to log out*. It does **not** solve "disabling a user should kill their live session immediately" — that needs either (a) tracking every issued `jti` per user so status changes can mass-revoke, or (b) short-lived access tokens + refresh tokens. Neither is built. `revoked_token_repository.revoke_all_for_user` exists as a documented stub, not a real implementation — don't wire it into `users.py`'s status-change endpoint assuming it works.

**Also still open (from prior session, unchanged):**
- CAPTCHA + IP-based rate limiting on `/auth/login` (Group B, not started) — matches the reference login screenshot Ritam shared.
- PENDING/invite email flow (schema-only, no real onboarding UX).
- Per-attempt failed-login audit trail (currently only logs at the lockout-trigger moment).
- MFA/2FA — not started, needs its own scoping pass.

## Changelog
<!-- Append 2-4 line entries here after each phase. Don't rewrite old entries. -->
- **2026-09-02**: CLAUDE.md created. Flagged Entra SSO status discrepancy vs. prior session notes.
- **2026-09-02**: Phases 4–8 designed and drafted in one session (password reset, lockout, Group CRUD, SUSPENDED/PENDING wiring, `/organization`). Frontend org-settings wiring left as follow-up.
- **2026-09-02**: Auth gap review — enumerated 7 items (token lifecycle, password strength, change-password, PENDING flow, failed-login audit, IP throttling, MFA). Ritam shared a reference login UI (Sign in w/ Microsoft + CAPTCHA) — confirmed CAPTCHA + rate limiting as "Group B," scoped separately from this batch.
- **2026-09-02**: Phase 9 built — password strength policy (shared across create/reset/change), `/users/me/change-password`, `/auth/logout` + JWT denylist (migration `c3d4e5f6a7b8`). Explicitly documented that logout ≠ mid-session force-revocation; that gap remains open pending a refresh-token or per-user-jti-tracking decision.

---

## Project
AMS Platform — Enterprise Asset Management System for Logarhythm. Tracks
employees, assets, components, software/licenses, assignments, repairs,
warranties, and audit history end-to-end.

## Tech Stack
- Backend: FastAPI + SQLAlchemy 2.0 (Mapped/mapped_column) + Alembic + PostgreSQL
- Frontend: Next.js (App Router) + TypeScript + Tailwind (semantic tokens only, no raw hex)
- Auth: JWT (now with `jti` + server-side revocation) + Argon2 (local, with lockout + strength policy) + Microsoft Entra OIDC/PKCE via `msal` (SSO)
- Orchestration: Docker Compose

## Key Commands
- `docker compose up` — full stack
- `docker compose exec backend python -m app.scripts.seed_admin` — bootstrap admin (`admin@ams-platform.com` / `ChangeMe123!` — **note: this default no longer satisfies the new password policy**, change it immediately after first login via `/users/me/change-password`)
- `cd backend && python -m pytest` — **never bare `pytest`** (Windows path issue)
- Windows venv: `venv\Scripts\activate.bat`, not the PowerShell script
- Local (non-Docker) backend needs its own `backend/.env` pointing at `localhost:5432`

## Coding Style & Architecture
- Layering is strict: `api/` (thin routers) → `services/` (business logic + audit calls) → `repositories/` (raw queries only). Don't blur these.
- Every mutating service call ends with `audit_service.log_action(...)` in the same transaction/commit as the change itself.
- RBAC via `require_role`/`require_self_or_role` in `api/deps.py` on every protected route — always enforce server-side even if the frontend already hides the UI.
- History-preserving pattern for anything mutable-but-auditable (components, assignments): close old row + insert new row, never overwrite in place. See `component_service.replace_component` as the reference implementation.
- Security-sensitive tokens (device agent, password reset, now revoked-token jtis) are never stored raw where avoidable — reset/device tokens are SHA-256 hashed; JWTs themselves aren't hashed (they're bearer tokens by design) but their `jti` is tracked, not the full token.
- Password validation lives in ONE place (`core/password_policy.py`) — if you add a new password-accepting endpoint, import `validate_password_strength` into its schema rather than re-deriving rules.
- Frontend: Tailwind semantic tokens only (`text-ink`, `bg-card`, `border-border`) — this is what makes dark mode work without per-component changes.
- Migrations chain off `down_revision` — never create a second head casually. Current head: `c3d4e5f6a7b8`.

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
- Don't leak account-state info from auth-adjacent public endpoints — `/auth/login`, `/auth/forgot-password` return generic responses regardless of account existence/provider/lock state. Status-specific messages only appear post-auth.
- Don't assume a test password like `"wrong"` or `"whatever"` will pass schema validation anymore — `UserCreate`/`ResetPasswordRequest`/`ChangePasswordRequest` all enforce `password_policy.py`. Use a compliant string (e.g. `Str0ng!Passw0rd99`) in new tests that go through those schemas; existing fixtures (`AdminPass123!` etc.) already comply.
- Don't assume `POST /auth/logout` protects against a disabled user's *existing* session — it only revokes the token used in that specific logout call. See "Known follow-up" above.
- Don't assume I want you editing files directly — give me the diff/snippet + reasoning unless I explicitly ask you to write it.
- If I paste a summary from my other Claude session, treat it as authoritative current state, not something to re-derive from code alone.