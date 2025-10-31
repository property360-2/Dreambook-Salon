import { afterEach, describe, expect, jest, test } from '@jest/globals';

const mockFindMany = jest.fn();
const mockCreate = jest.fn();
const mockUpsert = jest.fn();
const mockDelete = jest.fn();

jest.unstable_mockModule('../../lib/prisma.js', () => ({
  prisma: {
    service: {
      findMany: mockFindMany,
      create: mockCreate,
    },
    serviceInventory: {
      upsert: mockUpsert,
      delete: mockDelete,
    },
  },
}));

const {
  listServices,
  createService,
  linkInventoryToService,
  unlinkInventoryFromService,
} = await import('./service.service.js');

afterEach(() => {
  jest.clearAllMocks();
});

describe('service.service', () => {
  test('listServices maps inventory requirements', async () => {
    mockFindMany.mockResolvedValueOnce([
      {
        id: 'svc_1',
        name: 'Haircut',
        description: 'Basic cut',
        durationMinutes: 60,
        priceCents: 2000,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
        inventoryLinks: [
          {
            inventoryId: 'inv_1',
            quantity: 2,
            inventory: {
              id: 'inv_1',
              name: 'Shampoo',
              description: 'Gentle wash',
              stock: 10,
              unit: 'bottle',
              threshold: 3,
              isActive: true,
              createdAt: new Date(),
              updatedAt: new Date(),
            },
          },
        ],
      },
    ]);

    const services = await listServices();

    expect(services).toHaveLength(1);
    expect(services[0].inventoryRequirements).toEqual([
      expect.objectContaining({
        inventoryId: 'inv_1',
        quantity: 2,
        inventory: expect.objectContaining({
          name: 'Shampoo',
          stock: 10,
        }),
      }),
    ]);
    expect(mockFindMany).toHaveBeenCalledWith(
      expect.objectContaining({
        include: expect.any(Object),
      }),
    );
  });

  test('createService returns mapped resource', async () => {
    const createdAt = new Date();
    const updatedAt = new Date();
    mockCreate.mockResolvedValueOnce({
      id: 'svc_1',
      name: 'Haircut',
      description: 'Basic cut',
      durationMinutes: 60,
      priceCents: 2000,
      isActive: true,
      createdAt,
      updatedAt,
      inventoryLinks: [],
    });

    const service = await createService(
      {
        name: 'Haircut',
        durationMinutes: 60,
        priceCents: 2000,
      },
      { id: 'usr_admin' },
    );

    expect(service).toMatchObject({
      id: 'svc_1',
      name: 'Haircut',
      inventoryRequirements: [],
    });
    expect(mockCreate).toHaveBeenCalledWith(
      expect.objectContaining({
        data: expect.objectContaining({
          createdById: 'usr_admin',
        }),
        include: expect.any(Object),
      }),
    );
  });

  test('linkInventoryToService upserts requirement and returns joined data', async () => {
    mockUpsert.mockResolvedValueOnce({
      serviceId: 'svc_1',
      inventoryId: 'inv_1',
      quantity: 3,
      inventory: {
        id: 'inv_1',
        name: 'Shampoo',
        description: null,
        stock: 25,
        unit: 'bottle',
        threshold: 5,
        isActive: true,
      },
    });

    const link = await linkInventoryToService('svc_1', {
      inventoryId: 'inv_1',
      quantity: 3,
    });

    expect(link).toEqual({
      serviceId: 'svc_1',
      inventoryId: 'inv_1',
      quantity: 3,
      inventory: expect.objectContaining({
        id: 'inv_1',
        name: 'Shampoo',
      }),
    });
    expect(mockUpsert).toHaveBeenCalledWith(
      expect.objectContaining({
        where: {
          serviceId_inventoryId: {
            serviceId: 'svc_1',
            inventoryId: 'inv_1',
          },
        },
      }),
    );
  });

  test('unlinkInventoryFromService removes the link', async () => {
    mockDelete.mockResolvedValueOnce({});

    await unlinkInventoryFromService('svc_1', 'inv_1');

    expect(mockDelete).toHaveBeenCalledWith({
      where: {
        serviceId_inventoryId: {
          serviceId: 'svc_1',
          inventoryId: 'inv_1',
        },
      },
    });
  });
});
