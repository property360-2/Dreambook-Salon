import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const mockUseQuery = vi.fn();

vi.mock('@tanstack/react-query', () => ({
  useQuery: (options) => mockUseQuery(options),
}));

vi.mock('../hooks/useAuth.js', () => ({
  useAuth: vi.fn(),
}));

vi.mock('../features/admin/ServiceManager.jsx', () => ({
  ServiceManager: () => <div data-testid="service-manager">Service Admin</div>,
}));

vi.mock('../features/admin/InventoryManager.jsx', () => ({
  InventoryManager: () => (
    <div data-testid="inventory-manager">Inventory Admin</div>
  ),
}));

import { useAuth } from '../hooks/useAuth.js';
import { Dashboard } from './Dashboard.jsx';

describe('Dashboard', () => {
  beforeEach(() => {
    mockUseQuery.mockReset();
  });

  it('renders services with inventory details for non-admin user', () => {
    mockUseQuery.mockReturnValue({
      data: {
        services: [
          {
            id: 'svc_1',
            name: 'Signature Haircut',
            description: 'Precision cut and style.',
            durationMinutes: 60,
            priceCents: 2500,
            isActive: true,
            inventoryRequirements: [
              {
                inventoryId: 'inv_1',
                quantity: 100,
                inventory: { name: 'Clarifying Shampoo', unit: 'ml' },
              },
            ],
          },
        ],
      },
      isLoading: false,
      isError: false,
    });

    useAuth.mockReturnValue({
      user: { name: 'Jamie', role: 'CUSTOMER' },
      token: null,
    });

    render(<Dashboard />);

    expect(screen.getByText(/Signature Haircut/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Clarifying Shampoo/i),
    ).toBeInTheDocument();
    expect(screen.queryByTestId('service-manager')).not.toBeInTheDocument();
  });

  it('renders admin management tabs when user is admin', () => {
    mockUseQuery.mockReturnValue({
      data: { services: [] },
      isLoading: false,
      isError: false,
    });

    useAuth.mockReturnValue({
      user: { name: 'Morgan', role: 'ADMIN' },
      token: 'token',
    });

    render(<Dashboard />);

    expect(screen.getByRole('tab', { name: /services/i })).toHaveAttribute(
      'aria-selected',
      'true',
    );
    expect(screen.getByTestId('service-manager')).toBeInTheDocument();
    expect(
      screen.queryByTestId('inventory-manager'),
    ).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: /inventory/i }));

    expect(screen.getByRole('tab', { name: /inventory/i })).toHaveAttribute(
      'aria-selected',
      'true',
    );
    expect(
      screen.queryByTestId('service-manager'),
    ).not.toBeInTheDocument();
    expect(screen.getByTestId('inventory-manager')).toBeInTheDocument();
  });
});
