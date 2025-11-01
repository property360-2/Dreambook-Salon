# 03-pages-ux-map.md

# 🎨 Pages & UX Map — Salon Appointment & Inventory System

This document lists every user-facing page (Customer & Admin), key components, routing structure, and UX flows. Each page includes: purpose, main components, important API calls, and acceptance criteria. Use this as a blueprint for building UI screens and wiring them to backend endpoints.

---

# Table of Contents
- Customer (Public) Pages
- Customer (Authenticated) Pages
- Admin Pages
- Shared Components
- Routing Structure (suggested)
- UX Flows (detailed)
  - Booking flow (with demo payment)
  - Appointment completion → inventory deduction
  - Admin: add service & link inventory
  - Admin: block times & set caps
  - Chatbot interactions
- UI Patterns & Accessibility
- Error states & Notifications
- Acceptance criteria & QA checklist

---

# Customer (Public) Pages

## `/` — Home / Landing
**Purpose:** Welcome page, highlight services, CTA to book, chatbot widget.
**Main components:** Hero, ServiceHighlights, ChatbotWidget, Footer.
**API calls:** `GET /api/services?featured=true`
**Notes:** Show "Book Now" CTA that routes to `/services` or `/book`.

---

## `/services` — Services Catalog
**Purpose:** Browse all services (filter by category/duration/price).
**Main components:** ServiceCard, FiltersBar, Pagination (optional).
**API calls:** `GET /api/services`
**Acceptance:** Users can view details and click "Book" to start booking flow.

---

## `/service/:id` — Service Detail
**Purpose:** Show detailed service info + required items (admin-visible), price, duration, recommended add-ons.
**Main components:** ServiceDetail, AddToBookingBtn, LinkedInventoryList.
**API calls:** `GET /api/services/:id`
**Acceptance:** Service info accurate; shows required inventory (admin-only details optionally).

---

# Customer (Authenticated) Pages

## `/book` — Booking Start (Service + Date)
**Purpose:** Choose service, pick date, request available times.
**Main components:** ServiceSelector, DatePicker (calendar), AvailabilityResults.
**API calls:** `GET /api/appointments/available?serviceId=&date=`
**Acceptance:** Shows available slots and prevents blocked dates/times.

---

## `/book/confirm` — Booking Confirm & Checkout
**Purpose:** Confirm details, choose payment method (demo), enter customer info.
**Main components:** BookingSummary, PaymentMethodSelect, DemoPaymentButton.
**API calls:** `POST /api/appointments` then optionally `POST /api/payments/demo`
**Acceptance:** Booking created; if payment chosen and succeeds, booking `payment.status` = `paid`.

---

## `/payment/demo/:paymentId` — Demo Payment Page
**Purpose:** Simulate payment flow (Confirm / Cancel).
**Main components:** PaymentInfo, ConfirmBtn, CancelBtn, MockReceipt.
**API calls:** `POST /api/payments/demo` (or `PUT` to change status)
**Acceptance:** Produces mock txnId; updates payment & appointment status accordingly.

---

## `/appointments` — My Appointments
**Purpose:** Customer booking history and upcoming appointments.
**Main components:** AppointmentList, AppointmentCard, RebookBtn, CancelBtn.
**API calls:** `GET /api/appointments?userId=<me>`
**Acceptance:** Customers can view, cancel (if allowed), or rebook.

---

# Admin Pages

## `/admin/dashboard` — Admin Overview
**Purpose:** KPIs: revenue, upcoming appointments, low-stock alerts, top services.
**Main components:** RevenueChart, AppointmentsTable, LowStockPanel, QuickActions.
**API calls:** `GET /api/analytics/revenue`, `GET /api/analytics/top-services`, `GET /api/analytics/low-stock`
**Acceptance:** KPIs load quickly; low-stock items are visible and clickable.

---

## `/admin/services` — Manage Services
**Purpose:** CRUD services, upload hero imagery, and link required inventory items.
**Main components:** ServicesTable, ServiceFormModal (add/edit), ServiceInventoryEditor, ImageUploader.
**API calls:** `GET /api/services`, `POST /api/services`, `PUT /api/services/:id`, `POST /api/uploads/service-image`, `POST /api/services/:id/inventory`, `DELETE /api/services/:id/inventory/:inventoryId`
**Acceptance:** Admin can add/edit service details, upload a cover image, and link required inventory items.
**MVP note:** Phase 2 surfaces these forms within the authenticated dashboard while dedicated `/admin/services` route is still pending.

---

## `/admin/inventory` — Inventory Management
**Purpose:** Manage stock quantities, set thresholds, view logs.
**Main components:** InventoryTable, StockEditModal, InventoryLogView.
**API calls:** `GET /api/inventory`, `POST /api/inventory`, `PUT /api/inventory/:id`, `GET /api/inventory/logs`
**Acceptance:** Admin can modify stock; logs created for each change.
**MVP note:** Phase 2 delivers add/update flows within the dashboard module; log view arrives with analytics phase.

---

## `/admin/appointments` — Appointments Management
**Purpose:** List & manage all bookings; mark in-progress/completed/no-show.
**Main components:** AppointmentFilter, AppointmentsTable, StatusActions (complete).
**API calls:** `GET /api/appointments`, `PUT /api/appointments/:id/complete`
**Acceptance:** Staff can change status; completion triggers inventory deduction.

---

## `/admin/settings` — System Settings
**Purpose:** Set `maxConcurrentAppointments`, block dates/times, configure demo payment behavior.
**Main components:** SettingsForm, BlockedRangesEditor, FeatureFlags.
**API calls:** `GET/PUT /api/settings`, `POST /api/settings/blocked`
**Acceptance:** Settings persist and affect booking behavior.

---

## `/admin/chatbot` — Chatbot Rules Editor
**Purpose:** Admin can create/edit rule-based responses.
**Main components:** RulesList, RuleEditor (pattern, reply, priority).
**API calls:** `GET /api/chatbot/rules`, `POST /api/chatbot/rules`, `PUT /api/chatbot/rules/:id`
**Acceptance:** Rules immediately affect bot responses.

---

# Shared Components (reusable)

- `Navbar` — role-aware navigation links.
- `ProtectedRoute` — guards pages based on role.
- `ServiceCard` — shows name, price, duration, and "Book" CTA.
- `BookingForm` — composed of ServiceSelector, DatePicker, TimeSlots.
- `DatePicker` — calendar with blocked ranges disabled.
- `TimeSlotList` — shows available slots with concurrency warning.
- `PaymentCard` — demo payment options & CTA.
- `ChatbotWidget` — floating chat with message list + input.
- `InventoryTable` — table with sorting/filters and inline edit.
- `AnalyticsChart` — generic chart wrapper for Chart.js.
- `Toast` / `Snackbar` — transient notifications.
- `ConfirmModal` — for destructive actions (cancel appointment, complete with insufficient stock).

---

# Routing Structure (suggested)

```

/                -> Home
/services        -> Services catalog
/service/:id     -> Service detail
/login           -> Login
/register        -> Register
/book            -> Booking flow (protected)
/book/confirm    -> Booking confirmation
/payment/demo/:id-> Demo payment
/appointments    -> My appointments (protected)

/admin
/dashboard
/services
/inventory
/appointments
/settings
/chatbot

```

Use nested routes for admin. Use role-based redirects: non-admin trying to access `/admin/*` → 403 / redirect to home.

---

# UX Flows (detailed)

## Booking Flow (Customer)
1. Customer selects service on `ServiceCard` → clicks **Book**.
2. `/book` page opens with prefilled service.
3. Customer picks date → frontend requests `GET /api/appointments/available?serviceId=&date=`. Show `TimeSlotList`.
4. Customer selects slot → click **Continue**.
5. `/book/confirm` shows summary; choose payment method (Demo/Onsite).
6. On Confirm: `POST /api/appointments` (creates appointment with `status: pending`).
   - If payment chosen:
     - Redirect to `/payment/demo/:paymentId`.
     - On confirm: `POST /api/payments/demo` → returns `paid` or `failed`.
     - If `paid`: update appointment `payment.status` & maybe `appointment.status: paid` / `confirmed`.
7. Show confirmation screen with txnId & appointment details; send email/sms notification (optional).

**UX details:** show spinner when checking availability; disable Confirm button during network calls; show friendly messages for blocked dates.

---

# API Updates (Phase 2)

- `GET /api/appointments/available` — returns capacity-aware time slots per service/date, accounting for blocked ranges and salon concurrency limits.
- `POST /api/appointments` — creates a booking, scaffolds customer accounts for new guests, and logs creation events; response includes optional temp credentials.
- `PUT /api/appointments/:id/status` — transitions appointments through `PENDING`, `CONFIRMED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, triggering inventory deductions and timeline logs.
- `GET /api/settings` / `PUT /api/settings` — surfaces salon-wide booking settings (`maxConcurrentAppointments`, `bookingWindowDays`) for admin control.
- `POST /api/settings/blocked` / `DELETE /api/settings/blocked/:id` — manages blackout windows that immediately affect availability checks.
- `POST /api/payments/demo` / `PUT /api/payments/demo/:id` — mock payment lifecycle that stamps demo transaction IDs and syncs appointment payment states.
- `GET /api/chatbot/rules` + CRUD routes — admin rule management for the keyword bot; `POST /api/chatbot/respond` powers the UI widget with throttled keyword matching.
---

## Appointment Completion → Inventory Deduction (Admin / Staff)
1. Staff views `/admin/appointments` and clicks **Complete** for an appointment.
2. Client shows arrival; staff clicks **Mark as Completed**.
3. Frontend calls `PUT /api/appointments/:id/complete`.
4. Backend starts DB transaction:
   - Reads `service.requiredItems`.
   - For each item: `inventory.stock -= quantity`.
   - Insert `InventoryLog` record per change.
   - Commit.
5. Backend returns success; UI shows success toast and updates inventory list.
6. If any stock would go negative:
   - If `prevent_completion_on_insufficient_stock` enabled → return error and show modal with options.
   - Else allow and flag inventory negative; show alert on dashboard.

**UX details:** Confirmation modal before completion; show per-item deduction summary.

---

## Admin: Add Service & Link Inventory
1. Admin opens `/admin/services` → clicks **Add Service**.
2. ServiceForm collects `name`, `price`, `duration`.
3. Admin opens `ServiceInventoryEditor` to add rows: `inventoryItem` + `quantity`.
4. On save: `POST /api/services` then `POST /api/services/:id/inventory` for each link.
5. UI shows success and new service in list.

**UX details:** Autocomplete inventory dropdown; validation on quantity > 0.

---

## Admin: Block Times & Set Caps
1. `/admin/settings` → `BlockedRangesEditor` to pick date ranges or recurring slots.
2. Save → `POST /api/settings/blocked`.
3. Set `maxConcurrentAppointments` → `PUT /api/settings`.
4. Booking availability logic consults blocked ranges and cap when returning slots.

**UX details:** Calendar UI for blocked ranges with drag-to-select; preview affected slots.

---

## Chatbot Interactions
- Chat widget calls `POST /api/chatbot/message` with message text.
- Backend applies rules (regex/keyword) and returns a reply object:
  - `{ reply: "text", actions: [{ type: "book", payload: { serviceId: 1 } }] }`
- If action exists, show quick action buttons: "Book Rebond" → prefill booking form.

**UX details:** Persist temporary chat history, allow copy of booking link.

---

# UI Patterns & Accessibility

- Responsive layout (mobile-first). Nav collapses to hamburger on small screens.
- Use semantic HTML (buttons, form labels, fieldsets).
- Keyboard accessible: All interactive elements focusable, modals trap focus.
- Color contrast: meet WCAG AA for text & buttons.
- Date/time pickers support keyboard entry and screen readers.
- Use aria-live regions for toast notifications and chat messages.
- Loading states: skeletons for lists, disabled buttons for pending actions.

---

# Error States & Notifications

- **Availability check fails:** show inline error + retry button.
- **Booking conflict (race):** show conflict modal and suggest next available slots.
- **Payment failed:** show reason and option to retry or choose another method.
- **Completion prevented (insufficient stock):** show detailed modal with per-item stock amounts and options (abort or force-complete).
- **Generic network error:** global banner "Network error — Check your connection".

Notifications: success / info / warning / error toasts; critical issues (low-stock) appear in admin dashboard persistent panel.

---

# Acceptance Criteria & QA Checklist (Pages)
- [ ] Landing & Services load with minimal latency.
- [ ] Booking flow creates appointment and honors blocked slots and capacity caps.
- [ ] Demo payment page returns mock txnId and updates appointment/payment status.
- [ ] Admin can CRUD services and link inventory items; changes reflect in booking completion deduction.
- [ ] Marking appointment completed deducts inventory (logged) and updates dashboard.
- [ ] Chatbot responds to simple queries and quick-actions work.
- [ ] All pages are responsive and keyboard-accessible.

---

# Final Notes / Implementation Tips
- Keep state management simple: React Query (or SWR) for server state + local state for form handling.
- Centralize API error handling and retry policies (especially for booking and completion).
- Make `DemoPayment` configurable (deterministic vs randomized) via `/admin/settings`.
- Use optimistic UI carefully (only for non-critical actions or with rollback on failure).

