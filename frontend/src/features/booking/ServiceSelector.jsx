function formatCurrency(cents) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format((cents ?? 0) / 100);
}

export function ServiceSelector({
  services = [],
  selectedServiceId,
  onChange,
  loading = false,
}) {
  if (loading) {
    return (
      <div className="card">
        <p className="muted">Loading services...</p>
      </div>
    );
  }

  if (!services.length) {
    return (
      <div className="card">
        <p className="muted">No services are available yet. Please check back soon.</p>
      </div>
    );
  }

  const selectedService = services.find((service) => service.id === selectedServiceId);

  return (
    <div className="card flow-md">
      <div className="field">
        <label htmlFor="service-select">Service</label>
        <select
          id="service-select"
          value={selectedServiceId ?? ''}
          onChange={(event) => {
            const service = services.find((item) => item.id === event.target.value) ?? null;
            onChange?.(service);
          }}
        >
          <option value="">Select a service...</option>
          {services.map((service) => (
            <option key={service.id} value={service.id}>
              {service.name} · {service.durationMinutes} min · {formatCurrency(service.priceCents)}
            </option>
          ))}
        </select>
      </div>
      {selectedService?.description && (
        <p className="muted">{selectedService.description}</p>
      )}
    </div>
  );
}
