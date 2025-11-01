# 03-pages.md

# 💇‍♀️ Salon Appointment & Inventory System — **Pages & Component Map (Django + CDN)**

> This document defines every key page, its component structure (atoms → molecules → organisms), purpose, and routing convention.  Designed for Django Templates + CDN-hosted static assets using the Atomic Design principle.

---

## 🏠 1. Home Page — `/`

**Purpose:** Entry point for customers; highlights services, booking CTA, chatbot widget.

**Template:** `pages/home.html`

**Composed Of:**

* **Atoms:** Button (Book Now), TextBlock, Image
* **Molecules:** ServiceCard (thumbnail + price), TestimonialCard
* **Organisms:** HeroBanner, FeaturedServices, Footer

**Dynamic Context:**

* Featured 3–4 active services
* Opening hours (from settings)

**Includes:** ChatbotWidget (bottom-right, loaded via CDN script)

---

## 💆‍♀️ 2. Services Page — `/services/`

**Purpose:** List of all active services with details, linked inventory consumption visible only to admin/staff.

**Template:** `pages/services.html`

**Composed Of:**

* **Atoms:** Badge (price), Button (Book Now)
* **Molecules:** ServiceCard (name, description, duration)
* **Organisms:** ServiceList (loop of cards)

**Dynamic Context:**

* Services queryset (active=True)
* Admin mode → shows stock relation info

---

## 📅 3. Booking Page — `/book/`

**Purpose:** Customer selects a service, date/time; handles availability check & booking creation.

**Template:** `pages/booking.html`

**Composed Of:**

* **Atoms:** InputDate, SelectDropdown, SubmitButton
* **Molecules:** BookingFormGroup, TimeSlotCard
* **Organisms:** BookingPanel (availability grid + form)

**Dynamic Context:**

* Services (for dropdown)
* Availability API (via AJAX to `/api/availability`)

**Flow:**

1. Select service → fetch durations.
2. Choose date/time → check overlaps.
3. Confirm → create appointment.

---

## 💳 4. Demo Payment Page — `/payment/<appointment_id>/`

**Purpose:** Simulate payment for demo checkout (GCash/PayMaya/Onsite).

**Template:** `pages/payment.html`

**Composed Of:**

* **Atoms:** PaymentOptionButton, StatusBadge
* **Molecules:** PaymentSummaryCard, PaymentStatusAlert
* **Organisms:** PaymentPanel (handles simulated flow)

**Dynamic Context:**

* Appointment + amount
* Payment status transitions (pending → paid/failed)

**Behavior:**

* Randomized or deterministic outcome depending on settings.

---

## 📦 5. Inventory Page — `/admin/inventory/`

**Purpose:** CRUD for inventory items, low-stock alerts, auto-refresh widgets.

**Template:** `pages/admin_inventory.html`

**Composed Of:**

* **Atoms:** TableHeader, StockBadge, InputNumber
* **Molecules:** InventoryRow (name, stock, threshold)
* **Organisms:** InventoryTable, LowStockAlertPanel

**Dynamic Context:**

* List of all items
* Highlight `stock <= threshold`

**Admin Actions:** Add, edit, archive item.

---

## 💇‍♂️ 6. Service Management Page — `/admin/services/`

**Purpose:** Admin CRUD for services and their required inventory items.

**Template:** `pages/admin_services.html`

**Composed Of:**

* **Atoms:** InputField, Select, QuantityInput
* **Molecules:** ServiceItemRow (item + qty)
* **Organisms:** ServiceForm (inline formset for ServiceItem)

**Dynamic Context:**

* All items available for linking
* Pre-filled data for editing

---

## 🕐 7. Appointment Management Page — `/admin/appointments/`

**Purpose:** View all appointments with filtering and status management.

**Template:** `pages/admin_appointments.html`

**Composed Of:**

* **Atoms:** StatusBadge, DateFilterInput
* **Molecules:** AppointmentRow
* **Organisms:** AppointmentTable, FilterBar

**Dynamic Context:**

* Upcoming, completed, no-show lists
* Staff can mark appointments as completed → triggers inventory deduction

---

## ⛔ 8. Blocked Dates & Settings Page — `/admin/settings/`

**Purpose:** Manage booking caps, blocked ranges, and inventory behavior flags.

**Template:** `pages/admin_settings.html`

**Composed Of:**

* **Atoms:** ToggleSwitch, InputNumber
* **Molecules:** BlockRangeRow, ConfigField
* **Organisms:** SettingsPanel, BlockedRangeTable

**Dynamic Context:**

* Singleton Settings object
* CRUD for BlockedRange

---

## 💬 9. Chatbot Rules Page — `/admin/chatbot/`

**Purpose:** Admin view to manage chatbot keyword-response rules.

**Template:** `pages/admin_chatbot.html`

**Composed Of:**

* **Atoms:** InputText, SaveButton
* **Molecules:** RuleRow
* **Organisms:** ChatbotRulesTable

**Dynamic Context:**

* Rule list, add/edit/delete buttons

---

## 📊 10. Analytics Dashboard — `/admin/dashboard/`

**Purpose:** Visual analytics (revenue, top services, low-stock, appointment volume).

**Template:** `pages/admin_dashboard.html`

**Composed Of:**

* **Atoms:** StatBadge, ChartCanvas
* **Molecules:** StatCard (title, value, delta)
* **Organisms:** RevenueChart, ServiceRankingChart, LowStockPanel

**Dynamic Context:**

* Chart.js (CDN)
* Aggregated metrics (from ORM queries)

---

## 👤 11. Login & Registration Pages — `/auth/login`, `/auth/register`

**Purpose:** Authentication entry for customers and staff.

**Template:** `pages/login.html`, `pages/register.html`

**Composed Of:**

* **Atoms:** Input, Button
* **Molecules:** AuthFormGroup
* **Organisms:** LoginForm, RegisterForm

**Dynamic Context:**

* Redirect based on role after login

---

## 📜 12. Booking History Page — `/my/bookings/`

**Purpose:** Customer view of past and upcoming appointments.

**Template:** `pages/my_bookings.html`

**Composed Of:**

* **Atoms:** StatusBadge, DateLabel
* **Molecules:** BookingRow
* **Organisms:** BookingHistoryTable

**Dynamic Context:**

* Appointments filtered by logged-in user

---

## 🧱 Shared Components

| Type         | Component                                                           | Description             |
| ------------ | ------------------------------------------------------------------- | ----------------------- |
| **Atom**     | `Button`, `Badge`, `Input`, `ToggleSwitch`, `StatBadge`             | Base visual elements    |
| **Molecule** | `FormRow`, `Card`, `RowItem`, `FormGroup`                           | Small reusable sections |
| **Organism** | `BookingPanel`, `InventoryTable`, `ChatbotWidget`, `DashboardPanel` | Page-level features     |

---

## 🌐 Routing Map (Simplified)

| Path                   | Page                | Access      |
| ---------------------- | ------------------- | ----------- |
| `/`                    | Home                | Public      |
| `/services/`           | Services            | Public      |
| `/book/`               | Booking             | Customer    |
| `/payment/<id>/`       | Payment             | Customer    |
| `/my/bookings/`        | Booking History     | Customer    |
| `/auth/login`          | Login               | Public      |
| `/auth/register`       | Register            | Public      |
| `/admin/dashboard/`    | Dashboard           | Admin       |
| `/admin/services/`     | Service Management  | Admin       |
| `/admin/inventory/`    | Inventory           | Admin       |
| `/admin/appointments/` | Appointments        | Staff/Admin |
| `/admin/settings/`     | Settings & Blocking | Admin       |
| `/admin/chatbot/`      | Chatbot Rules       | Admin       |

---

## 🧩 CDN Components and Scripts

**Hosted:**

* `main.css` (compiled Tailwind)
* `chatbot-widget.js` (standalone rule-based engine)
* `charts.js` (Chart.js via CDN)
* `helpers.js` (availability + payment utilities)

**Example include (template):**

```html
{% load static %}
<link rel="stylesheet" href="https://cdn.example.com/static/css/main.css">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.example.com/static/js/chatbot-widget.js" defer></script>
```

---

## 🧠 Template Tips

* Every page extends `base.html` with `{% block content %}`.
* Import atoms and molecules using `{% include 'components/...html' %}`.
* Use Django `context` for dynamic data (passed by views).
* Prefer CDN scripts for interactivity (chatbot, charts, booking slots).

---

## ✅ Completion Criteria

* All listed templates exist and render without static errors.
* Reusable components live under `/templates/components/`.
* CDN files load successfully via HTTPS.
* Each route has a view + template pairing defined.

---

> **Next Step Suggestion:** Generate the base Django app skeleton (`salon_system/`) with `core`, `services`, `inventory`, and atomic folder scaffolding for you to start committing.
