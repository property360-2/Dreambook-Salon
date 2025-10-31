# 01-concept.md

# 💇‍♀️ Salon Appointment & Inventory System — Concept Document

## Project Vision

Build a full-featured, pragmatic salon management system that covers booking, inventory automation, admin controls, a simple rule-based chatbot, analytics, and a demo online payment flow. The goal is to enable a salon to run day-to-day operations digitally with minimal manual stock tracking and fewer booking conflicts — while keeping the implementation simple enough for iterative development and future integrations (real payments, LLM chatbot, external POS).

---

## Objectives

- Provide a reliable customer booking experience with conflict/block prevention.
- Automatically deduct inventory when services are completed.
- Give admins flexible control: add services, link inventory items, set booking caps, block times/dates.
- Provide a demo payment flow (GCash/PayMaya) for testing checkout UX without real money.
- Include a basic rule-based chatbot to assist customers (easy to extend later).
- Offer analytics that help make inventory and business decisions.

---

## Scope

### In-Scope (MVP)

- User authentication & roles (Admin / Staff / Customer)
- Service CRUD (name, price, duration, linked inventory items & quantities)
- Inventory CRUD (name, stock, unit, threshold)
- Appointment booking UI + backend (slot selection, duration-based scheduling)
- Overlap prevention & admin-configurable appointment cap per time-slot
- Admin tools: manage services, inventory, appointments, settings
- Auto-deduction of inventory when appointment status set to `completed`
- Demo payment flow for `gcash` / `paymaya` / `onsite` (simulated success/failure)
- Basic analytics pages: revenue, top services, low stock
- Lightweight rule-based chatbot module (server-side or client-side JS)

### Out-of-Scope (Phase 1 / later)

- Real payment gateway integrations (PayMaya, GCash)
- Advanced AI chatbot (LLM)
- Multi-location / franchise management
- Complex resource scheduling (multiple technicians & skill-matching) — can be added later
- Offline sync / PWA features

---

## Primary Users & Roles

- **Admin**
  - Full access: users, services, inventory, appointments, analytics, settings
  - Can set appointment caps and blocked time ranges
- **Staff**
  - View today's appointments, mark appointments `in-progress` / `completed` / `no-show`
  - See inventory usage and low-stock alerts
- **Customer**
  - Browse services, book appointments, simulate payments, chat with chatbot, view own booking history

---

## Core Concepts & Business Rules

### Services & Required Inventory

- Each `Service` has:
  - `name`, `price`, `duration` (minutes)
  - `requiredItems`: list of inventory items + quantity consumed per single service
- Example: `Rebond` → consumes `Rebond Cream (1 bottle)`, `Neutralizer (0.5 bottle)`
- Inventory is decremented only when appointment status becomes `completed` (not on booking).

### Appointments & Blocking

- Appointments have: `customer`, `service`, `start_time`, `end_time`, `status`
- **Overlap prevention**:
  - When creating a new appointment, system checks active appointments for overlaps against the service duration.
  - Admin can configure **max concurrent appointments per time slot** (e.g., max 3)
- Admin can block specific dates/times (e.g., holidays) where booking is disabled.

### Inventory Automation

- Trigger: When staff/admin marks appointment `completed`.
- Action: For each `requiredItem` linked to the service, decrement the inventory `stock` by `quantity`.
- If inventory would go negative, either:
  - Prevent completion and show a warning, or
  - Allow completion but flag inventory as negative and alert admin (configurable).
- Low-stock: when `stock <= threshold` send admin alert or show on dashboard.

### Demo Payment Behavior

- Payment flow is simulated:
  - Payment record created with `method`, `amount`, `status` (`pending` → `paid`/`failed`)
  - TransactionId is a mock string (e.g., `TXN-123456`)
  - Demo endpoint may optionally randomize success/failure or allow deterministic success for testing
- Appointment `status` may update to `paid` upon demo success (or another bookkeeping field `payment.status` used)

### Chatbot (Rule-based)

- Lightweight bot implemented with simple rules/keyword matching.
- Intended for quick answers: services, price ranges, booking flow, hours of operation.
- Designed to be replaced or augmented by an LLM later; keep code modular.

---

## High-level Architecture (Concept)

- **Frontend**: React (or Next.js) single-page app (SPA) for customers & admin. Components: BookingForm, ServiceList, AdminDashboard, InventoryTable, ChatbotWidget, DemoPayment.
- **Backend**: Node.js + Express API with Prisma ORM to MySQL/Postgres.
- **Database**: Relational schema (Services, Inventory, ServiceInventory, Appointments, Users, Payments).
- **Hosting**: Frontend on Vercel, Backend on Render/Railway or similar.
- **Optional**: Webhooks later for actual payment providers.

---

## Key Data Flows

### Booking flow (high-level)

1. Customer selects service + date/time.
2. Frontend asks backend for available slots (backend checks overlaps & caps).
3. If available → create appointment record with `status: pending` (or `confirmed`).
4. Customer goes to demo payment (if selected), demo endpoint returns `paid` or `failed`.
5. Payment status stored in `payment` record; appointment `status` updated accordingly.

### Completion → Inventory deduction

1. Staff marks appointment `completed`.
2. Backend fetches linked `ServiceInventory` items for that service.
3. For each item, `inventory.stock = inventory.stock - quantity`.
4. If any `stock` <= `threshold`, create low-stock alert / dashboard flag.

---

## Non-functional Requirements

- **Reliability**: Prevent double-booking and inconsistent stock updates (use DB transactions).
- **Simplicity**: Keep chatbot and demo payment intentionally simple for MVP.
- **Extensibility**: Clear separation of service <-> inventory linkage for future pricing or bundles.
- **Security**: Passwords hashed (bcrypt), JWT for sessions, role-based authorization checks on routes.
- **Performance**: Reasonable for small-medium salons; scale later if needed.

---

## Assumptions & Constraints

- Single-location salon for MVP. Multi-location support is a future enhancement.
- Only one technician resource is modeled implicitly via max concurrent appointment cap. No per-staff skill matching initially.
- Inventory is tracked in the same units admin configures (no automatic unit conversions).
- Demo payment is UI-only and non-financial; no PCI compliance required for demo.

---

## Edge Cases & How to Handle

- **Concurrent completions**: Use database transactions / row locking when decrementing inventory to avoid race conditions.
- **Stock insufficient at completion**: Config option: `prevent_completion_on_insufficient_stock: true|false`. Default: `false` (complete but alert).
- **Timezones**: Store all timestamps in UTC; localize on frontend. (User's timezone should be configurable.)
- **Partial consumption / fractional usage**: Inventory `stock` and `quantity` should be floats.

---

## Acceptance Criteria (MVP)

1. Admin can add services and link inventory items with specific quantities.
2. Customer can book a service; system prevents overlapping based on service duration and admin cap.
3. Staff can mark an appointment as `completed` and inventory is automatically decremented.
4. Demo payment flow exists and updates payment status and appointment payment state.
5. Basic analytics page shows revenue and low-stock items.
6. Simple chatbot answers service & booking questions using pre-defined rules.

---

## Success Metrics

- remove double-bookings to near-zero (measured by booking conflict logs).
- Accurate inventory tracking for services used (match between expected deduction vs manual logs).
- Admin adoption: admin uses dashboard daily for stock checks.
- Customer bookings through web flow (demo payments used to exercise payment UX).

---

## Glossary

- **ServiceInventory**: Link table that states how much of an inventory item a service consumes.
- **Appointment Cap**: Admin-configured maximum concurrent bookings within overlapping periods.
- **Demo Payment**: Mock payment flow for UX testing only; not a real payment processor.

---
