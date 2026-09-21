# CLAUDE.md

> **How to use this file (read this first, every session):**
> This is the single source of truth for a new Claude session on the AMS Platform project. Read top to bottom before touching code. Section order is deliberate: **what this is → what exists right now → what's next → rules → history**. If you're picking up mid-conversation and something here contradicts what Ritam just told you, his live message wins — but update this file to match before the session ends, or the next Claude inherits the same confusion.

---

## 1. What This Project Is

**AMS Platform** — an internal Enterprise Asset Management System for a company called **Logarhythm**, being converted from a portfolio/demo project into a real production system. It tracks employees, IT assets, hardware components, software licenses, assignments/returns/transfers, repairs, warranties, audit history, dashboards, reports, notifications, documents, and bulk CSV import — end to end, with a full-history, audit-first design.

**Tech stack:**
- Backend: FastAPI + SQLAlchemy 2.0 (`Mapped`/`mapped_column`) + Alembic + PostgreSQL 16
- Frontend: Next.js 14 (App Router) + TypeScript + Tailwind CSS (semantic tokens only — see §5)
- Orchestration: Docker Compose

**Design philosophy:** audit-first, history-preserving (nothing mutable is ever overwritten in place — old row closed, new row opened), RBAC enforced server-side on every endpoint, semantic color tokens throughout the frontend so dark mode works for free.

**Working pattern:** Ritam implements all code changes himself — Claude drafts diffs/snippets with reasoning, doesn't apply them directly unless explicitly asked. He runs two parallel Claude sessions (one planning, one implementation review) and cross-references both. This file is what keeps a third/new session aligned with either.

---

## 2. Current State — What Exists Right Now

*(Read this as present-tense fact about the codebase, not a changelog. If you need to know how it got this way, see §6 History.)*

### Core platform (pre-IAM-upgrade, stable)
All of Employees, Assets, Components, Software/Licenses, Assignments, Returns, Transfers, Repairs, Warranties, Audit Logs, Dashboards, Reports (3 of ~11 types), Notifications (in-app + optional email), Documents, bulk CSV import, and the Device Agent API groundwork are built and tested. Full detail in `README.md` — not duplicated here since it doesn't change during the IAM work.

### Authentication & IAM (active work area)

**Login (local):**
- Email + password, Argon2-hashed. `POST /auth/login`.
- **Account lockout**: after `MAX_FAILED_LOGIN_ATTEMPTS` (default 5) bad passwords, account locks for `LOCKOUT_DURATION_MINUTES` (default 15). Cleared on successful login or password reset.
- **hCaptcha**: optional, gated by `HCAPTCHA_ENABLED` (default false — no keys needed for local dev/tests). When enabled, `captcha_service.py` verifies server-side against hCaptcha's API and **fails closed** (a verification error rejects the login, doesn't let it through). Frontend widget lives in `login/page.tsx`, gated by `NEXT_PUBLIC_HCAPTCHA_SITE_KEY`.
- **Password policy**: enforced in `core/password_policy.py`, applied via Pydantic validators on every password-accepting schema (`UserCreate`, `ResetPasswordRequest`, `ChangePasswordRequest`). Min 10 chars, upper/lower/digit/special, common-password blocklist.
- Login responses are deliberately generic — never leak whether an email exists, its auth provider, or its lock state.

**Login (SSO):**
- Microsoft Entra ID via Authorization Code Flow + PKCE, `msal` library, backend-only token exchange (frontend never sees a Microsoft token). `GET /auth/sso/login` → authorization URL; `GET /auth/sso/callback` → 302 redirect to frontend with `?token=` or `?sso_error=`.
- No self-signup: SSO only succeeds against an Admin-pre-created User row, matched by email, linked to the Entra identity on first login.
- Tenant enforcement via `ENTRA_ALLOWED_TENANT_ID`; identity key is `entra_object_id` + `entra_tenant_id` composite (Microsoft's `oid` is tenant-scoped, not global).
- Disabled by default (`ENTRA_ENABLED=false`).

**Session / token lifecycle:**
- Access tokens are JWTs carrying a `jti` claim. `create_access_token()` returns a **3-tuple** `(token, jti, expire)` — not a bare string. Every issuance site (`api/auth.py`, `api/sso.py`) records the jti in `issued_tokens` at mint time.
- `POST /auth/logout` revokes the *current* token immediately (inserts its jti into `revoked_tokens`).
- **Mass revocation** (`token_service.revoke_all_for_user`) kills every *other* outstanding token for a user in one shot. Wired into: (a) `PATCH /users/{id}/status` whenever status moves away from ACTIVE, and (b) self-service password change (revokes other sessions, deliberately leaves the current request's own token alone so the user isn't logged out mid-action).
- `get_current_user` checks `revoked_tokens` on every request via the token's `jti`.
- No refresh tokens exist — mass revocation was chosen instead as a smaller, self-contained fix for "disabled user should lose access immediately," not a full refresh-token architecture.

**Password reset (forgotten password, unauthenticated):**
- `POST /auth/forgot-password` — always returns a generic 202, regardless of whether the email exists, is Microsoft-provider, or is disabled. `POST /auth/reset-password` — single-use, SHA-256-hashed token, 30-minute expiry, clears any lockout on success.

**Change password (logged in):**
- `POST /users/me/change-password` — requires current password; rejects MICROSOFT-provider accounts (nothing local to change); triggers mass revocation of other sessions.

**User status:**
- `UserStatus`: ACTIVE, DISABLED, SUSPENDED, PENDING. All four are enforced in `get_current_user` (non-ACTIVE = rejected), with **status-specific 403 messages** since Phase 7. `PATCH /users/{id}/status` logs a matching audit action per status (`USER_DISABLED`, `USER_SUSPENDED`, `USER_SET_PENDING`, `USER_ENABLED`) and now also mass-revokes sessions (see above).
- **PENDING is schema-only** — nothing currently sets it, and there's no invite/activation email flow. Admin-created users go straight to ACTIVE.

**Groups:**
- `Group` model + full CRUD at `/groups` (Admin creates, any staff role lists). `Employee.group_id` is wired through `EmployeeCreate`/`Update`/`Read` schemas (existed on the model since early IAM work, was unused until this was closed).

**Organization settings:**
- `/organization` — singleton `organization_settings` table. GET open to any authenticated user (branding needs to render everywhere), PATCH Admin-only.
- **Frontend not yet wired to this** — `BrandContext.tsx` and the Settings page's email-notification toggle still read/write `localStorage` only. This is a known, explicit gap (see §3), not an oversight.

### Database migration chain
Current head: **`f1g2h3i4j5k6`**. Full chain: `905d66c2055a` (initial schema) → `a1b2c3d4e5f6` (groups, password reset tokens, user auth-provider/lockout fields) → `b2c3d4e5f6a7` (organization_settings) → `c3d4e5f6a7b8` (revoked_tokens) → `d4e5f6a7b8c9` (issued_tokens) → `f1g2h3i4j5k6` (Phase A: org_hierarchy). **Never branch off an earlier revision — always chain off the current head.**

---

## 3. What's Next — The Plan

*(This section includes items discussed but not yet built or confirmed in detail. Treat unconfirmed items as "the current best plan," not as settled spec — confirm specifics with Ritam before implementing if anything here seems ambiguous.)*

### Immediate next: Group B — remaining brute-force defenses
- **IP-based rate limiting on `/auth/login`.** CAPTCHA (per-request bot defense) and account lockout (per-account defense) are both done; this is the third leg — stopping a distributed attack that sprays many accounts from one IP, which per-account lockout alone doesn't catch. **Open question, not yet decided:** rate limit by IP alone, or IP+email combined? Ask Ritam if it isn't resolved by the time you read this.

### Scoped but not started
- **PENDING/invite flow** — real onboarding UX: Admin creates a user as PENDING, an activation email goes out, user sets their own password to activate. Bigger than a quick patch — email templates + activation UI + a new token type (likely reusing the password-reset-token pattern).
- **Per-attempt failed-login audit trail** — currently, a failed login only produces an audit entry at the moment lockout actually triggers, not for every individual bad attempt. Worth doing only if Ritam wants forensic-grade brute-force logs; otherwise explicitly deprioritized as diminishing returns.
- **MFA/2FA** — explicitly out of scope until separately planned. Biggest lift of anything on this list (new DB fields, TOTP or SMS provider integration, recovery codes, frontend enrollment/verification flow). Do not start this without a dedicated scoping conversation.
- **Frontend `/organization` wiring** — `BrandContext.tsx` and the Settings page need to call the real `/organization` endpoint instead of `localStorage`. Held back because it touches a UX decision Ritam hasn't made: should non-Admins see the branding form read-only, or hidden entirely? Ask before building.

### Explicitly rejected / deferred by design (don't re-propose without new information)
- **Refresh tokens** — considered as an alternative to mass revocation for the mid-session-kill problem; mass revocation was chosen instead as smaller and self-contained. Only reconsider if Ritam wants shorter-lived access tokens for an unrelated reason.
- **Rewriting `revoked_token_repository.revoke_all_for_user` as a no-op stub** — it was a stub through Phase 9, but is now a real implementation via `issued_tokens`. If you see old code or notes calling it a stub, they're outdated — check the actual file.

### Outside IAM (from the original 17-phase roadmap, not detailed here)
Reports beyond the 3 built types, S3/GCS document storage (currently local disk), and any roadmap phases beyond what's IAM-related. **If you need these, ask Ritam for the specifics — this file's authors don't have the full original 17-phase document in hand; the IAM work above was scoped phase-by-phase in conversation, not from that source doc.**

---

## 4. Key Commands

- `docker compose up` — full stack
- `docker compose exec backend python -m app.scripts.seed_admin` — bootstrap admin (`admin@ams-platform.com` / `ChangeMe123!`). **This default password no longer satisfies the password policy (§2) — change it immediately via `/users/me/change-password` after first login.**
- `cd backend && python -m pytest` — **never bare `pytest`** (Windows path resolution issue)
- Windows venv: `venv\Scripts\activate.bat` — not the PowerShell activation script
- Local (non-Docker) backend needs its own `backend/.env` pointing at `localhost:5432`, separate from the root `.env` Docker Compose uses
- To enable hCaptcha locally: register at https://dashboard.hcaptcha.com, set `HCAPTCHA_ENABLED=true` + `HCAPTCHA_SECRET_KEY` (backend) + `NEXT_PUBLIC_HCAPTCHA_SITE_KEY` (frontend)

---

## 5. Coding Style & Architecture Rules

*(With alternatives, not just "never" — a new Claude should know what to do instead, not just what to avoid.)*

- **Layering is strict**: `api/` (thin routers, no business logic) → `services/` (business logic + audit calls) → `repositories/` (raw queries only, no business logic). Don't blur these boundaries.
- Every mutating service call ends with `audit_service.log_action(...)` in the **same transaction** as the change itself — never a separate commit.
- RBAC via `require_role`/`require_self_or_role` in `api/deps.py` on every protected route. Always enforce server-side — frontend hiding a button is never sufficient on its own.
- **History-preserving pattern** for anything mutable-but-auditable: close the old row (status flip + timestamp) and insert a new row, never overwrite in place. Reference implementation: `component_service.replace_component`.
- Security-sensitive tokens are hashed before storage where the raw value doesn't need to be recoverable (password reset tokens, device agent tokens — SHA-256). JWTs themselves are bearer tokens by design and aren't hashed, but their `jti` is tracked (not the full token) in `issued_tokens`/`revoked_tokens`.
- Password validation lives in **one place**: `core/password_policy.py`. New password-accepting endpoints should import `validate_password_strength` into their schema, not redefine rules.
- Security features **fail closed, not open** — see `captcha_service.py`: a verification error rejects the request rather than silently letting it through. Apply the same principle to any new security check.
- `create_access_token()` returns `(token, jti, expire)` — a 3-tuple. Any new code that mints an access token must record the jti via `issued_token_repository.create`, or that token becomes invisible to mass revocation.
- Frontend: **Tailwind semantic tokens only** (`text-ink`, `bg-card`, `bg-surface`, `border-border`, `bg-primary`) — never raw hex or one-off colors. This is what makes dark mode work app-wide with zero per-component changes.
- Migrations always chain off the current `down_revision` (see §2 for current head) — never create a second head.
- Don't assume a throwaway test password like `"wrong"` or `"whatever"` will pass schema validation — anything going through `UserCreate`/`ResetPasswordRequest`/`ChangePasswordRequest` needs a policy-compliant string (e.g. `Str0ng!Passw0rd99`). Existing fixtures (`AdminPass123!` etc.) already comply.
- Don't query Entra identity by `oid` alone — pair with `entra_tenant_id` (tenant-scoped, not global).
- Don't leak account-state info from public auth endpoints (`/auth/login`, `/auth/forgot-password`) — responses stay generic regardless of account existence/provider/lock state. Status-specific detail only appears post-authentication.
- Don't assume CAPTCHA is active in tests or local dev — `HCAPTCHA_ENABLED` defaults false; tests exercising it explicitly monkeypatch it on.
- Don't set `AssetStatus.ASSIGNED`/`UNDER_REPAIR` directly — route through `assignment_service`/`repair_service`.
- Don't assume Ritam wants you editing files directly — give diffs/snippets + reasoning unless he explicitly asks you to write to disk.
- If Ritam pastes a summary from his other Claude session, treat it as authoritative current state — don't try to re-derive it from code alone.

---

## 6. Project Structure

- `backend/app/api/` — routers
- `backend/app/services/` — business logic
- `backend/app/repositories/` — queries
- `backend/app/models/` — ORM models (register new ones in `models/__init__.py`)
- `backend/alembic/versions/` — chained migrations
- `frontend/src/app/(app)/` — authenticated pages
- `frontend/src/services/` — one file per API resource
- `frontend/src/types/index.ts` — mirrors backend schemas; update both together

---

## 7. History (Appendix — for archaeology, not orientation)

*(Skim only if you need to understand why something is the way it is. §2/§3 are sufficient to start working.)*

- IAM Phase 1–2: auth audit; `Group`/`PasswordResetToken` models; `User` provider/lockout fields; migration `a1b2c3d4e5f6`.
- IAM Phase 3: Entra SSO built (msal, PKCE, backend-only exchange, tenant enforcement). Earlier session notes had called this "upcoming" — code review confirmed it was actually complete; flagged and resolved as a discrepancy.
- IAM Phase 4: password reset flow.
- IAM Phase 5: account lockout.
- IAM Phase 6: Group CRUD + `Employee.group_id` schema exposure.
- IAM Phase 7: status-specific 403 messages + matching audit actions for SUSPENDED/PENDING.
- IAM Phase 8: `/organization` endpoint, migration `b2c3d4e5f6a7`.
- Auth gap review: enumerated 7 items (token lifecycle, password strength, change-password, PENDING flow, failed-login audit, IP throttling, MFA). Ritam shared a reference login UI (Microsoft sign-in + CAPTCHA), which confirmed CAPTCHA + rate limiting as "Group B."
- IAM Phase 9: password strength policy, `/users/me/change-password`, `/auth/logout` + JWT denylist, migration `c3d4e5f6a7b8`. Mid-session revocation flagged as still-open at this point.
- IAM Phase 10: mass session revocation (`issued_tokens`, migration `d4e5f6a7b8c9`) + hCaptcha on login. `create_access_token`'s return signature changed to a 3-tuple as part of this — a breaking change to an existing function, called out explicitly since it's easy to miss.
- This file itself was restructured from a pure changelog format (which left a new session with no map of current state or forward plan) into the current state/plan/rules/history structure, per Ritam's feedback that the old version wasn't usable for onboarding a fresh Claude session.
- Phase A (Org Hierarchy): Replaced flat Department/Location with recursive `OrgUnit` tree structure (migration `f1g2h3i4j5k6`), built `OrgUnitPicker` and Admin UI.
- Phase B (Asset & Software Taxonomy): Added `category` to AssetType, added `SoftwareCategory` lookup table, repointed Asset locations to `org_units.id`.
- Phase C (Lifecycle Fields): Added `asset_tag` to Asset, reused Document for PO/Invoice, added `ServiceContract` model, depreciation fields (`depreciation_method`, `useful_life_months`), added `AssetDisposal` workflow and reports.
- Phase D (License Management): Added `purchase_cost` to License, enabled device-based assignment by adding `asset_id` to `SoftwareAssignment` (mutually exclusive with `employee_id`), added secure `LICENSE_KEY_VIEWED` key reveal flow.