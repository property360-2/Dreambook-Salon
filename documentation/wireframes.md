    # 04-wireframes.md

# 🎯 Wireframes & Component Layouts — Key Pages (ASCII + React skeletons)

Below are **textual wireframes** (ASCII) and **React component skeletons** (Tailwind-style) for the most important pages: Home, Services, Service Detail, Booking flow (pick slot + confirm), Demo Payment page, Admin Dashboard, Admin Services, Admin Inventory, and the Chatbot widget.  
Use these as ready-to-drop templates for Codex to expand into full pages.

---

> Implementation notes (quick)
>
> - Tailwind classes are used in the React skeletons for styling; replace with your preferred CSS if needed.
> - Components are intentionally minimal and focused on structure & data flow (props, hooks, API calls).
> - API endpoints referenced are examples matching earlier docs.

---

# 1) Home / Landing

```

+-------------------------------------------------------------+
| NAVBAR: Logo | Services | Book | Login/Register | Admin      |
+-------------------------------------------------------------+
| HERO: Big headline, short description, CTA "Book Now"       |
| [Hero image / carousel]                                     |
+-------------------------------------------------------------+
| FEATURED SERVICES (cards)                                   |
| [ Service Card ] [ Service Card ] [ Service Card ]          |
+-------------------------------------------------------------+
| ChatbotWidget (floating)                                    |
+-------------------------------------------------------------+
| FOOTER                                                      |
+-------------------------------------------------------------+

```

## Component tree

- HomePage
  - Hero
  - FeaturedServices (ServiceCard)
  - Testimonials (optional)
  - ChatbotWidget

## React skeleton (`HomePage.jsx`)

```jsx
import React, { useEffect, useState } from "react";

export default function HomePage() {
  const [services, setServices] = useState([]);

  useEffect(() => {
    fetch("/api/services?featured=true")
      .then((res) => res.json())
      .then((data) => setServices(data))
      .catch(console.error);
  }, []);

  return (
    <main className="min-h-screen bg-gray-50">
      <nav className="flex items-center justify-between p-4">
        <div className="text-2xl font-bold">Dream Salon</div>
        <div>
          <a href="/services" className="mr-4">
            Services
          </a>
          <a href="/book" className="btn">
            Book
          </a>
        </div>
      </nav>

      <section className="px-6 py-12 text-center">
        <h1 className="text-4xl font-extrabold mb-3">Look good. Feel great.</h1>
        <p className="text-gray-600 mb-6">
          Book appointments, track inventory, and manage your salon easily.
        </p>
        <a
          href="/book"
          className="inline-block px-6 py-3 bg-indigo-600 text-white rounded-lg"
        >
          Book Now
        </a>
      </section>

      <section className="px-6 py-8">
        <h2 className="text-xl font-semibold mb-4">Featured Services</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {services.map((s) => (
            <article key={s.id} className="p-4 bg-white rounded shadow">
              <h3 className="font-bold">{s.name}</h3>
              <p className="text-sm text-gray-600">
                ₱{s.price} • {s.duration} min
              </p>
              <a
                href={`/service/${s.id}`}
                className="mt-3 inline-block text-indigo-600"
              >
                View
              </a>
            </article>
          ))}
        </div>
      </section>

      <div id="chatbot-root" className="fixed bottom-6 right-6"></div>
    </main>
  );
}
```

---

# 2) Services Catalog

```
+---------------------------+---------------------------------+
| FILTERS (left)           | SERVICES GRID (right)           |
| - Category               | +----------------------------+  |
| - Duration               | | ServiceCard                |  |
| - Price                  | +----------------------------+  |
|                         | | ServiceCard                |  |
+---------------------------+-------------------------------+
```

## Key API

- `GET /api/services?category=&minDuration=&maxPrice=`

## React skeleton (`ServicesPage.jsx`)

```jsx
import React, { useEffect, useState } from "react";

export default function ServicesPage() {
  const [services, setServices] = useState([]);
  useEffect(() => {
    fetch("/api/services")
      .then((r) => r.json())
      .then(setServices);
  }, []);
  return (
    <div className="p-6">
      <div className="grid grid-cols-4 gap-6">
        <aside className="col-span-1 bg-white p-4 rounded shadow">
          <h4 className="font-semibold mb-2">Filters</h4>
          {/* Filter controls */}
        </aside>

        <div className="col-span-3">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {services.map((s) => (
              <div key={s.id} className="p-4 bg-white rounded shadow">
                <h3 className="font-bold">{s.name}</h3>
                <p className="text-sm text-gray-600">₱{s.price}</p>
                <div className="mt-3">
                  <a href={`/service/${s.id}`} className="text-indigo-600">
                    Details
                  </a>
                  <a
                    href={`/book?serviceId=${s.id}`}
                    className="ml-4 text-green-600"
                  >
                    Book
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

# 3) Service Detail

```
+-------------------------------------------------------------+
| Back | Service Title                | Price | Duration      |
+-------------------------------------------------------------+
| Image / gallery                                              |
| Description                                                   |
| Required Inventory (admin-only view: show quantities)         |
| [ Book Now ]                                                  |
+-------------------------------------------------------------+
```

## API

- `GET /api/services/:id` (includes requiredItems if admin view)

## React skeleton (`ServiceDetail.jsx`)

```jsx
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

export default function ServiceDetail() {
  const { id } = useParams();
  const [service, setService] = useState(null);

  useEffect(() => {
    fetch(`/api/services/${id}`)
      .then((r) => r.json())
      .then(setService);
  }, [id]);

  if (!service) return <div className="p-6">Loading...</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold">{service.name}</h1>
          <p className="text-gray-600">
            ₱{service.price} • {service.duration} min
          </p>
        </div>
        <a href={`/book?serviceId=${service.id}`} className="btn">
          Book Now
        </a>
      </div>

      <section className="mt-6 bg-white p-4 rounded shadow">
        <h3 className="font-semibold">Description</h3>
        <p className="mt-2 text-gray-700">
          {service.description || "No description."}
        </p>

        {service.requiredItems?.length > 0 && (
          <div className="mt-4">
            <h4 className="font-semibold">Required Inventory</h4>
            <ul className="mt-2 list-disc ml-5 text-sm text-gray-600">
              {service.requiredItems.map((item) => (
                <li key={item.id}>
                  {item.inventory.name} — {item.quantity}{" "}
                  {item.inventory.unit || ""}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>
    </div>
  );
}
```

---

# 4) Booking Flow — Pick Slot (`/book`)

```
+-------------------------------------------------------------+
| Step 1: Choose Service (dropdown / prefilled)               |
+-------------------------------------------------------------+
| Date Picker (calendar)                                      |
+-------------------------------------------------------------+
| Available Times (list/grid)                                 |
| [ 09:00 ] [ 09:30 ] [ 10:00 - FULL ] [ ... ]                |
+-------------------------------------------------------------+
| Footer: Selected slot summary | Next: Confirm               |
+-------------------------------------------------------------+
```

## API

- `GET /api/appointments/available?serviceId=&date=`
- `POST /api/appointments` (body: userId, serviceId, start, end, notes)

## React skeleton (`BookingPickSlot.jsx`)

```jsx
import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

export default function BookingPickSlot() {
  const q = new URLSearchParams(useLocation().search);
  const preService = q.get("serviceId");
  const [serviceId, setServiceId] = useState(preService || "");
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [slots, setSlots] = useState([]);
  const [selected, setSelected] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!serviceId) return;
    fetch(`/api/appointments/available?serviceId=${serviceId}&date=${date}`)
      .then((r) => r.json())
      .then(setSlots);
  }, [serviceId, date]);

  const handleNext = () => {
    if (!selected) return alert("Pick a time slot");
    navigate(`/book/confirm?serviceId=${serviceId}&start=${selected.start}`);
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h2 className="text-xl font-semibold mb-4">Book a Service</h2>
      <div className="mb-4">
        <label className="block text-sm font-medium">Service</label>
        <select
          value={serviceId}
          onChange={(e) => setServiceId(e.target.value)}
          className="mt-1 w-full p-2 border rounded"
        >
          <option value="">Choose a service</option>
          {/* TODO: populate services */}
        </select>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium">Date</label>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="mt-1 p-2 border rounded"
        />
      </div>

      <div>
        <h3 className="font-semibold mb-2">Available Slots</h3>
        <div className="grid grid-cols-3 gap-2">
          {slots.length === 0 && (
            <div className="text-sm text-gray-500 col-span-3">
              No slots available
            </div>
          )}
          {slots.map((slot) => (
            <button
              key={slot.start}
              onClick={() => setSelected(slot)}
              className={`p-2 border rounded ${
                selected?.start === slot.start ? "ring-2 ring-indigo-400" : ""
              }`}
              disabled={slot.full}
            >
              {slot.label} {slot.full ? "(Full)" : ""}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-6 flex justify-end">
        <button
          onClick={handleNext}
          className="px-5 py-2 bg-indigo-600 text-white rounded"
        >
          Next: Confirm
        </button>
      </div>
    </div>
  );
}
```

---

# 5) Booking Confirm + Checkout (`/book/confirm`)

```
+-------------------------------------------------------------+
| Summary: Service | Date | Time | Price                      |
+-------------------------------------------------------------+
| Customer Info (prefill if logged in)                        |
| Payment Method: [GCash Demo] [PayMaya Demo] [Pay on Site]   |
+-------------------------------------------------------------+
| [ Confirm & Pay ]  or  [ Confirm (Pay on Site) ]            |
+-------------------------------------------------------------+
```

## API

- `POST /api/appointments` → returns appointment & optionally payment placeholder
- `POST /api/payments/demo` → simulate payment

## React skeleton (`BookingConfirm.jsx`)

```jsx
import React, { useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

export default function BookingConfirm() {
  const [params] = useSearchParams();
  const serviceId = params.get("serviceId");
  const start = params.get("start");
  const [method, setMethod] = useState("onsite");
  const navigate = useNavigate();

  const handleConfirm = async () => {
    // create appointment
    const appointmentRes = await fetch("/api/appointments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ serviceId, start }),
    });
    const appointment = await appointmentRes.json();

    if (method === "onsite") {
      alert("Appointment confirmed (pay on site)");
      navigate("/appointments");
      return;
    }

    // create demo payment
    const payRes = await fetch("/api/payments/demo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ appointmentId: appointment.id, method }),
    });
    const payment = await payRes.json();
    // navigate to payment page or show receipt
    navigate(`/payment/demo/${payment.id}`);
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h2 className="text-xl font-semibold mb-4">Confirm Booking</h2>
      <div className="bg-white p-4 rounded shadow">
        <p>Service: {serviceId}</p>
        <p>Start: {start}</p>
        <div className="mt-4">
          <label className="block text-sm">Payment Method</label>
          <select
            value={method}
            onChange={(e) => setMethod(e.target.value)}
            className="mt-1 p-2 border rounded"
          >
            <option value="onsite">Pay on Site</option>
            <option value="gcash">GCash (Demo)</option>
            <option value="paymaya">PayMaya (Demo)</option>
          </select>
        </div>
        <div className="mt-4 flex justify-end">
          <button
            onClick={handleConfirm}
            className="px-4 py-2 bg-indigo-600 text-white rounded"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

# 6) Demo Payment Page (`/payment/demo/:paymentId`)

```
+-------------------------------------------------------------+
| Payment Method: GCash (Demo)    Amount: ₱1500              |
+-------------------------------------------------------------+
| [ Confirm Payment ]      [ Simulate Failure ]               |
| After Confirm: show mock txnId & "Payment successful"       |
| Or show "Payment failed" and option retry                   |
+-------------------------------------------------------------+
```

## API

- `POST /api/payments/demo` (body: appointmentId, method) → returns payment { id, transactionId, status }

## React skeleton (`DemoPayment.jsx`)

```jsx
import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

export default function DemoPayment() {
  const { paymentId } = useParams();
  const [payment, setPayment] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`/api/payments/${paymentId}`)
      .then((r) => r.json())
      .then(setPayment);
  }, [paymentId]);

  if (!payment) return <div className="p-6">Loading payment...</div>;

  const confirm = async (simulateFailure = false) => {
    // For demo: call endpoint to finalize
    const res = await fetch("/api/payments/demo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        appointmentId: payment.appointmentId,
        method: payment.method,
        forceFail: simulateFailure,
      }),
    });
    const data = await res.json();
    if (data.status === "paid") {
      alert("Payment success — txn: " + data.transactionId);
      navigate("/appointments");
    } else {
      alert("Payment failed. Try again.");
      setPayment(data);
    }
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h2 className="text-lg font-semibold">Demo Payment</h2>
      <div className="bg-white p-4 rounded shadow mt-4">
        <p>Method: {payment.method}</p>
        <p>Amount: ₱{payment.amount}</p>
        <div className="mt-4 flex gap-2">
          <button
            onClick={() => confirm(false)}
            className="px-4 py-2 bg-green-600 text-white rounded"
          >
            Confirm Payment
          </button>
          <button
            onClick={() => confirm(true)}
            className="px-4 py-2 bg-red-500 text-white rounded"
          >
            Simulate Failure
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

# 7) Admin Dashboard

```
+-------------------------------------------------------------+
| Topbar: Admin | Quick actions: Add Service | Add Inventory   |
+-------------------------------------------------------------+
| KPI row: Revenue | Appointments Today | Low-Stock Count     |
+-------------------------------------------------------------+
| Left: Upcoming Appointments (table)    Right: Charts        |
| - list of appointments with quick complete action           |
+-------------------------------------------------------------+
| Bottom: Low-stock Items (click to go to Inventory page)    |
+-------------------------------------------------------------+
```

## API

- `GET /api/analytics/revenue?from=&to=`
- `GET /api/appointments?date=today`
- `GET /api/analytics/low-stock`

## React skeleton (`AdminDashboard.jsx`)

```jsx
import React, { useEffect, useState } from "react";

export default function AdminDashboard() {
  const [kpis, setKpis] = useState({});
  const [appointments, setAppointments] = useState([]);
  const [lowStock, setLowStock] = useState([]);

  useEffect(() => {
    fetch("/api/analytics/revenue")
      .then((r) => r.json())
      .then((data) => setKpis(data));
    fetch("/api/appointments?date=today")
      .then((r) => r.json())
      .then(setAppointments);
    fetch("/api/analytics/low-stock")
      .then((r) => r.json())
      .then(setLowStock);
  }, []);

  return (
    <div className="p-6">
      <header className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>
        <div>
          <a href="/admin/services" className="mr-3">
            Services
          </a>
          <a href="/admin/inventory" className="btn">
            Inventory
          </a>
        </div>
      </header>

      <section className="grid grid-cols-3 gap-4 mt-6">
        <div className="p-4 bg-white rounded shadow">
          <h3 className="text-sm text-gray-500">Revenue (30d)</h3>
          <div className="text-xl font-semibold">₱{kpis.revenue || 0}</div>
        </div>
        <div className="p-4 bg-white rounded shadow">
          <h3 className="text-sm text-gray-500">Appointments Today</h3>
          <div className="text-xl font-semibold">{appointments.length}</div>
        </div>
        <div className="p-4 bg-white rounded shadow">
          <h3 className="text-sm text-gray-500">Low Stock</h3>
          <div className="text-xl font-semibold">{lowStock.length}</div>
        </div>
      </section>

      <section className="mt-6 grid grid-cols-2 gap-6">
        <div className="bg-white p-4 rounded shadow">
          <h3 className="font-semibold">Upcoming Appointments</h3>
          <ul className="mt-3 divide-y">
            {appointments.map((a) => (
              <li key={a.id} className="py-2 flex justify-between">
                <div>
                  <div className="font-medium">{a.service.name}</div>
                  <div className="text-sm text-gray-500">
                    {new Date(a.start).toLocaleString()}
                  </div>
                </div>
                <div>
                  <button className="px-3 py-1 bg-green-600 text-white rounded mr-2">
                    Complete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white p-4 rounded shadow">
          <h3 className="font-semibold">Top Services</h3>
          {/* chart or list */}
        </div>
      </section>
    </div>
  );
}
```

---

# 8) Admin Services (CRUD + Link Inventory)

```
+-------------------------------------------------------------+
| Services Table: [Add Service] [Import CSV]                  |
| Columns: Name | Price | Duration | Linked Items | Actions   |
+-------------------------------------------------------------+
| Modal: Add/Edit Service                                     |
| - Name, Price, Duration, Description                        |
| - ServiceInventoryEditor: add rows -> select inventory + qty |
+-------------------------------------------------------------+
```

## API

- `GET /api/services`
- `POST /api/services`
- `POST /api/services/:id/inventory`

## React skeleton (`AdminServices.jsx`)

```jsx
import React, { useEffect, useState } from "react";

export default function AdminServices() {
  const [services, setServices] = useState([]);
  useEffect(() => {
    fetch("/api/services")
      .then((r) => r.json())
      .then(setServices);
  }, []);
  return (
    <div className="p-6">
      <header className="flex justify-between items-center">
        <h1 className="text-xl font-bold">Services</h1>
        <button className="btn">Add Service</button>
      </header>

      <table className="w-full mt-4 bg-white rounded shadow">
        <thead className="text-left">
          <tr>
            <th className="p-3">Name</th>
            <th>Price</th>
            <th>Duration</th>
            <th>Linked Items</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {services.map((s) => (
            <tr key={s.id}>
              <td className="p-3">{s.name}</td>
              <td>₱{s.price}</td>
              <td>{s.duration} min</td>
              <td>{s.requiredItems?.length || 0}</td>
              <td>
                <button className="text-indigo-600">Edit</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

# 9) Admin Inventory

```
+-------------------------------------------------------------+
| Inventory Table: Name | Stock | Unit | Threshold | Actions  |
+-------------------------------------------------------------+
| Click item -> Inventory Log (audit), Manual add stock modal |
+-------------------------------------------------------------+
```

## API

- `GET /api/inventory`
- `PUT /api/inventory/:id`
- `GET /api/inventory/logs?inventoryId=`

## React skeleton (`AdminInventory.jsx`)

```jsx
import React, { useEffect, useState } from "react";

export default function AdminInventory() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    fetch("/api/inventory")
      .then((r) => r.json())
      .then(setItems);
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold">Inventory</h1>
      <table className="w-full mt-4 bg-white rounded shadow">
        <thead>
          <tr>
            <th className="p-3">Name</th>
            <th>Stock</th>
            <th>Unit</th>
            <th>Threshold</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((i) => (
            <tr key={i.id}>
              <td className="p-3">{i.name}</td>
              <td>{i.stock}</td>
              <td>{i.unit || "-"}</td>
              <td>{i.threshold || "-"}</td>
              <td>
                <a href={`/admin/inventory/${i.id}`}>View</a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

# 10) Chatbot Widget (Floating)

```
+----------------------------------+
|  Chat (floating bubble)          |
+----------------------------------+
|  [Message list]                  |
|  Customer: "How much is rebond?" |
|  Bot: "Rebond is ₱1500..."       |
|  Quick action: [Book Rebond]     |
+----------------------------------+
| Input box [ type message ] [send]|
+----------------------------------+
```

## API

- `POST /api/chatbot/message` (body: { message }) → reply { reply, actions[] }

## React skeleton (`ChatbotWidget.jsx`)

```jsx
import React, { useState } from "react";

export default function ChatbotWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { from: "bot", text: "Hi! Need help booking?" },
  ]);
  const [input, setInput] = useState("");

  const send = async () => {
    if (!input.trim()) return;
    const userMsg = { from: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    const res = await fetch("/api/chatbot/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }),
    });
    const data = await res.json();
    setMessages((prev) => [...prev, { from: "bot", text: data.reply }]);
    // optionally handle data.actions
  };

  return (
    <div className="fixed right-6 bottom-6">
      {open && (
        <div className="w-80 bg-white shadow-lg rounded flex flex-col overflow-hidden">
          <div className="p-3 bg-indigo-600 text-white">Chat with us</div>
          <div className="p-3 flex-1 overflow-auto">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`mb-2 ${
                  m.from === "bot" ? "text-left" : "text-right"
                }`}
              >
                <div
                  className={`inline-block px-3 py-2 rounded ${
                    m.from === "bot" ? "bg-gray-100" : "bg-indigo-100"
                  }`}
                >
                  {m.text}
                </div>
              </div>
            ))}
          </div>

          <div className="p-2 border-t">
            <div className="flex">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="flex-1 p-2 border rounded"
                placeholder="Ask about services..."
              />
              <button
                onClick={send}
                className="ml-2 px-3 bg-indigo-600 text-white rounded"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}

      <button
        onClick={() => setOpen((o) => !o)}
        className="w-14 h-14 rounded-full bg-indigo-600 text-white shadow-lg flex items-center justify-center"
      >
        💬
      </button>
    </div>
  );
}
```

---
