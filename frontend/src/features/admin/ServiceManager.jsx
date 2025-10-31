import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { api } from '../../lib/api.js';
import { useAuth } from '../../hooks/useAuth.js';
import { useToast } from '../../components/ToastProvider.jsx';
import { ConfirmDialog } from '../../components/ConfirmDialog.jsx';

const serviceDefaults = {
  name: '',
  description: '',
  durationMinutes: 60,
  pricePesos: 0,
  imageUrl: '',
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
  const [confirmRemoval, setConfirmRemoval] = useState(null);
  const [isUploadingImage, setIsUploadingImage] = useState(false);
  const { addToast } = useToast();

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
    formState: { errors: serviceErrors },
    setValue,
    watch,
  } = useForm({
    defaultValues: serviceDefaults,
  });
  const imageUrlValue = watch('imageUrl');

  const {
    register: registerLink,
    handleSubmit: handleLinkSubmit,
    reset: resetLinkForm,
    formState: { errors: linkErrors },
  } = useForm({
    defaultValues: linkDefaults,
  });

  const createServiceMutation = useMutation({
    mutationFn: (values) =>
      api.createService(token, {
        name: values.name.trim(),
        description: values.description?.trim() || undefined,
        durationMinutes: Number(values.durationMinutes),
        priceCents: Math.round(Number(values.pricePesos ?? 0) * 100),
        imageUrl: values.imageUrl?.trim() ? values.imageUrl.trim() : undefined,
        isActive: Boolean(values.isActive),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['services'] });
      resetServiceForm(serviceDefaults);
      setServiceError(null);
      addToast({
        type: 'success',
        title: 'Service saved',
        message: 'The service was saved successfully.',
      });
    },
    onError: (err) => {
      addToast({
        type: 'error',
        title: 'Unable to save service',
        message: err.message ?? 'Something went wrong.',
      });
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
      addToast({
        type: 'success',
        title: 'Inventory linked',
        message: 'Inventory requirement saved for the service.',
      });
    },
    onError: (err) => {
      addToast({
        type: 'error',
        title: 'Unable to link inventory',
        message: err.message ?? 'Something went wrong.',
      });
      setLinkError(err.message ?? 'Unable to link inventory item');
    },
  });

  const unlinkMutation = useMutation({
    mutationFn: ({ serviceId, inventoryId }) =>
      api.unlinkServiceInventory(token, serviceId, inventoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['services'] });
      addToast({
        type: 'success',
        title: 'Inventory link removed',
        message: 'The service no longer requires that inventory item.',
      });
      setConfirmRemoval(null);
    },
    onError: (err) => {
      addToast({
        type: 'error',
        title: 'Unable to remove link',
        message: err.message ?? 'Something went wrong.',
      });
      setLinkError(err.message ?? 'Unable to remove inventory link');
      setConfirmRemoval(null);
    },
  });

  const services = servicesQuery.data?.services ?? [];
  const inventory = inventoryQuery.data?.inventory ?? [];
  const handleImageChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    if (!file.type.startsWith('image/')) {
      addToast({
        type: 'error',
        title: 'Unsupported file',
        message: 'Please select a valid image file (JPG or PNG).',
      });
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      addToast({
        type: 'error',
        title: 'File too large',
        message: 'Images must be 5 MB or smaller.',
      });
      return;
    }

    if (!token) {
      addToast({
        type: 'error',
        title: 'Not authenticated',
        message: 'You need to sign in again to upload images.',
      });
      return;
    }

    const inputElement = event.target;
    const reader = new FileReader();
    reader.onload = async () => {
      try {
        const base64 = reader.result;
        const response = await api.uploads.serviceImage(token, base64);
        setValue('imageUrl', response.url, { shouldDirty: true });
        addToast({
          type: 'success',
          title: 'Image uploaded',
          message: 'The image was uploaded successfully.',
        });
      } catch (err) {
        addToast({
          type: 'error',
          title: 'Upload failed',
          message: err.message ?? 'Unable to upload image right now.',
        });
      } finally {
        setIsUploadingImage(false);
      }
    };
    reader.onerror = () => {
      setIsUploadingImage(false);
      addToast({
        type: 'error',
        title: 'Upload failed',
        message: 'Could not read the selected file.',
      });
    };
    reader.onloadend = () => {
      inputElement.value = '';
    };
    setIsUploadingImage(true);
    reader.readAsDataURL(file);
  };

  const handleRemoveImage = () => {
    if (!imageUrlValue) {
      return;
    }
    setValue('imageUrl', '', { shouldDirty: true });
    addToast({
      type: 'info',
      title: 'Image removed',
      message: 'The service image has been cleared.',
    });
  };

  const onCreateService = (values) => {
    setServiceError(null);
    createServiceMutation.mutate(values);
  };
  const onLinkInventory = (values) => {
    setLinkError(null);
    linkMutation.mutate(values);
  };

  const handleUnlink = (serviceId, inventoryId) => {
    const service = services.find((svc) => svc.id === serviceId);
    const requirement = service?.inventoryRequirements.find(
      (item) => item.inventoryId === inventoryId,
    );

    setConfirmRemoval({
      serviceId,
      inventoryId,
      inventoryName: requirement?.inventory.name ?? 'this inventory item',
    });
  };

  if (!isAdmin) {
    return null;
  }

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
          {serviceErrors.name && (
            <span className="field-error">{serviceErrors.name.message}</span>
          )}
        </div>

        <div className="field">
          <label htmlFor="service-description">Description</label>
          <textarea
            id="service-description"
            rows={2}
            {...registerService('description')}
          />
        </div>

        <input type="hidden" {...registerService('imageUrl')} />

        <div className="field">
          <label htmlFor="service-image">Service image</label>
          <input
            id="service-image"
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            disabled={isUploadingImage}
          />
          <p className="muted" style={{ margin: 0 }}>
            {isUploadingImage
              ? 'Uploading image...'
              : 'Upload JPG or PNG up to 5 MB.'}
          </p>
          {imageUrlValue && (
            <div className="image-preview">
              <img src={imageUrlValue} alt="Service preview" />
              <button
                type="button"
                className="button secondary"
                onClick={handleRemoveImage}
                disabled={isUploadingImage}
              >
                Remove image
              </button>
            </div>
          )}
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
              {...registerService('durationMinutes', {
                valueAsNumber: true,
                required: 'Duration is required',
                min: {
                  value: 15,
                  message: 'Duration must be at least 15 minutes',
                },
              })}
            />
            {serviceErrors.durationMinutes && (
              <span className="field-error">
                {serviceErrors.durationMinutes.message}
              </span>
            )}
          </div>
          <div className="field">
            <label htmlFor="service-price">Price (PHP)</label>
            <input
              id="service-price"
              type="number"
              min={0}
              step={0.01}
              placeholder="e.g. 25.00"
              {...registerService('pricePesos', {
                valueAsNumber: true,
                min: { value: 0, message: 'Price cannot be negative' },
              })}
            />
            <p className="muted" style={{ margin: 0 }}>
              Enter price in pesos; the system converts to cents automatically.
            </p>
            {serviceErrors.pricePesos && (
              <span className="field-error">
                {serviceErrors.pricePesos.message}
              </span>
            )}
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
          disabled={createServiceMutation.isPending || isUploadingImage}
          style={{ alignSelf: 'flex-start' }}
        >
          {createServiceMutation.isPending ? 'Saving…' : 'Create service'}
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
            disabled={
              servicesQuery.isLoading ||
              servicesQuery.isError ||
              services.length === 0 ||
              linkMutation.isPending
            }
          >
            <option value="" disabled>
              {servicesQuery.isLoading
                ? 'Loading services...'
                : 'Select service'}
            </option>
            {services.map((service) => (
              <option key={service.id} value={service.id}>
                {service.name}
              </option>
            ))}
          </select>
          {linkErrors.serviceId && (
            <span className="field-error">{linkErrors.serviceId.message}</span>
          )}
          {!servicesQuery.isLoading && services.length === 0 && (
            <p className="muted" style={{ margin: 0 }}>
              No services available yet.
            </p>
          )}
        </div>

        <div className="field">
          <label htmlFor="link-inventory">Inventory item</label>
          <select
            id="link-inventory"
            {...registerLink('inventoryId', {
              required: 'Inventory item is required',
            })}
            disabled={
              inventoryQuery.isLoading ||
              inventoryQuery.isError ||
              inventory.length === 0 ||
              linkMutation.isPending
            }
          >
            <option value="" disabled>
              {inventoryQuery.isLoading
                ? 'Loading inventory...'
                : 'Select inventory item'}
            </option>
            {inventory.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
          {linkErrors.inventoryId && (
            <span className="field-error">
              {linkErrors.inventoryId.message}
            </span>
          )}
          {!inventoryQuery.isLoading && inventory.length === 0 && (
            <p className="muted" style={{ margin: 0 }}>
              No inventory items available yet.
            </p>
          )}
        </div>

        <div className="field">
          <label htmlFor="link-quantity">Quantity per service</label>
          <input
            id="link-quantity"
            type="number"
            min={1}
            step={1}
            {...registerLink('quantity', {
              valueAsNumber: true,
              min: { value: 1, message: 'Quantity must be at least 1' },
            })}
          />
          {linkErrors.quantity && (
            <span className="field-error">{linkErrors.quantity.message}</span>
          )}
        </div>

        {linkError && <p className="error">{linkError}</p>}

        <button
          className="button"
          type="submit"
          disabled={linkMutation.isPending}
          style={{ alignSelf: 'flex-start' }}
        >
          {linkMutation.isPending ? 'Linking…' : 'Attach inventory'}
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
                  {service.imageUrl && (
                    <img
                      src={service.imageUrl}
                      alt={`${service.name} preview`}
                      className="service-card-image"
                    />
                  )}
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

      <ConfirmDialog
        open={Boolean(confirmRemoval)}
        title="Remove inventory requirement?"
        description={`This will unlink ${confirmRemoval?.inventoryName} from the service.`}
        confirmLabel="Remove"
        confirmVariant="danger"
        onCancel={() => setConfirmRemoval(null)}
        onConfirm={() =>
          confirmRemoval &&
          unlinkMutation.mutate({
            serviceId: confirmRemoval.serviceId,
            inventoryId: confirmRemoval.inventoryId,
          })
        }
      />
    </section>
  );
}
