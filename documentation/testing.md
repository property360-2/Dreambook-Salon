# Testing Playbook

## End-to-End Scenarios
- Customer books a service with open capacity: verify slot availability, booking creation, and pending status.
- Booking rejected when slot is blocked or at capacity: expect `409` from `/api/appointments` and toast messaging.
- Demo payment happy path: create appointment, `POST /api/payments/demo`, confirm via `PUT`, and assert appointment status updates to `CONFIRMED`.
- Demo payment failure path: simulate `FAILED`, ensure appointment remains `PENDING` and UI surfaces retry messaging.
- Appointment completion with inventory deduction: mark `COMPLETED`, confirm inventory adjustments recorded and low-stock warnings surface.
- Chatbot throttling: send rapid-fire questions using the same sessionId and expect throttle copy + retry delay.

## Smoke Tests
- `npm run test --workspaces --if-present` to run backend Jest + frontend Vitest suites.
- Seed reset: `npm run migrate --workspace backend && npm run seed --workspace backend` to rebuild fixtures.
- Manual admin sweep: log into dashboard, confirm appointments table populates, blocked ranges render, and chatbot rules list matches seed data.
