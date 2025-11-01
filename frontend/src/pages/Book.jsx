import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';

import { useToast } from '../components/ToastProvider.jsx';
import { DatePicker } from '../features/booking/DatePicker.jsx';
import { ServiceSelector } from '../features/booking/ServiceSelector.jsx';
import { TimeSlotList } from '../features/booking/TimeSlotList.jsx';
import { useBooking } from '../features/booking/BookingProvider.jsx';
import { api } from '../lib/api.js';

export function Book() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { state, setService, setDate, setSlot, setAvailability } = useBooking();

  const servicesQuery = useQuery(['services'], () => api.services());
  const services = servicesQuery.data?.services ?? [];

  useEffect(() => {
    if (!services.length) return;
    if (!state.selectedService) {
      setService(services[0]);
      return;
    }
    const match = services.find((service) => service.id === state.selectedService.id);
    if (!match) {
      setService(services[0]);
    }
  }, [services, setService, state.selectedService]);

  const availabilityQuery = useQuery(
    ['availability', state.selectedService?.id, state.selectedDate],
    () =>
      api.appointments.available({
        serviceId: state.selectedService.id,
        date: state.selectedDate,
      }),
    {
      enabled: Boolean(state.selectedService && state.selectedDate),
      onSuccess: (data) => {
        setAvailability(data);
        if (
          state.selectedSlot &&
          !data.slots?.some((slot) => slot.start === state.selectedSlot.start)
        ) {
          setSlot(null);
        }
      },
      onError: (error) => {
        setAvailability(null);
        addToast({
          type: 'error',
          title: 'Could not load availability',
          message: error.message,
        });
      },
    },
  );

  const handleServiceChange = (service) => {
    setService(service ?? null);
    setSlot(null);
    setAvailability(null);
  };

  const handleDateChange = (value) => {
    setDate(value);
    setSlot(null);
    setAvailability(null);
  };

  const handleContinue = () => {
    if (!state.selectedService || !state.selectedSlot) {
      addToast({
        type: 'error',
        title: 'Select a slot',
        message: 'Pick a service, date, and time before continuing.',
      });
      return;
    }
    navigate('/book/confirm');
  };

  return (
    <div className="flow-md">
      <div className="card flow-md">
        <h2 style={{ margin: 0 }}>Book an appointment</h2>
        <p className="muted" style={{ margin: 0 }}>
          Choose a service, date, and time that works for you.
        </p>
      </div>

      <ServiceSelector
        services={services}
        selectedServiceId={state.selectedService?.id ?? ''}
        onChange={handleServiceChange}
        loading={servicesQuery.isLoading}
      />

      <DatePicker value={state.selectedDate} onChange={handleDateChange} />

      {state.selectedService && state.selectedDate ? (
        <TimeSlotList
          slots={state.availability?.slots ?? []}
          selectedSlot={state.selectedSlot}
          onSelect={setSlot}
          loading={availabilityQuery.isLoading}
          blockedRanges={state.availability?.blockedRanges ?? []}
          maxConcurrentAppointments={state.availability?.meta?.maxConcurrentAppointments}
        />
      ) : null}

      <div className="card">
        <button
          type="button"
          className="button"
          onClick={handleContinue}
          disabled={!state.selectedService || !state.selectedSlot}
        >
          Continue
        </button>
      </div>
    </div>
  );
}
