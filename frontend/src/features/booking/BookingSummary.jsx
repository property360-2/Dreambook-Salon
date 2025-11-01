function formatDate(date) {
  if (!date) return '';
  return new Date(date).toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });
}

function formatTime(value) {
  return new Date(value).toLocaleTimeString([], {
    hour: 'numeric',
    minute: '2-digit',
  });
}

export function BookingSummary({ service, slot, date, paymentMethod }) {
  if (!service || !slot) {
    return null;
  }

  const formattedPrice = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format((service.priceCents ?? 0) / 100);

  const paymentLabel =
    paymentMethod === 'ONSITE'
      ? 'Pay at the salon'
      : paymentMethod.replace('DEMO_', '').toUpperCase();

  return (
    <div className="card flow-md">
      <h3 style={{ margin: 0 }}>Booking summary</h3>
      <div className="summary-grid">
        <div>
          <span className="muted label">Service</span>
          <p style={{ margin: 0, fontWeight: 600 }}>{service.name}</p>
          <p className="muted" style={{ margin: 0 }}>
            {service.durationMinutes} minutes - {formattedPrice}
          </p>
        </div>
        <div>
          <span className="muted label">When</span>
          <p style={{ margin: 0, fontWeight: 600 }}>
            {formatDate(date)} {formatTime(slot.start)} - {formatTime(slot.end)}
          </p>
        </div>
        <div>
          <span className="muted label">Payment</span>
          <p style={{ margin: 0, fontWeight: 600 }}>{paymentLabel}</p>
        </div>
      </div>
    </div>
  );
}
