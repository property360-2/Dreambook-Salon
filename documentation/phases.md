# 02-development-phases.md

# 🚀 Development Phases — Salon Appointment & Inventory System

This document breaks the project into clear phases. Each phase contains goals, detailed tasks (backend / frontend / database / QA), acceptance criteria, and deliverables. Use these as standalone checklists for development sprints or to hand off to Codex/engineers.

---

## Phase 1 — Core Setup & Authentication (Foundation)

**Goal:** Create the project skeleton, user auth, and basic CRUD for users and services.

### Tasks

**Backend**

- Initialize Node.js + Express project.
- Configure Prisma and connect to database.
- Implement user model & auth (JWT + bcrypt).
- Create `users` CRUD APIs and role-based middleware.
- Add basic logging & error handling.

**Frontend**

- Scaffold React app (Create React App or Next.js).
- Implement auth pages: `/login`, `/register`.
- Basic layout + navbar with role-aware links.

**Database**

- Create initial Prisma schema for `User`, `Service`, and `Appointment` stubs.
- Run migrations and seed an admin user.

**DevOps / Tooling**

- Add ESLint, Prettier, and environment variable patterns (`.env.example`).
- Setup basic `npm` scripts: `dev`, `start`, `migrate`.

### API Endpoints (minimum)

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/users/me`
- `GET /api/services`
- `POST /api/services` (admin)

### Acceptance Criteria

- Users can register/login and receive JWT.
- Role middleware blocks protected routes for unauthorized roles.
- Admin seed user exists and can create services through API.
- Frontend login/registration flows work with backend.

### Deliverables

- `backend/` skeleton, `src/index.js`, prisma schema, migrations.
- `frontend/` skeleton with auth pages and protected-route example.

---

## Phase 2 — Services, Inventory & Linking (Core Data Model)

**Goal:** Implement service management and inventory model including the `ServiceInventory` linkage.

### Tasks

**Backend**

- Implement Inventory model and CRUD APIs.
- Implement ServiceInventory linking endpoints (attach/detach inventory to service).
- Validate quantities and enforce business rules on linking.

**Frontend**

- Admin UI: Services CRUD with a form to add required inventory items and quantities.
- Inventory management page: add/update stock, set threshold.

**Database**

- Extend Prisma schema with `Inventory` and `ServiceInventory`.
- Seed sample inventory items and example service with linked items.

**API Endpoints**

- `GET /api/inventory`
- `POST /api/inventory`
- `PUT /api/inventory/:id`
- `POST /api/services/:id/inventory` (link item + quantity)
- `DELETE /api/services/:id/inventory/:inventoryId`

### Acceptance Criteria

- Admin can create inventory items and link them to services with quantities.
- Validation prevents linking with negative quantities.
- Frontend displays linked items inside service detail.

### Deliverables

- Inventory CRUD API, admin pages to manage inventory and service-inventory links.
- Updated Prisma schema & seed data.

---

## Phase 3 — Appointment Booking, Overlap Prevention & Admin Blocking

**Goal:** Robust appointment creation with concurrency checks, admin blocking, and appointment cap logic.

### Tasks

**Backend**

- Implement `Appointment` model with `start_time`, `end_time`, `status`.
- Add endpoints to fetch available slots and create appointments.
- Implement overlap prevention and admin-configurable max concurrent appointment cap. Use DB transactions for atomic checks + creation.
- Add endpoints to set blocked dates/times and slot caps.

**Frontend**

- Booking form with date/time picker and service selector.
- Request available slots from backend and display them.
- Admin settings page to set `maxConcurrentAppointments` and blocked ranges.

**Database**

- Add `BlockedSlot` or `BlockedRange` model in Prisma.
- Ensure appointment times stored in UTC.

**API Endpoints**

- `GET /api/appointments/available?serviceId=&date=`
- `POST /api/appointments` (creates appointment after overlap check)
- `POST /api/settings/blocked` (admin)
- `PUT /api/settings/cap` (admin)

### Acceptance Criteria

- Backend correctly rejects overlapping bookings beyond capacity.
- Admin can block dates/times and bookings for those ranges are denied.
- Frontend shows available slots and prevents booking blocked times.

### Deliverables

- Appointment slot-checking logic, booking UI, admin blocking UI.

---

## Phase 4 — Inventory Automation on Completion & Race Conditions

**Goal:** When an appointment is completed, automatically decrement inventory safely and handle insufficient stock.

### Tasks

**Backend**

- Implement endpoint to mark appointment as `completed`.
- On completion, fetch linked `ServiceInventory` items and decrement stock inside a DB transaction.
- Handle insufficient stock behavior via config:
  - Option A: Prevent completion and return error
  - Option B (default): Allow completion but flag negative stock and generate alert/notification
- Create audit logs for inventory changes.

**Frontend**

- Admin / Staff UI to mark appointment status `in-progress`, `completed`, `no-show`.
- Notification component for low-stock alerts.

**Database**

- Add `InventoryLog` model for audit trails (`inventoryId`, `change`, `reason`, `performedBy`, `timestamp`).

**API Endpoints**

- `PUT /api/appointments/:id/complete`
- `GET /api/inventory/low-stock`

### Acceptance Criteria

- Inventory is updated atomically when appointment completion occurs, even under concurrent completions.
- Inventory logs exist for each deduction.
- Low-stock alerts appear when thresholds crossed.

### Deliverables

- Atomic inventory deduction implementation, UI controls for completion, audit logs.

---

## Phase 5 — Demo Payment Flow & Payment Model

**Goal:** Add a mock payment module (GCash/PayMaya/Onsite demo) and link it with appointments.

### Tasks

**Backend**

- Add `Payment` model to Prisma.
- Implement demo payment endpoints to create a mock transaction and update payment + appointment status.
- Optionally allow randomized success/failure for test scenarios, and deterministic test mode.

**Frontend**

- Checkout flow: choose payment method, redirect to demo payment page, confirm/cancel buttons.
- Show mock receipt and transaction id.

**Database**

- Add `Payment` relations and seed instructions for test cases.

**API Endpoints**

- `POST /api/payments/demo` (simulate)
- `GET /api/payments/:id`

### Acceptance Criteria

- Demo payment creates a `Payment` record with `transactionId`.
- Appointment `status` or `payment.status` updates to `paid` on success.
- Frontend displays mock receipt and updates booking status.

### Deliverables

- Demo payment UI, backend demo endpoints, test scripts for both success and failure flows.

---

## Phase 6 — Chatbot (Rule-based) & Lightweight Assistant

**Goal:** Provide an on-site chatbot with keyword-based rules to assist customers and reduce friction.

### Tasks

**Backend / Chatbot**

- Create `chatbot` module with configurable rules (keyword -> response).
- Expose `POST /api/chatbot/message` endpoint that returns replies.
- Provide admin UI to edit rules/responses.

**Frontend**

- Chat widget component, store chat logs in local storage and/or backend.
- Quick actions: “Book now”, “Show services”, “Contact admin”.

**Database**

- Add `ChatRule` model for admin-editable rules (pattern, reply, priority).

**API Endpoints**

- `GET /api/chatbot/rules` (admin)
- `POST /api/chatbot/message`

### Acceptance Criteria

- Chatbot responds to basic queries (services, pricing, booking steps).
- Admin can edit rules via UI and see effect immediately.

### Deliverables

- Chat widget, backend rule editor, sample rule set.

---

## Phase 7 — Analytics Dashboard & Reports

**Goal:** Implement admin analytics: revenue, bookings, popular services, stock usage.

### Tasks

**Backend**

- Create analytics endpoints with aggregated queries:
  - Revenue totals by day/week/month.
  - Appointments per service.
  - Top N services.
  - Low-stock inventory list.
- Implement caching or optimized queries for heavy aggregations.

**Frontend**

- Admin dashboard pages with charts (Chart.js / Recharts).
- Filters for date ranges, services, payment methods.

**Database**

- Ensure indices on `createdAt`, `serviceId`, `status` for performant queries.

**API Endpoints**

- `GET /api/analytics/revenue?from=&to=`
- `GET /api/analytics/top-services?limit=5`
- `GET /api/analytics/low-stock`

### Acceptance Criteria

- Dashboard shows correct aggregated numbers and charts.
- Filters work and API remains responsive for expected dataset sizes.

### Deliverables

- Analytics pages, endpoints, sample charts and dashboards.

---

## Phase 8 — QA, Security, & Hardening

**Goal:** Stabilize the system: add testing, secure endpoints, and prepare for deployment.

### Tasks

**Testing**

- Unit tests for critical business logic (overlap checks, inventory deduction).
- Integration tests for API endpoints (appointments, payments).
- E2E tests covering booking → demo payment → completion → inventory deduction.

**Security**

- Ensure password hashing, JWT expiry and refresh strategy.
- Role-based access tests.
- Input validation and rate limiting (especially on chatbot / demo endpoints).

**Performance / Resilience**

- Add DB connection pooling and basic monitoring.
- Graceful error handling and retry for transient DB errors.

### Acceptance Criteria

- CI runs passing tests.
- Penetration checklist completed (no obvious auth bypass).
- Error rate and performance within acceptable ranges for MVP.

### Deliverables

- Test suite, CI pipeline config (GitHub Actions), security checklist.

---

## Phase 9 — Deployment, Handover & Documentation

**Goal:** Deploy to staging/production and prepare handover docs for the salon.

### Tasks

**Deployment**

- Prepare environment variable docs and `env.example`.
- Deploy backend (Render/Railway) and frontend (Vercel).
- Configure domain, HTTPS, and basic monitoring/alerts.

**Handover**

- Create admin user guide: how to add services, inventory, block dates, mark completion.
- Provide seed scripts and backup/restore instructions for DB.
- Provide developer docs: API spec (OpenAPI / Postman collection), Prisma schema, and deployment steps.

### Acceptance Criteria

- Production apps live and reachable.
- Admin guide available and tested.
- Backup/restore tested on staging.

### Deliverables

- Live deployments, admin/dev docs, Postman collection, and final checklist.

---

## Phase 10 — Future Enhancements (Backlog)

**Ideas for post-MVP**

- Real payment gateway integrations (PayMaya, GCash) with webhooks.
- Multi-technician scheduling with skill matching.
- LLM-based chatbot (context, memory, booking via chat).
- Multi-location / franchise support.
- Mobile app or PWA with offline booking capability.
- POS integration for in-store card payments.

---

## Common Test Cases (applies across phases)

- Create overlapping appointments concurrently — system should only allow within cap.
- Mark completion when inventory insufficient — behavior follows configured policy.
- Demo payment success/failure flows update appointment/payment correctly.
- Admin blocks dates — bookings on those dates are prevented.
- Inventory logs reflect every decrement and manual stock changes.

---

## Notes & Implementation Tips

- Use DB transactions for any read-modify-write sequences (appointments/stock).
- Store datetimes in UTC; convert to client timezone for UI.
- Keep chatbot rules and demo payment behavior configurable via admin settings for testing.
- Add feature flags for toggling demo payment / strict stock enforcement.

---

## Ready-to-use Checklists (copy-paste friendly)

### Pre-launch checklist

- [ ] Seed admin user
- [ ] Migrate DB
- [ ] Configure `MAX_CONCURRENT_APPOINTMENTS` default
- [ ] Add initial services & inventory
- [ ] Verify demo payment flow
- [ ] Run integration tests

### Launch checklist

- [ ] Deploy frontend & backend
- [ ] Configure env variables & secrets
- [ ] Smoke test full booking → payment → completion → inventory flow
- [ ] Share admin guide with salon owner
