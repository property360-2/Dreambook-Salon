import { prisma } from '../../lib/prisma.js';

function toInventoryLinkResource(link) {
  if (!link?.inventory) {
    return null;
  }

  return {
    inventoryId: link.inventoryId,
    quantity: link.quantity,
    inventory: {
      id: link.inventory.id,
      name: link.inventory.name,
      description: link.inventory.description,
      stock: link.inventory.stock,
      unit: link.inventory.unit,
      threshold: link.inventory.threshold,
      isActive: link.inventory.isActive,
      createdAt: link.inventory.createdAt,
      updatedAt: link.inventory.updatedAt,
    },
  };
}

function toServiceResource(service) {
  return {
    id: service.id,
    name: service.name,
    description: service.description,
    durationMinutes: service.durationMinutes,
    priceCents: service.priceCents,
    isActive: service.isActive,
    createdAt: service.createdAt,
    updatedAt: service.updatedAt,
    inventoryRequirements: Array.isArray(service.inventoryLinks)
      ? service.inventoryLinks
          .map(toInventoryLinkResource)
          .filter(Boolean)
      : [],
  };
}

export async function listServices({ includeInactive = false } = {}) {
  const services = await prisma.service.findMany({
    where: includeInactive
      ? undefined
      : {
          isActive: true,
        },
    include: {
      inventoryLinks: {
        include: {
          inventory: true,
        },
      },
    },
    orderBy: {
      name: 'asc',
    },
  });

  return services.map(toServiceResource);
}

export async function createService(input, user) {
  const service = await prisma.service.create({
    data: {
      name: input.name,
      description: input.description,
      durationMinutes: input.durationMinutes,
      priceCents: input.priceCents,
      isActive: input.isActive ?? true,
      createdById: user?.id,
    },
    include: {
      inventoryLinks: {
        include: { inventory: true },
      },
    },
  });

  return toServiceResource(service);
}

export async function linkInventoryToService(serviceId, { inventoryId, quantity }) {
  const link = await prisma.serviceInventory.upsert({
    where: {
      serviceId_inventoryId: {
        serviceId,
        inventoryId,
      },
    },
    update: {
      quantity,
    },
    create: {
      serviceId,
      inventoryId,
      quantity,
    },
    include: {
      inventory: true,
    },
  });

  return {
    serviceId: link.serviceId,
    inventoryId: link.inventoryId,
    quantity: link.quantity,
    inventory: {
      id: link.inventory.id,
      name: link.inventory.name,
      description: link.inventory.description,
      unit: link.inventory.unit,
      stock: link.inventory.stock,
      threshold: link.inventory.threshold,
      isActive: link.inventory.isActive,
    },
  };
}

export async function unlinkInventoryFromService(serviceId, inventoryId) {
  await prisma.serviceInventory.delete({
    where: {
      serviceId_inventoryId: {
        serviceId,
        inventoryId,
      },
    },
  });
}
