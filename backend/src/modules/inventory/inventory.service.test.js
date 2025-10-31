import { afterEach, describe, expect, jest, test } from '@jest/globals';

const mockFindMany = jest.fn();
const mockCreate = jest.fn();
const mockUpdate = jest.fn();

jest.unstable_mockModule('../../lib/prisma.js', () => ({
  prisma: {
    inventory: {
      findMany: mockFindMany,
      create: mockCreate,
      update: mockUpdate,
    },
  },
}));

const {
  listInventory,
  createInventory,
  updateInventory,
} = await import('./inventory.service.js');

afterEach(() => {
  jest.clearAllMocks();
});

describe('inventory.service', () => {
  test('listInventory returns sorted items', async () => {
    const createdAt = new Date();
    const updatedAt = new Date();
    mockFindMany.mockResolvedValueOnce([
      {
        id: 'inv_1',
        name: 'Shampoo',
        description: null,
        stock: 12,
        unit: 'bottle',
        threshold: 3,
        isActive: true,
        createdAt,
        updatedAt,
      },
    ]);

    const inventory = await listInventory();

    expect(inventory).toEqual([
      {
        id: 'inv_1',
        name: 'Shampoo',
        description: null,
        stock: 12,
        unit: 'bottle',
        threshold: 3,
        isActive: true,
        createdAt,
        updatedAt,
      },
    ]);
    expect(mockFindMany).toHaveBeenCalledWith({
      orderBy: {
        name: 'asc',
      },
    });
  });

  test('createInventory persists defaults', async () => {
    mockCreate.mockResolvedValueOnce({
      id: 'inv_2',
      name: 'Conditioner',
      description: null,
      stock: 0,
      unit: null,
      threshold: 0,
      isActive: true,
      createdAt: new Date(),
      updatedAt: new Date(),
    });

    const created = await createInventory({
      name: 'Conditioner',
    });

    expect(created).toMatchObject({
      name: 'Conditioner',
      stock: 0,
    });
    expect(mockCreate).toHaveBeenCalledWith({
      data: expect.objectContaining({
        name: 'Conditioner',
        stock: 0,
      }),
    });
  });

  test('updateInventory applies provided fields', async () => {
    mockUpdate.mockResolvedValueOnce({
      id: 'inv_1',
      name: 'Shampoo',
      description: 'Salon size',
      stock: 20,
      unit: 'liter',
      threshold: 5,
      isActive: true,
      createdAt: new Date(),
      updatedAt: new Date(),
    });

    const updated = await updateInventory('inv_1', {
      stock: 20,
      description: 'Salon size',
    });

    expect(updated).toMatchObject({
      stock: 20,
      description: 'Salon size',
    });
    expect(mockUpdate).toHaveBeenCalledWith({
      where: { id: 'inv_1' },
      data: expect.objectContaining({
        stock: 20,
        description: 'Salon size',
      }),
    });
  });
});
