import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { BookingProvider, useBooking } from './BookingProvider.jsx';

function BookingConsumer() {
  const { state, setService, reset } = useBooking();
  return (
    <div>
      <span data-testid="selected-service">{state.selectedService?.name ?? 'none'}</span>
      <span data-testid="payment-method">{state.paymentMethod}</span>
      <button
        type="button"
        onClick={() => setService({ id: 'svc_1', name: 'Signature Cut', priceCents: 3200 })}
      >
        choose
      </button>
      <button type="button" onClick={reset}>
        reset
      </button>
    </div>
  );
}

describe('BookingProvider', () => {
  it('provides initial state and updates selections', () => {
    render(
      <BookingProvider>
        <BookingConsumer />
      </BookingProvider>,
    );

    expect(screen.getByTestId('selected-service').textContent).toBe('none');
    expect(screen.getByTestId('payment-method').textContent).toBe('ONSITE');

    fireEvent.click(screen.getByText('choose'));
    expect(screen.getByTestId('selected-service').textContent).toBe('Signature Cut');

    fireEvent.click(screen.getByText('reset'));
    expect(screen.getByTestId('selected-service').textContent).toBe('none');
  });
});
