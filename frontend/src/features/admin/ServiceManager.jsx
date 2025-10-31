import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { api } from '../../lib/api.js';
import { useAuth } from '../../hooks/useAuth.js';

const serviceDefaults = {
  name: '',
  description: '',
  durationMinutes: 60,
  priceCents: 0,
  isActive: true,
};

const linkDefaults = {
  serviceId: '',
  inventoryId: '',
  quantity: 1,
};

const peso = new Intl.NumberFormat('en-PH', {
  style: 'currency',
  currency: 'PHP',
});

export function ServiceManager() {
  const { token, user } = useAuth();
  const isAdmin = user?.role === 'ADMIN';
  const queryClient = useQueryClient();
  const [serviceError, setServiceError] = useState(null);
  const [linkError, setLinkError] = useState(null);

  const servicesQuery = useQuery({
    queryKey: ['services', { scope: isAdmin ? 'admin' : 'public' }],
    queryFn: () =>
      api.services({
        includeInactive: isAdmin,
        token,
      }),
    enabled: Boolean(isAdmin),
  });

  const inventoryQuery = useQuery({
    queryKey: ['inventory'],
    queryFn: () => api.inventory.list(token),
    enabled: Boolean(token && isAdmin),
  });

  const {
    register: registerService,
    handleSubmit: handleServiceSubmit,
    reset: resetServiceForm,
  } = useForm({
    defaultValues: serviceDefaults,
  });

  const {
    register: registerLink,
    handleSubmit: handleLinkSubmit,
    reset: resetLinkForm,
  } = useForm({
    defaultValues: linkDefaults,
  });

  const createServiceMutation = useMutation({
    mutationFn: (values) =>
      api.createService(token, {
        name: values.name.trim(),
        description: values.description?.trim() || undefined,
        durationMinutes: Number(values.durationMinutes),
        priceCents: Number(values.priceCents),
        isActive: Boolean(values.isActive),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['services'] });
      resetServiceForm(serviceDefaults);
      setServiceError(null);
    },
    onError: (err) => {
      setServiceError(err.message ?? 'Unable to create service');
    },
  });

  const linkMutation = useMutation({
    mutationFn: (values) =>
      api.linkServiceInventory(token, values.serviceId, {
        inventoryId: values.inventoryId,
        quantity: Number(values.quantity),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['services'] });
      setLinkError(null);
      resetLinkForm(linkDefaults);
    },
    onError: (err) => {
      setLinkError(err.message ?? 'Unable to link inventory item');
    },
  });

  const unlinkMutation = useMutation({
    mutationFn: ({ serviceId, inventoryId }) =>
      api.unlinkServiceInventory(token, serviceId, inventoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['services'] });
    },
    onError: (err) => {
      setLinkError(err.message ?? 'Unable to remove inventory link');
    },
  });

  const onCreateService = (values) => createServiceMutation.mutate(values);
  const onLinkInventory = (values) => linkMutation.mutate(values);

  const handleUnlink = (serviceId, inventoryId) => {
    unlinkMutation.mutate({ serviceId, inventoryId });
  };

  if (!isAdmin) {
    return null;
  }

  const services = servicesQuery.data?.services ?? [];
  const inventory = inventoryQuery.data?.inventory ?? [];

  return (
    <section className="card">
      <header style={{ marginBottom: '1rem' }}>
        <h2 style={{ margin: 0 }}>Service catalog</h2>
        <p className="muted" style={{ margin: 0 }}>
          Create services and define the inventory required per appointment.
        </p>
      </header>

      <form
        className="form"
        onSubmit={handleServiceSubmit(onCreateService)}
        noValidate
        style={{ marginBottom: '2rem' }}
      >
        <h3 style={{ marginTop: 0 }}>Create service</h3>

        <div className="field">
          <label htmlFor="service-name">Name</label>
          <input
            id="service-name"
            type="text"
            {...registerService('name', { required: 'Name is required' })}
          />
        </div>

        <div className="field">
          <label htmlFor="service-description">Description</label>
          <textarea
            id="service-description"
            rows={2}
            {...registerService('description')}
          />
        </div>

        <div
          style={{
            display: 'grid',
            gap: '0.75rem',
            gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
          }}
        >
          <div className="field">
            <label htmlFor="service-duration">Duration (minutes)</label>
            <input
              id="service-duration"
              type="number"
              min={15}
              step={15}
              {...registerService('durationMinutes', { valueAsNumber: true })}
            />
          </div>
          <div className="field">
            <label htmlFor="service-price">Price (PHP cents)</label>
            <input
              id="service-price"
              type="number"
              min={0}
              step={100}
              {...registerService('priceCents', { valueAsNumber: true })}
            />
          </div>
          <div
            className="field"
            style={{ flexDirection: 'row', alignItems: 'center', gap: '0.5rem' }}
          >
            <input
              id="service-active"
              type="checkbox"
              {...registerService('isActive')}
            />
            <label htmlFor="service-active">Active</label>
          </div>
        </div>

        {serviceError && <p className="error">{serviceError}</p>}

        <button
          className="button"
          type="submit"
          disabled={createServiceMutation.isPending}
          style={{ alignSelf: 'flex-start' }}
        >
          Create service
        </button>
      </form>

      <form
        className="form"
        onSubmit={handleLinkSubmit(onLinkInventory)}
        noValidate
        style={{ marginBottom: '2rem' }}
      >
        <h3 style={{ marginTop: 0 }}>Link inventory to service</h3>

        <div className="field">
          <label htmlFor="link-service">Service</label>
          <select
            id="link-service"
            {...registerLink('serviceId', { required: 'Service is required' })}
          >
            <option value="">Select service</option>
            {services.map((service) => (
              <option key={service.id} value={service.id}>
                {service.name}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="link-inventory">Inventory item</label>
          <select
            id="link-inventory"
            {...registerLink('inventoryId', {
              required: 'Inventory item is required',
            })}
          >
            <option value="">Select inventory item</option>
            {inventory.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="link-quantity">Quantity per service</label>
          <input
            id="link-quantity"
            type="number"
            min={1}
            step={1}
            {...registerLink('quantity', { valueAsNumber: true })}
          />
        </div>

        {linkError && <p className="error">{linkError}</p>}

        <button
          className="button"
          type="submit"
          disabled={linkMutation.isPending}
          style={{ alignSelf: 'flex-start' }}
        >
          Attach inventory
        </button>
      </form>

      <div>
        <h3 style={{ marginBottom: '0.75rem' }}>Service overview</h3>
        {servicesQuery.isLoading && (
          <p className="muted">Loading services...</p>
        )}
        {servicesQuery.isError && (
          <p className="error">
            Failed to load services: {servicesQuery.error?.message}
          </p>
        )}

        {!servicesQuery.isLoading &&
          !servicesQuery.isError &&
          services.length === 0 && <p className="muted">No services yet.</p>}

        {!servicesQuery.isLoading &&
          !servicesQuery.isError &&
          services.length > 0 && (
            <div className="service-grid">
              {services.map((service) => (
                <article className="service-card" key={service.id}>
                  <header>
                    <h3>{service.name}</h3>
                    <p className="muted" style={{ margin: 0 }}>
                      {service.durationMinutes} min -{' '}
                      {peso.format(service.priceCents / 100)}
                    </p>
                    <p className="muted" style={{ margin: 0 }}>
                      Status: {service.isActive ? 'Active' : 'Inactive'}
                    </p>
                  </header>

                  {service.description && (
                    <p className="muted">{service.description}</p>
                  )}

                  <section>
                    <h4 style={{ marginBottom: '0.5rem' }}>Inventory needed</h4>
                    {service.inventoryRequirements.length === 0 && (
                      <p className="muted">No inventory linked yet.</p>
                    )}
                    {service.inventoryRequirements.length > 0 && (
                      <ul style={{ paddingLeft: '1.2rem' }}>
                        {service.inventoryRequirements.map((link) => (
                          <li key={link.inventoryId}>
                            <strong>{link.inventory.name}</strong> - use{' '}
                            {link.quantity} {link.inventory.unit ?? ''}
                            <button
                              type="button"
                              className="button secondary"
                              style={{ marginLeft: '0.5rem' }}
                              onClick={() =>
                                handleUnlink(service.id, link.inventoryId)
                              }
                            >
                              Remove
                            </button>
                          </li>
                        ))}
                      </ul>
                    )}
                  </section>
                </article>
              ))}
            </div>
          )}
      </div>
    </section>
  );
}
