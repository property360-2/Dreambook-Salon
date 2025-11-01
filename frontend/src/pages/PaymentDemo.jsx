import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';

import { useToast } from '../components/ToastProvider.jsx';
import { useBooking } from '../features/booking/BookingProvider.jsx';
import { api } from '../lib/api.js';

function formatCurrency(cents) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format((cents ?? 0) / 100);
}

export function PaymentDemo() {
  const navigate = useNavigate();
  const { paymentId } = useParams();
  const { addToast } = useToast();
  const { state, setPayment, setLastAppointment } = useBooking();

  const paymentQuery = useQuery(
    ['payment', paymentId],
    () => api.payments.getDemo(paymentId),
    {
      enabled: !state.payment || state.payment.id !== paymentId,
      onSuccess: (data) => {
        setPayment(data.payment);
        setLastAppointment(data.payment.appointment);
      },
    },
  );

  const payment =
    state.payment && state.payment.id === paymentId
      ? state.payment
      : paymentQuery.data?.payment;

  useEffect(() => {
    if (!payment && !paymentQuery.isLoading) {
      addToast({
        type: 'error',
        title: 'Payment not found',
        message: 'We could not locate that demo payment.',
      });
      navigate('/book', { replace: true });
    }
  }, [payment, paymentQuery.isLoading, addToast, navigate]);

  const updatePayment = useMutation({
    mutationFn: (status) => api.payments.updateDemo(paymentId, { status }),
  });

  if (!payment) {
    return (
      <div className="card">
        <p className="muted">Loading payment details...</p>
      </div>
    );
  }

  const handleUpdate = async (status, successMessage) => {
    try {
      const response = await updatePayment.mutateAsync(status);
      setPayment(response.payment);
      setLastAppointment(response.payment.appointment);
      addToast({ type: 'success', title: successMessage });
      navigate('/book/complete');
    } catch (error) {
      addToast({ type: 'error', title: 'Unable to update payment', message: error.message });
    }
  };

  return (
    <div className="flow-md">
      <div className="card flow-md">
        <h2 style={{ margin: 0 }}>Demo payment</h2>
        <p className="muted" style={{ margin: 0 }}>
          This flow simulates a payment confirmation. No real transaction happens.
        </p>
      </div>

      <div className="card flow-md">
        <div>
          <span className="muted label">Method</span>
          <p style={{ margin: 0, fontWeight: 600 }}>{payment.method}</p>
        </div>
        <div>
          <span className="muted label">Amount</span>
          <p style={{ margin: 0, fontWeight: 600 }}>{formatCurrency(payment.amountCents)}</p>
        </div>
        <div>
          <span className="muted label">Status</span>
          <p style={{ margin: 0, fontWeight: 600 }}>{payment.status}</p>
        </div>
        {payment.transactionId ? (
          <div>
            <span className="muted label">Transaction</span>
            <p style={{ margin: 0, fontWeight: 600 }}>{payment.transactionId}</p>
          </div>
        ) : null}
      </div>

      <div className="card flow-md">
        <button
          type="button"
          className="button"
          onClick={() => handleUpdate('PAID', 'Payment confirmed')}
          disabled={updatePayment.isPending}
        >
          Confirm payment
        </button>
        <button
          type="button"
          className="button secondary"
          onClick={() => handleUpdate('CANCELLED', 'Payment cancelled')}
          disabled={updatePayment.isPending}
        >
          Cancel payment
        </button>
      </div>
    </div>
  );
}
