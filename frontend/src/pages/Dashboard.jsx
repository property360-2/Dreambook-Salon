import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { useAuth } from '../hooks/useAuth.js';
import { api } from '../lib/api.js';
import { ServiceManager } from '../features/admin/ServiceManager.jsx';
import { InventoryManager } from '../features/admin/InventoryManager.jsx';

const peso = new Intl.NumberFormat('en-PH', {
  style: 'currency',
  currency: 'PHP',
});

export function Dashboard() {
  const { user, token } = useAuth();
  const isAdmin = user.role === 'ADMIN';
  const [adminTab, setAdminTab] = useState('services');
  const serviceScope = isAdmin ? 'admin' : 'public';
  const {
    data: servicesData,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['services', { scope: serviceScope }],
    queryFn: () =>
      api.services({
        includeInactive: isAdmin,
        token: isAdmin ? token : undefined,
      }),
  });

  return (
    <div className="flow">
      <section className="card">
        <h2 style={{ margin: 0 }}>Welcome back, {user.name}!</h2>
        <p className="muted">
          Phase 2 focus: connect services to inventory and keep stock healthy.
        </p>
      </section>

      <section className="card">
        <header style={{ marginBottom: '1rem' }}>
          <h2 style={{ margin: 0 }}>Available services</h2>
          <p className="muted" style={{ margin: 0 }}>
            These map to the seed data and admin-created inventory-linked items.
          </p>
        </header>

        {isLoading && <p className="muted">Loading services...</p>}
        {isError && (
          <p className="error">Could not load services: {error.message}</p>
        )}
        {!isLoading && !isError && servicesData?.services?.length === 0 && (
          <p className="muted">No services yet. Add one from the admin API.</p>
        )}

        {!isLoading && !isError && servicesData?.services?.length > 0 && (
          <div className="service-grid">
            {servicesData.services.map((service) => (
              <article className="service-card" key={service.id}>
                {service.imageUrl && (
                  <img
                    src={service.imageUrl}
                    alt={`${service.name} preview`}
                    className="service-card-image"
                  />
                )}
                <h3>{service.name}</h3>
                {service.description && (
                  <p className="muted" style={{ margin: 0 }}>
                    {service.description}
                  </p>
                )}
                <div>
                  <h4 style={{ marginBottom: '0.5rem' }}>Inventory usage</h4>
                  {service.inventoryRequirements?.length === 0 && (
                    <p className="muted" style={{ margin: 0 }}>
                      No inventory linked yet.
                    </p>
                  )}
                  {service.inventoryRequirements?.length > 0 && (
                    <ul style={{ paddingLeft: '1.25rem', margin: 0 }}>
                      {service.inventoryRequirements.map((link) => (
                        <li key={link.inventoryId}>
                          {link.inventory.name} - {link.quantity}{' '}
                          {link.inventory.unit ?? ''}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
                <div style={{ marginTop: 'auto' }}>
                  <strong>{peso.format(service.priceCents / 100)}</strong>
                  <p className="muted" style={{ margin: 0 }}>
                    {service.durationMinutes} min -{' '}
                    {service.isActive ? 'Active' : 'Inactive'}
                  </p>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      {isAdmin && (
        <div>
          <div className="tabs" role="tablist" aria-label="Admin management">
            <button
              type="button"
              className={`tab-button ${adminTab === 'services' ? 'active' : ''}`}
              onClick={() => setAdminTab('services')}
              role="tab"
              aria-selected={adminTab === 'services'}
            >
              Services
            </button>
            <button
              type="button"
              className={`tab-button ${
                adminTab === 'inventory' ? 'active' : ''
              }`}
              onClick={() => setAdminTab('inventory')}
              role="tab"
              aria-selected={adminTab === 'inventory'}
            >
              Inventory
            </button>
          </div>

          {adminTab === 'services' && <ServiceManager />}
          {adminTab === 'inventory' && <InventoryManager />}
        </div>
      )}
    </div>
  );
}
