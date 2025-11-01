# 02-phases.md

# 💇‍♀️ Salon Appointment & Inventory System — **Development Phases (Django + CDN)**

> Target stack: **Django** (DRF optional), **PostgreSQL/MySQL**, **Django Templates with Atomic Components**, **CDN for static/media**.
> Goal: Ship a clean MVP fast, keep code modular, and leave hooks for real payments + LLM later.

---

## 🧭 Phase Map

1. **Phase 0 — Foundations & DevOps**
2. **Phase 1 — Project Bootstrap & Atomic UI**
3. **Phase 2 — Auth, Users, RBAC**
4. **Phase 3 — Services & Inventory**
5. **Phase 4 — Appointments, Availability & Blocking**
6. **Phase 5 — Demo Payments (GCash/PayMaya/Onsite)**
7. **Phase 6 — Rule-based Chatbot**
8. **Phase 7 — Analytics & Dashboard**
9. **Phase 8 — Admin UX Polish & Notifications**
10. **Phase 9 — QA, Seed Data, Test Coverage**
11. **Phase 10 — CDN, Build, and Deployment**
12. **Phase 11 — Post-MVP Backlog**

Each phase below includes: **Deliverables**, **Tasks**, **Routes/Models (if any)**, **Acceptance Criteria**, and **Notes**.

---

## 0) Foundations & DevOps

**Deliverables**

* `.env.example` with DB creds, secret key, CDN bucket vars
* `Makefile` / `justfile` with common commands
* Pre-commit (black, isort, flake8, djlint)
* GitHub Actions (lint, test)

**Tasks**

* Create virtualenv & base requirements
* Add code style tooling + hooks
* Decide DB engine (Postgres recommended)
* Choose CDN (Cloudflare R2 / S3) + region

**Acceptance**

* `make dev` runs server
* `make test` runs tests
* Linting passes in CI

**Snippet (requirements.txt)**

```
Django>=5.0
psycopg[binary]
django-environ
django-storages
boto3
Pillow
whitenoise
python-dateutil
```

---

## 1) Project Bootstrap & Atomic UI

**Deliverables**

* Django project `salon_system/`
* Apps scaffolded: `core, services, inventory, appointments, payments, chatbot, analytics`
* Base template + atomic directories

**Tasks**

* `django-admin startproject salon_system`
* Create apps & register in `INSTALLED_APPS`
* `templates/components/{atoms,molecules,organisms}`, `templates/pages`
* Base layout (navbar, flash messages, footer)
* Static pipeline with CDN-ready `collectstatic`

**Acceptance**

* Home page renders using atoms/molecules
* Static files served locally & via `collectstatic` without errors

**Atomic directories**

```
/templates/
  /components/
    /atoms/ (Button, Input, Badge, Avatar, Icon)
    /molecules/ (FormRow, StatCard, ServiceCard)
    /organisms/ (BookingPanel, InventoryTable, ChatbotWidget)
  /pages/
    home.html, admin_dashboard.html, booking.html, services.html, inventory.html
```

---

## 2) Auth, Users, RBAC

**Deliverables**

* Custom `User` model (roles: ADMIN, STAFF, CUSTOMER)
* Session auth (Django auth) + optional DRF JWT for API
* Login, logout, registration (customer)
* Role-based decorators: `@role_required("ADMIN")`, etc.

**Models**

* `core.User(email, role, first_name, last_name, is_active)`

**Routes**

* `GET /auth/login`, `POST /auth/login`
* `POST /auth/logout`
* `GET /auth/register` (customer)

**Acceptance**

* Users can log in/out
* Admin can invite staff
* Role-restricted pages redirect unauthenticated users

---

## 3) Services & Inventory

**Deliverables**

* CRUD UI + APIs for Service and Inventory
* Link table for service consumption
* Threshold alerts in dashboard

**Models**

* `services.Service(name, price, duration_minutes, is_active)`
* `inventory.Item(name, unit, stock: float, threshold: float, is_active)`
* `services.ServiceItem(service, item, qty_per_service: float)`

**Routes (examples)**

* Services: `GET/POST /admin/services`, `GET/POST /admin/services/{id}`
* Inventory: `GET/POST /admin/inventory`

**Acceptance**

* Admin can create/edit services and link items
* Low stock items appear on dashboard when `stock <= threshold`

**Notes**

* Use inline formset for Service + ServiceItem in Django admin or custom form.

---

## 4) Appointments, Availability & Blocking

**Deliverables**

* Booking form (service, date, time)
* Overlap prevention with **max concurrent appointments**
* Blackout windows (blocked ranges)
* Settings singleton for caps & booking window days

**Models**

* `appointments.Appointment(customer, service, start_at, end_at, status)`
* `appointments.BlockedRange(start_at, end_at, reason)`
* `appointments.Settings(max_concurrent:int, booking_window_days:int, prevent_completion_on_insufficient_stock:bool)`

**Logic**

* Availability API checks overlaps within `[start_at, end_at)` and cap
* Save hook validates not in a blocked range

**Routes**

* `GET /api/availability?service_id=&date=`
* `POST /book` (creates pending/confirmed appointment)
* Admin: `GET/POST /admin/blocked-ranges`, `GET/POST /admin/settings`

**Acceptance**

* Double-booking prevented
* Admin can block dates and set caps

---

## 5) Demo Payments (GCash/PayMaya/Onsite)

**Deliverables**

* Simulated payment endpoint + UI modal
* Payment record linked to appointment
* Deterministic mode (always success) + random mode

**Models**

* `payments.Payment(appointment, method:enum, amount, status:enum[pending,paid,failed], txn_id)`

**Routes**

* `POST /payments/demo/initialize` → returns mock intent
* `POST /payments/demo/confirm` → sets status + updates appointment payment_state

**Acceptance**

* Demo flow updates UI state (paid/failed)
* Transactions visible in admin

---

## 6) Rule-based Chatbot

**Deliverables**

* Minimal keyword matcher with admin CRUD
* Throttled endpoint to respond

**Models**

* `chatbot.Rule(keyword, response, is_active)`

**Routes**

* `POST /api/chatbot/respond` → `{ message }` → `{ reply }`
* Admin: `GET/POST /admin/chatbot/rules`

**Acceptance**

* Common queries answered (price range, hours, booking link)
* Easily extendable ruleset

---

## 7) Analytics & Dashboard

**Deliverables**

* Revenue cards, top services, low stock list, appointment volume heatmap
* Chart.js (CDN) integration

**Queries**

* Revenue by day/month
* Count by service
* Inventory items under threshold
* Appointments by hour/day

**Acceptance**

* Charts load under 1s with seed data
* Export CSV for revenue & appointments

---

## 8) Admin UX Polish & Notifications

**Deliverables**

* Toasts, form validation, pagination, search
* Optional email notifications (low stock, booking confirmation)

**Acceptance**

* Admin workflows < 3 clicks for common tasks
* Low stock email triggered on threshold breach (if SMTP configured)

---

## 9) QA, Seed Data, Test Coverage

**Deliverables**

* Management command to seed demo data
* Unit tests for availability and inventory deduction
* E2E smoke tests (Django test client)

**Commands**

```
python manage.py seed_demo
python manage.py test
```

**Acceptance**

* 80%+ coverage for core logic (appointments, inventory)
* Demo data creates: 5 services, 20 items, 50 appointments

---

## 10) CDN, Build, and Deployment

**Deliverables**

* `collectstatic` to CDN bucket (Cloudflare R2 / S3)
* Django `storages` configured for static & media
* Production settings: security headers, `SECURE_*`, `ALLOWED_HOSTS`

**Settings (example)**

```python
# settings.py (excerpt)
STATIC_URL = "https://cdn.example.com/static/"
MEDIA_URL = "https://cdn.example.com/media/"

STORAGES = {
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
    },
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
}
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN")  # cdn domain
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=31536000, public"}
```

**Acceptance**

* Static & media load from CDN domain
* Cache headers applied; versioned builds work after `collectstatic`

---

## 11) Post-MVP Backlog

* Real payment integrations (GCash/PayMaya)
* Multi-branch/location support
* Staff skill mapping & resource scheduling
* LLM chatbot with context + RAG (FAQs, services)
* SMS/Email reminders + calendar invites
* PWA/offline & mobile-first optimizations
* Audit trail & advanced permissions

---

## 🔌 API Sketch (if exposing JSON)

**Endpoints (sample)**

* `GET /api/services` — list services
* `GET /api/inventory/low-stock` — dashboard list
* `POST /api/appointments/availability` — timeslots per day
* `POST /api/appointments` — create booking
* `POST /api/appointments/{id}/complete` — triggers inventory deduction
* `POST /api/payments/demo/confirm` — mark paid/failed
* `POST /api/chatbot/respond` — rule-based reply

---

## 🔄 Inventory Deduction Flow (Detail)

1. Staff sets appointment → `completed`.
2. Transaction begins → fetch `ServiceItem` rows for `service_id`.
3. For each item: decrement `Item.stock` by `qty_per_service`.
4. If any would go < 0 → behavior depends on `prevent_completion_on_insufficient_stock`.
5. Commit transaction; emit low-stock signals.

---

## 🧪 Availability Algorithm (Pseudocode)

```
# inputs: service_id, date, start_time
service = Service.get(id)
start = combine(date, start_time)
end   = start + timedelta(minutes=service.duration)

if BlockedRange.exists(overlaps=[start, end]):
    return 409 BLOCKED

active = Appointment.filter(start_at < end and end_at > start and status in ["pending","confirmed","in-progress"]).count()

if active >= Settings.max_concurrent:
    return 409 FULL

return 200 AVAILABLE
```

---

## 🧱 Minimal ERD (Text)

```
User (id, email, role)
Service (id, name, price, duration_minutes)
Item (id, name, unit, stock, threshold)
ServiceItem (service_id, item_id, qty_per_service)
Appointment (id, user_id, service_id, start_at, end_at, status, payment_state)
BlockedRange (id, start_at, end_at, reason)
Settings (singleton)
Payment (id, appointment_id, method, amount, status, txn_id)
Rule (id, keyword, response, is_active)
```

---

## 🧰 Developer Commands (Makefile idea)

```
make dev            # runserver + watch static
make migrate        # makemigrations & migrate
make seed           # seed demo data
make lint           # black, isort, flake8, djlint
make collect        # collectstatic to CDN
```

---

## ✅ Phase-by-Phase Exit Checklist

* [ ] **P0**: CI green, lint/test scripts ok
* [ ] **P1**: Atomic templates render; base navbar/footer
* [ ] **P2**: Auth + RBAC working
* [ ] **P3**: Services/Inventory CRUD + links
* [ ] **P4**: Overlap prevention + blocking + settings
* [ ] **P5**: Demo payments wired to appointments
* [ ] **P6**: Chatbot rules CRUD + respond endpoint
* [ ] **P7**: Dashboard charts & CSV export
* [ ] **P8**: UX polish + notifications
* [ ] **P9**: Seeds + tests ≥ 80% core coverage
* [ ] **P10**: CDN live; cache headers verified

---

### Notes for Future You

* Keep templates small: prefer atoms/molecules over monolithic pages.
* Put cross-cutting concerns (signals, permissions) in `core/`.
* Use `transaction.atomic()` around completion → inventory logic.
* Store timestamps in UTC; format in templates.
* Add feature flags (env-based) for demo payment modes.
