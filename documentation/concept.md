# 💇‍♀️ Salon Appointment & Inventory System — **Django + CDN Edition**

## 🎯 Project Vision

A modular **salon management system** built on **Django**, emphasizing **clean component reuse (atomic design)**, automated **inventory deduction**, and smooth **appointment handling** with demo payment and chatbot support.
Designed to be **fast, reliable, and CDN-ready**, supporting scalable frontend assets and modular backend logic.

---

## ⚙️ Tech Stack Overview

| Layer                  | Technology                                   | Description                                                                   |
| ---------------------- | -------------------------------------------- | ----------------------------------------------------------------------------- |
| **Backend**            | **Django (Python)**                          | Main API and admin panel — REST or DRF-based for modular endpoints.           |
| **Frontend Rendering** | Django Templates + CDN-hosted static files   | Uses atomic design components: atoms, molecules, organisms, templates, pages. |
| **Database**           | PostgreSQL / MySQL                           | Core relational schema for appointments, inventory, and payments.             |
| **Static Assets**      | CDN (Cloudflare / AWS S3 / Firebase Hosting) | For CSS, JS, images, media, chatbot assets, etc.                              |
| **Auth & Security**    | Django Auth + JWT (optional DRF)             | Role-based access and secure sessions.                                        |
| **Analytics Layer**    | Django ORM queries + Chart.js (CDN)          | Dashboard charts and insights.                                                |

---

## 🧩 Objectives

* Deliver a unified, responsive web platform for salon operations.
* Eliminate booking overlaps and automate inventory deduction.
* Provide a reusable, atomic frontend for scalability.
* Enable easy extension (chatbot → LLM, payment → real gateways).
* CDN-optimized performance for low-latency asset delivery.

---

## 🧱 Architecture Principles

### 1. **Atomic Design System**

* **Atoms**: Buttons, input fields, icons, text blocks.
* **Molecules**: Form groups, booking cards, inventory badges.
* **Organisms**: Booking panels, chatbot modules, analytics dashboards.
* **Templates**: Page-level Django templates composing organisms.
* **Pages**: Service list, booking form, admin dashboard, chatbot view.

All components stored under `/templates/components/{atoms,molecules,organisms}` and reused in pages.

### 2. **Backend Modularity**

* Each domain (appointments, services, inventory, chatbot, payments) lives in its own Django app.
* Shared utilities (notifications, analytics, auth middleware) stored in a `/core` app.
* Reusable serializers, signals, and management commands.

### 3. **CDN Integration**

* All static files (CSS, JS, media, chatbot scripts) uploaded and versioned to CDN.
* Django’s `collectstatic` configured to publish to CDN bucket.
* Leverage caching headers and compression for instant delivery.

---

## 👥 User Roles

| Role         | Description                                                                      | Access   |
| ------------ | -------------------------------------------------------------------------------- | -------- |
| **Admin**    | Full system access — manages services, staff, inventory, appointments, analytics | All      |
| **Staff**    | Limited to daily operations, appointment updates, and completion                 | Moderate |
| **Customer** | Can browse services, book appointments, view payments, chat                      | Limited  |

---

## 💡 Core Concepts

### 1. **Service → Inventory Linkage**

Each service defines its resource consumption.

| Field          | Description                          |
| -------------- | ------------------------------------ |
| Name           | Service name (e.g., “Hair Rebond”)   |
| Duration       | Duration in minutes                  |
| Price          | Service price                        |
| Required Items | Inventory items + quantity deduction |

Trigger: When appointment marked as `completed`, system deducts from inventory.

---

### 2. **Appointment & Blocking**

* Appointments have `status` (`pending`, `confirmed`, `completed`, `no-show`).
* Admin sets **max concurrent appointments per time block**.
* Blocked time ranges stored as “Blackout Windows”.
* Django signals validate availability before saving.

---

### 3. **Inventory Automation**

* Auto deduction on completion.
* Threshold notifications (below min stock).
* Admin dashboard highlights low stock & negative stock.
* Configurable “prevent completion if insufficient stock” toggle.

---

### 4. **Demo Payment Flow**

Simulated payment workflow (GCash, PayMaya, Onsite):

* Transaction generated with mock `TXN-XXXXXX` ID.
* Random or deterministic success/failure for UX testing.
* Stored as separate `Payment` model linked to appointment.

---

### 5. **Chatbot (Rule-Based)**

Simple keyword-response engine, stored in DB:

* `ChatbotRule (keyword, response)`
* API endpoint `/api/chatbot/respond`
* Optional throttling
* Modular design to later replace with LLM chatbot

---

## 📊 Analytics & Dashboard

* Revenue breakdown (daily/weekly/monthly)
* Top services chart
* Inventory usage summary
* Low-stock & threshold alerts
* Appointment volume heatmap (per day/time)

Frontend uses Chart.js (served via CDN).

---

## 🗂 Django Apps Layout (Proposal)

```
/salon_system/
│
├── core/                   # Shared utilities, auth, models
├── services/               # Service CRUD + inventory linkage
├── inventory/              # Inventory items + thresholds
├── appointments/           # Booking logic, blocking, statuses
├── payments/               # Demo payment module
├── chatbot/                # Rule-based chatbot endpoints
├── analytics/              # Dashboard & reports
├── static/                 # CDN-ready assets
├── templates/
│   ├── components/
│   │   ├── atoms/
│   │   ├── molecules/
│   │   └── organisms/
│   └── pages/
└── manage.py
```

---

## 🔒 Non-Functional Highlights

* **Transactions:** Used during completion + inventory deduction.
* **Caching:** Enabled for static assets (CDN + Django cache middleware).
* **Scalability:** Horizontal scaling via CDN & modular apps.
* **Security:** Django CSRF, hashed passwords, RBAC decorators.
* **Extensibility:** Components designed for easy LLM/chatbot/payment upgrades.

---

## ✅ MVP Acceptance Criteria

1. Customers can book a service, and system prevents overlap.
2. Admin can add/edit services and link required inventory.
3. Inventory auto-deducts when appointment marked `completed`.
4. Demo payment works and updates appointment payment status.
5. Admin sees analytics dashboard with revenue and low-stock alerts.
6. Chatbot responds to pre-defined rules.

---

## 🚀 Future Extensions

* Real GCash/PayMaya integration via APIs.
* LLM-powered chatbot (e.g., GPT-based).
* Multi-branch salon management.
* Automated reminder system (SMS/email).
* Role-based analytics (staff vs owner).

---

