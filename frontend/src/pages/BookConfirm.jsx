import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';

import { useToast } from '../components/ToastProvider.jsx';
import { BookingSummary } from '../features/booking/BookingSummary.jsx';
import { useBooking } from '../features/booking/BookingProvider.jsx';
import { api } from '../lib/api.js';

export function BookConfirm() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const {
    state,
    setCustomer,
    setPaymentMethod,
    setNotes,
    setLastAppointment,
    setCredentials,
    setPayment,
  } = useBooking();

  const [localNotes, setLocalNotes] = useState(state.notes ?? '');

  useEffect(() => {
    if (!state.selectedService || !state.selectedSlot) {
      navigate('/book', { replace: true });
    }
  }, [navigate, state.selectedService, state.selectedSlot]);

  useEffect(() => {
    setLocalNotes(state.notes ?? '');
  }, [state.notes]);

  const createAppointment = useMutation({
    mutationFn: (payload) => api.appointments.create(payload),
  });

  const createDemoPayment = useMutation({
    mutationFn: (payload) => api.payments.createDemo(payload),
  });

  const isSubmitting = createAppointment.isPending || createDemoPayment.isPending;

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!state.selectedService || !state.selectedSlot) {
      addToast({
        type: 'error',
        title: 'Missing selection',
        message: 'Choose a service and time slot before confirming.',
      });
      navigate('/book');
      return;
    }

    if (!state.customer.name || !state.customer.email) {
      addToast({
        type: 'error',
        title: 'Add your details',
        message: 'Name and email are required to secure your booking.',
      });
      return;
    }

    try {
      const appointmentPayload = {
        serviceId: state.selectedService.id,
        scheduledStart: state.selectedSlot.start,
        notes: localNotes.trim() ? localNotes.trim() : undefined,
        customer: {
          name: state.customer.name.trim(),
          email: state.customer.email.trim().toLowerCase(),
          phone: state.customer.phone?.trim() || undefined,
        },
        paymentMethod: state.paymentMethod,
      };

      const appointmentResponse = await createAppointment.mutateAsync(appointmentPayload);
      const appointment = appointmentResponse.appointment;
      setLastAppointment(appointment);
      setCredentials(appointmentResponse.credentials ?? null);
      setPayment(null);
      setNotes(localNotes);

      if (state.paymentMethod === 'ONSITE') {
        addToast({
          type: 'success',
          title: 'Appointment booked',
          message: 'See you soon! We sent the details to your email.',
        });
        navigate('/book/complete');
        return;
      }

      const paymentResponse = await createDemoPayment.mutateAsync({
        appointmentId: appointment.id,
        method: state.paymentMethod,
      });

      const payment = paymentResponse.payment;
      setPayment(payment);
      addToast({
        type: 'info',
        title: 'Complete demo payment',
        message: 'Finish the mock payment to confirm your booking.',
      });
      navigate(`/payment/demo/${payment.id}`);
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Unable to confirm',
        message: error.message,
      });
    }
  };

  const handleFieldChange = (field) => (event) => {
    setCustomer({
      [field]: event.target.value,
    });
  };

  const handlePaymentChange = (event) => {
    setPaymentMethod(event.target.value);
  };

  return (
    <form className="flow-md" onSubmit={handleSubmit}>
      <div className="card flow-md">
        <h2 style={{ margin: 0 }}>Confirm your booking</h2>
        <p className="muted" style={{ margin: 0 }}>
          Double-check the details and add your contact information.
        </p>
      </div>

      <BookingSummary
        service={state.selectedService}
        slot={state.selectedSlot}
        date={state.selectedDate}
        paymentMethod={state.paymentMethod}
      />

      <div className="card flow-md">
        <div className="field">
          <label htmlFor="customer-name">Your name</label>
          <input
            id="customer-name"
            type="text"
            value={state.customer.name}
            onChange={handleFieldChange('name')}
            required
          />
        </div>
        <div className="field">
          <label htmlFor="customer-email">Email address</label>
          <input
            id="customer-email"
            type="email"
            value={state.customer.email}
            onChange={handleFieldChange('email')}
            required
          />
        </div>
        <div className="field">
          <label htmlFor="customer-phone">Phone (optional)</label>
          <input
            id="customer-phone"
            type="tel"
            value={state.customer.phone}
            onChange={handleFieldChange('phone')}
          />
        </div>
      </div>

      <div className="card flow-md">
        <fieldset className="flow-sm">
          <legend className="muted">Payment preference</legend>
          <label className="radio-option">
            <input
              type="radio"
              name="payment-method"
              value="ONSITE"
              checked={state.paymentMethod === 'ONSITE'}
              onChange={handlePaymentChange}
            />
            <span>Pay at the salon</span>
          </label>
          <label className="radio-option">
            <input
              type="radio"
              name="payment-method"
              value="DEMO_GCASH"
              checked={state.paymentMethod === 'DEMO_GCASH'}
              onChange={handlePaymentChange}
            />
            <span>Demo payment (GCash)</span>
          </label>
          <label className="radio-option">
            <input
              type="radio"
              name="payment-method"
              value="DEMO_PAYMAYA"
              checked={state.paymentMethod === 'DEMO_PAYMAYA'}
              onChange={handlePaymentChange}
            />
            <span>Demo payment (PayMaya)</span>
          </label>
        </fieldset>
      </div>

      <div className="card flow-md">
        <div className="field">
          <label htmlFor="booking-notes">Notes for the stylist (optional)</label>
          <textarea
            id="booking-notes"
            rows={4}
            value={localNotes}
            onChange={(event) => setLocalNotes(event.target.value)}
            onBlur={() => setNotes(localNotes)}
            style={{ resize: 'vertical' }}
          />
        </div>

        <div className="flow-sm">
          <button type="submit" className="button" disabled={isSubmitting}>
            {isSubmitting ? 'Processing...' : 'Confirm booking'}
          </button>
          <button
            type="button"
            className="button secondary"
            onClick={() => navigate('/book')}
            disabled={isSubmitting}
          >
            Back
          </button>
        </div>
      </div>
    </form>
  );
}
