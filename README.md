# AMS Platform — Enterprise Asset Management System

Full-stack asset lifecycle management: FastAPI + PostgreSQL backend, JWT
auth with role-based access control (Admin / HR / IT Support / Employee),
and complete history-preserving tracking of employees, assets, components,
software licenses, assignments, returns, transfers, repairs, and
warranties.

## Status: all 21 backend phases complete and tested

Every phase below was built, then verified against a **live PostgreSQL 16
instance** with real HTTP requests (not just unit tests in isolation) —
this caught several real bugs along the way, documented inline in code
comments where they were fixed:

1. ✅ Project setup
2. ✅ Database schema — 23 tables, history-preserving design throughout
3. ✅ Alembic migrations — verified full upgrade → downgrade → upgrade cycle
4. ✅ Authentication — Argon2 + JWT, admin-seeded bootstrap (users can't self-register)
5. ✅ RBAC — enforced server-side on every endpoint via `require_role`/`require_self_or_role`
6. ✅ Employee management
7. ✅ Asset management — manual status changes blocked from setting ASSIGNED/UNDER_REPAIR directly
8. ✅ Components — replacement preserves full history, never overwrites
9. ✅ Software & licenses — seat limits enforced, keys never exposed raw
10. ✅ Assignments — multi-asset handover transactions
11. ✅ Returns & transfers — condition-based asset routing, history preserved on both sides
12. ✅ Repair management — full status-history log
13. ✅ Warranty — status computed from dates, never stored/stale
14. ✅ Audit logs — append-only, admin-only read API
15. ✅ Dashboards — per-role aggregate endpoints
16. ✅ Reports — CSV export (3 representative reports; rest follow the same pattern)
17. ✅ Notifications — in-app **and email**, wired into assignment/repair workflows
18. ✅ Documents — upload/download with content-type allowlist and size limit
19. ✅ Testing — 35 pytest tests covering the business rules in spec section 50, all passing
20. ✅ Dockerization — healthchecks, auto-migration entrypoint, `.dockerignore`s
21. ✅ Future Asset Agent API groundwork — register/heartbeat/inventory/software/config stubs
22. ✅ Bulk CSV import — employees and assets, per-row failure isolation
23. ✅ Audit-log viewer UI — Admin-only, entity filters, before/after diff view

**Known extension points** (explicitly scoped out or simplified, not oversights):
- Reports: 3 of section 36's ~11 report types are implemented; the rest are the same query→CSV pattern.
- Documents: local disk storage; the swap point is isolated (`document_service.py`) for S3/GCS later.
- Email: real SMTP delivery (stdlib `smtplib`), disabled by default (`EMAIL_ENABLED=false`) so a deployment with no mail server configured just logs and continues rather than failing the request that triggered it. Verified end-to-end in this session using a local SMTP debug server.
- The Windows Asset Agent itself is explicitly out of scope per the spec — only the platform-side API groundwork exists.
- Test isolation uses per-test SAVEPOINT rollback; running the suite resets local dev data (re-run `python -m app.scripts.seed_admin` after).

**Two more real bugs found and fixed this round** (same pattern as before — found by actually running the thing, not by reading the code):
- The app had **no logging configuration** anywhere — `logger.info(...)`/`logger.exception(...)` calls throughout the codebase (including the new email service's "skipped, not configured" message) were being silently swallowed, since nothing attached a handler to Python's root logger and uvicorn only configures its own named loggers. Fixed with `app/core/logging_config.py`, called once at startup.
- Creating a duplicate-named row in any reference/lookup table (departments, locations, asset types, component types, vendors) threw a raw unhandled `IntegrityError` — a 500 with a stack trace — instead of a clean error. Fixed to return 409 with a readable message.

## Frontend: Next.js app (login, dashboards, employees, assets, assignments, repairs)

A working App Router frontend covering the core operational flows:

- **Auth**: login, JWT stored client-side, auto-redirect on 401, role-aware sidebar nav (an EMPLOYEE never even sees links to screens they're not permitted to use — the backend enforces this either way).
- **Dashboards**: role-specific panels (Admin/IT/HR/self), matching the four dashboards in section 34.
- **Employees**: list + create (Admin/HR), detail page with profile, assigned assets, assigned software, employment-status changes, and the exit checklist (section 24).
- **Assets**: list with inventory-summary counts and search, register (IT/Admin), detail page with Overview/Hardware(components)/Repair history/Warranty sections (section 30) and a guarded status-change control that — matching the backend — can't set ASSIGNED or UNDER_REPAIR directly.
- **Assignments**: multi-asset handover flow (select an employee + any number of AVAILABLE assets in one transaction).
- **Repairs**: ticket list, status-history modal driven off the same state machine as the backend; employees can report an issue against their own assigned assets from their dashboard.
- **Reusable components** (section 43): DataTable (with the app's one signature device — a left-edge color stripe reflecting lifecycle status), StatusBadge, Modal, ConfirmationDialog, StatCard, Sidebar.

Design: IBM Plex Sans (UI) + IBM Plex Mono (asset/employee/ticket codes — a deliberate nod to stamped asset-tag serials), a restrained ink/indigo palette rather than default SaaS-indigo, `prefers-reduced-motion` respected, visible focus rings.

**Verified this session**: clean `tsc --noEmit`, a full production `next build` (10/10 routes, confirmed via a scratch copy with fonts swapped to system fonts — `next/font/google` itself needs network access this sandbox doesn't have to `fonts.googleapis.com`, which will work normally wherever this actually gets deployed/built), CORS confirmed live between the two servers, and every new endpoint the UI calls hit live against the real backend with real data.

**Known trade-off**: `npm audit` reports 2 remaining high-severity advisories, both inside Next.js's own bundled toolchain (a Server Actions endpoint-disclosure issue this app doesn't use, and PostCSS source-map parsing this app doesn't invoke on untrusted input) — not reachable through this app's actual code paths. Fully clearing them requires jumping to Next 16, a breaking major-version change not verified in this session; flagged here rather than forced through untested.

**Not yet built**: report-download buttons for the ~8 remaining report types in section 36 (the pattern is established — see `report_service.py` — just not every type is written), and S3/GCS document storage (local disk today, isolated behind one module so it's a contained swap). Everything else from the original spec's core workflows — including all three gaps called out in the previous pass (bulk import, audit-log viewer, email) — is now built and verified end-to-end against the live backend:

- **Software & licenses** (`/software`): browse the catalog, add software/licenses, and assign a license seat to an employee directly from the license table (grayed out once seats run out).
- **Transfers & returns**: the asset detail page's "Assignment" section shows who currently holds it (derived live from the backend, not stored) with "Process return" (GOOD/DAMAGED/MISSING, routes the asset to the right status exactly like the backend does) and "Transfer" (pick a new employee) actions.
- **Documents**: upload/list/download attached to the asset detail page, gated to Admin/HR/IT per the backend's actual permission set (not just IT/Admin).
- **Notifications**: a bell in the header polls every 30s, shows unread count, mark-as-read — and, if `EMAIL_ENABLED=true` is configured server-side, the same trigger sends a real email.
- **Reports** (`/reports`): one-click CSV download for the three implemented report types.
- **CSV import**: an "Import CSV" button on both the Employees and Assets list pages, using a shared modal that shows a per-row created/skipped/error summary after upload.
- **Audit log** (`/audit-logs`, Admin only): filterable by entity type/ID, with an expandable before/after diff panel per entry.

## Running it

```bash
cp .env.example .env        # then edit JWT_SECRET_KEY etc.
docker compose up --build
```

- Backend: http://localhost:8000 (docs at `/api/v1/docs`)
- Frontend: http://localhost:3000
- Postgres: localhost:5432

First run: the backend container runs migrations automatically, but you
still need to seed the first Admin account (no one can log in otherwise):

```bash
docker compose exec backend python -m app.scripts.seed_admin
```

Default login after seeding: `admin@ams-platform.com` / `ChangeMe123!` —
change this immediately in a real deployment.

Email notifications are off by default (`EMAIL_ENABLED=false` in
`.env.example`) — the app works fully without them. To enable real email
delivery, set `EMAIL_ENABLED=true` and fill in `SMTP_HOST`/`SMTP_PORT`/
`SMTP_USERNAME`/`SMTP_PASSWORD` for your mail provider.

To run the backend test suite locally (needs a reachable Postgres — the
suite wipes and recreates the schema each run):

```bash
cd backend
pip install -r requirements.txt
pytest
```

## Roadmap (per the spec)

1. ✅ Project setup
2. Database schema (Users, Employees, Assets, Components, Software,
   Licenses, Assignments, Repairs, Warranties, Audit Logs, ...)
3. Alembic migrations
4. Authentication (JWT + Argon2)
5. Role-based access control
6. Employee management
7. Asset management
8. Components (with replacement history)
9. Software & licenses
10. Assignments (single + multi-item handovers)
11. Returns & transfers
12. Repair management
13. Warranty tracking
14. Audit logs
15. Dashboards (Admin / IT / HR / Employee)
16. Reports (CSV/Excel/PDF export)
17. Notifications
18. Documents
19. Testing
20. Dockerization (base already in place, hardened here)
21. Future Asset Agent API groundwork (register/heartbeat/inventory endpoints
    — no actual agent yet)

Each phase followed the spec's development rule: explain what's being
built and which tables/endpoints/screens/business rules it touches, then
implement it without breaking what's already working. The frontend
(Next.js screens beyond the Phase 1 health-check landing page) is the
next piece of work.
