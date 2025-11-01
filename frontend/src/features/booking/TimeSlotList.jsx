function formatTime(value) {
  return new Date(value).toLocaleTimeString([], {
    hour: 'numeric',
    minute: '2-digit',
  });
}

function formatRange(slot) {
  return `${formatTime(slot.start)} – ${formatTime(slot.end)}`;
}

export function TimeSlotList({
  slots = [],
  selectedSlot,
  onSelect,
  loading = false,
  blockedRanges = [],
  maxConcurrentAppointments,
}) {
  if (loading) {
    return (
      <div className="card">
        <p className="muted">Checking availability...</p>
      </div>
    );
  }

  return (
    <div className="card flow-md">
      <div>
        <h3 style={{ margin: 0 }}>Available times</h3>
        {maxConcurrentAppointments && (
          <p className="muted">
            Up to {maxConcurrentAppointments}{' '}
            {maxConcurrentAppointments > 1 ? 'appointments' : 'appointment'} per slot.
          </p>
        )}
      </div>

      {slots.length > 0 ? (
        <div className="slot-grid">
          {slots.map((slot) => {
            const isSelected = selectedSlot?.start === slot.start;
            return (
              <button
                key={slot.start}
                type="button"
                className={`slot-button ${isSelected ? 'selected' : ''}`}
                onClick={() => onSelect?.(slot)}
              >
                <span className="slot-time">{formatRange(slot)}</span>
                <span className="slot-capacity">
                  {slot.remainingCapacity} spot{slot.remainingCapacity === 1 ? '' : 's'} left
                </span>
              </button>
            );
          })}
        </div>
      ) : (
        <div className="empty-state">
          <p className="muted">
            No open slots for this date. Try another day or contact the salon directly.
          </p>
          {blockedRanges?.length > 0 && (
            <ul className="muted" style={{ margin: 0, paddingLeft: '1.25rem' }}>
              {blockedRanges.map((range) => (
                <li key={range.id}>
                  {new Date(range.startsAt).toLocaleString()} –{' '}
                  {new Date(range.endsAt).toLocaleString()}{' '}
                  {range.reason ? `(${range.reason})` : ''}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
