import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import { useBooking } from '../features/booking/BookingProvider.jsx';

function formatDateTime(value) {
  return new Date(value).toLocaleString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

export function BookComplete() {
  const navigate = useNavigate();
  const { state, reset } = useBooking();
  const appointment = state.lastAppointment;

  useEffect(() => {
    if (!appointment) {
      navigate('/book', { replace: true });
    }
  }, [appointment, navigate]);

  if (!appointment) {
    return null;
  }

  return (
    <div className="flow-md">
      <div className="card flow-md">
        <h2 style={{ margin: 0 }}>You're all set!</h2>
        <p className="muted" style={{ margin: 0 }}>
          We’ve saved your appointment and sent a confirmation email.
        </p>
      </div>

      <div className="card flow-md">
        <div>
          <span className="muted label">Appointment</span>
          <p style={{ margin: 0, fontWeight: 600 }}>{appointment.service?.name}</p>
          <p className="muted" style={{ margin: 0 }}>
            {formatDateTime(appointment.scheduledStart)} - {formatDateTime(appointment.scheduledEnd)}
          </p>
        </div>
        <div>
          <span className="muted label">Status</span>
          <p style={{ margin: 0, fontWeight: 600 }}>{appointment.status}</p>
          {state.payment && (
            <p className="muted" style={{ margin: 0 }}>
              Payment: {state.payment.status} ({state.payment.method})
            </p>
          )}
        </div>
      </div>

      {state.credentials ? (
        <div className="card flow-md">
          <h3 style={{ margin: 0 }}>Account created</h3>
          <p className="muted" style={{ margin: 0 }}>
            Use these credentials to log in next time. You can change the password later.
          </p>
          <div className="credential-block">
            <div>
              <span className="muted label">Email</span>
              <p style={{ margin: 0, fontWeight: 600 }}>{state.credentials.username}</p>
            </div>
            <div>
              <span className="muted label">Temporary password</span>
              <p style={{ margin: 0, fontWeight: 600 }}>{state.credentials.password}</p>
            </div>
          </div>
        </div>
      ) : null}

      <div className="card flow-md">
        <button
          type="button"
          className="button"
          onClick={() => {
            reset();
            navigate('/book');
          }}
        >
          Book another appointment
        </button>
      </div>
    </div>
  );
}
