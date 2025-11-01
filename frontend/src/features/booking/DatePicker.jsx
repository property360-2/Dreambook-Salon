function todayISO() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function DatePicker({ value, onChange, minDate }) {
  const min = minDate ?? todayISO();

  return (
    <div className="card flow-md">
      <div className="field">
        <label htmlFor="booking-date">Preferred date</label>
        <input
          id="booking-date"
          type="date"
          value={value ?? ''}
          min={min}
          onChange={(event) => onChange?.(event.target.value)}
        />
      </div>
      <p className="muted">We’ll show open slots once you pick a day.</p>
    </div>
  );
}
