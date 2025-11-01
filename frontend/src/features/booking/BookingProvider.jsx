import { createContext, useCallback, useContext, useMemo, useState } from 'react';

const BookingContext = createContext(undefined);

function createInitialState() {
  return {
    selectedService: null,
    selectedDate: '',
    selectedSlot: null,
    availability: null,
    customer: {
      name: '',
      email: '',
      phone: '',
    },
    paymentMethod: 'ONSITE',
    notes: '',
    lastAppointment: null,
    credentials: null,
    payment: null,
  };
}

export function BookingProvider({ children }) {
  const [state, setState] = useState(createInitialState);

  const reset = useCallback(() => {
    setState(createInitialState());
  }, []);

  const setService = useCallback((service) => {
    setState((prev) => ({
      ...prev,
      selectedService: service,
    }));
  }, []);

  const setDate = useCallback((date) => {
    setState((prev) => ({
      ...prev,
      selectedDate: date,
    }));
  }, []);

  const setSlot = useCallback((slot) => {
    setState((prev) => ({
      ...prev,
      selectedSlot: slot,
    }));
  }, []);

  const setAvailability = useCallback((availability) => {
    setState((prev) => ({
      ...prev,
      availability,
    }));
  }, []);

  const setCustomer = useCallback((updates) => {
    setState((prev) => ({
      ...prev,
      customer: {
        ...prev.customer,
        ...updates,
      },
    }));
  }, []);

  const setPaymentMethod = useCallback((method) => {
    setState((prev) => ({
      ...prev,
      paymentMethod: method,
    }));
  }, []);

  const setNotes = useCallback((notes) => {
    setState((prev) => ({
      ...prev,
      notes,
    }));
  }, []);

  const setLastAppointment = useCallback((appointment) => {
    setState((prev) => ({
      ...prev,
      lastAppointment: appointment,
    }));
  }, []);

  const setCredentials = useCallback((credentials) => {
    setState((prev) => ({
      ...prev,
      credentials,
    }));
  }, []);

  const setPayment = useCallback((payment) => {
    setState((prev) => ({
      ...prev,
      payment,
    }));
  }, []);

  const value = useMemo(
    () => ({
      state,
      reset,
      setService,
      setDate,
      setSlot,
      setAvailability,
      setCustomer,
      setPaymentMethod,
      setNotes,
      setLastAppointment,
      setCredentials,
      setPayment,
    }),
    [
      state,
      reset,
      setService,
      setDate,
      setSlot,
      setAvailability,
      setCustomer,
      setPaymentMethod,
      setNotes,
      setLastAppointment,
      setCredentials,
      setPayment,
    ],
  );

  return <BookingContext.Provider value={value}>{children}</BookingContext.Provider>;
}

export function useBooking() {
  const context = useContext(BookingContext);
  if (!context) {
    throw new Error('useBooking must be used within a BookingProvider');
  }
  return context;
}
