import { prisma } from '../../lib/prisma.js';

function toInventoryResource(record) {
  return {
    id: record.id,
    name: record.name,
    description: record.description ?? null,
    stock: record.stock,
    unit: record.unit ?? null,
    threshold: record.threshold,
    isActive: record.isActive,
    createdAt: record.createdAt,
    updatedAt: record.updatedAt,
  };
}

export async function listInventory() {
  const items = await prisma.inventory.findMany({
    orderBy: {
      name: 'asc',
    },
  });

  return items.map(toInventoryResource);
}

export async function createInventory(input) {
  const record = await prisma.inventory.create({
    data: {
      name: input.name,
      description: input.description,
      stock: input.stock ?? 0,
      unit: input.unit ?? null,
      threshold: input.threshold ?? 0,
      isActive: input.isActive ?? true,
    },
  });

  return toInventoryResource(record);
}

export async function updateInventory(id, input) {
  const record = await prisma.inventory.update({
    where: { id },
    data: {
      ...(input.name !== undefined ? { name: input.name } : {}),
      ...(input.description !== undefined ? { description: input.description } : {}),
      ...(input.stock !== undefined ? { stock: input.stock } : {}),
      ...(input.unit !== undefined ? { unit: input.unit } : {}),
      ...(input.threshold !== undefined ? { threshold: input.threshold } : {}),
      ...(input.isActive !== undefined ? { isActive: input.isActive } : {}),
    },
  });

  return toInventoryResource(record);
}
