# Phase 2 Follow-ups (Next Session)

- [ ] **Service editing** – allow admins to update existing services (name, price, image) and persist `imageUrl` changes via PUT `/api/services/:id`.
- [ ] **Image lifecycle** – delete or detatch previous Cloudinary asset when an admin uploads a replacement or removes an image; store Cloudinary `public_id` to support cleanup.
- [ ] **UX polish** — add inline error messaging for image upload failures (service form) and show a placeholder image when no `imageUrl` exists.
- [ ] **API hardening** — add backend tests for `/api/uploads/service-image` and validation around file type/size before sending to Cloudinary.
- [ ] **Docs & env** — update deployment checklist with Cloudinary requirements (env vars, allowed file size) and note optional rate limits.
- [ ] **Seed refresh** — rerun `npm run seed --workspace backend` after clearing dev DB so services pick up the sample image URLs.

## Booking & Availability

- [x] Extend Prisma schema with `Settings` and `BlockedRange` tables to store `maxConcurrentAppointments` and manual blackout windows; run migration after updates.
- [x] Implement `GET /api/appointments/available` leveraging service duration, cap, and blocked ranges to return slot list.
- [x] Ship `POST /api/appointments` with overlap prevention, computed `scheduledEnd`, and customer linkage (create customer record when booking anonymously).
- [x] Add admin endpoints to create/delete blocked ranges (`POST /api/settings/blocked`, `DELETE /api/settings/blocked/:id`) and wire to Prisma layer.

## Appointment Lifecycle & Inventory

- [x] Introduce `PUT /api/appointments/:id/status` supporting `in-progress`, `completed`, and `cancelled`.
- [x] Create inventory deduction service triggered on `completed` appointments, failing fast when stock would go negative and surfacing low-stock warnings.
- [x] Log appointment status changes and inventory adjustments for audit (basic log table or reuse existing utilities).
- [x] Update seeds to include sample appointments with various statuses for dashboard/testing.

## Frontend Booking Flow

- [x] Scaffold booking feature folder (`frontend/src/features/booking`) with `ServiceSelector`, `DatePicker`, and `TimeSlotList` components.
- [x] Build `/book` screen that fetches services, requests availability, and persists selection via context/store.
- [x] Build `/book/confirm` screen with summary, customer info form, and submission to `POST /api/appointments`; route to demo payment when applicable.
- [x] Add empty/error states for slots and network failures plus toasts for conflicts.

## Admin Dashboard Enhancements

- [ ] Create `AppointmentsTable` widget that lists upcoming bookings, filters by status, and offers inline status updates.
- [ ] Surface low-stock alerts and blocked-date list in the dashboard summary cards.
- [ ] Enable service editing modal to manage linked inventory (add/remove) alongside the image tasks above.
- [ ] Add role-gated navigation entries for new admin routes (appointments, settings).

## Demo Payment Flow

- [x] Add `Payment` Prisma model with `status`, `method`, `amount`, `transactionId`, and `appointmentId`.
- [x] Implement `POST /api/payments/demo` (create) and `PUT /api/payments/demo/:id` (confirm/cancel) endpoints producing mock transaction IDs.
- [x] Update appointment service to reconcile payment status and reflect in booking confirmation responses.
- [x] Build `/payment/demo/:paymentId` UI that mimics confirm/cancel with optimistic UI and fallback toasts.

## Chatbot MVP

- [x] Define `ChatbotRule` Prisma model (pattern, reply, priority, isActive) and expose CRUD endpoints under `/api/chatbot/rules`.
- [x] Implement keyword matching service with fallback responses and simple throttling.
- [ ] Build `ChatbotWidget` component with floating launcher, conversation list, and input; persist sessions in localStorage.
- [x] Seed baseline rules (greeting, hours, booking CTA) and document how to extend them.

## Docs, Env, & QA

- [x] Update `.env.example` with new Cloudinary + chatbot + payment demo variables (e.g., `SALON_MAX_CONCURRENT_DEFAULT`, `SALON_CHATBOT_RATE_LIMIT`).
- [x] Document new routes and flows in `documentation/pages.md` and `documentation/concept.md`.
- [x] Outline e2e scenarios covering booking, completion with stock deduction, and payment success/failure (`documentation/testing.md` or update existing testing section).
- [x] Add Jest/RTL tests for new booking, appointment, and payment logic; list missing cases in the TODO if any remain.
