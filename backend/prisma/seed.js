import { config as loadEnv } from 'dotenv';
import { PrismaClient } from '@prisma/client';

import { hashPassword } from '../src/utils/password.js';

loadEnv();

const prisma = new PrismaClient();

async function upsertAdmin() {
  const adminEmail =
    process.env.ADMIN_EMAIL?.toLowerCase() ?? 'admin@dreambook.local';
  const adminPassword =
    process.env.ADMIN_PASSWORD ?? 'ChangeMe123!';

  const existing = await prisma.user.findUnique({
    where: { email: adminEmail },
  });

  if (existing) {
    return existing;
  }

  const passwordHash = await hashPassword(adminPassword);

  return prisma.user.create({
    data: {
      email: adminEmail,
      name: 'Dreambook Admin',
      passwordHash,
      role: 'ADMIN',
    },
  });
}

async function ensureSampleServices(adminId) {
  const count = await prisma.service.count();
  if (count > 0) {
    return;
  }

  const now = new Date();

  await prisma.service.createMany({
    data: [
      {
        name: 'Signature Haircut',
        description:
          'Precision cut with wash, dry, and personalized styling advice.',
        durationMinutes: 60,
        priceCents: 2500,
        isActive: true,
        createdAt: now,
        updatedAt: now,
        createdById: adminId,
      },
      {
        name: 'Gel Manicure',
        description:
          'Long-lasting gel polish with cuticle care and hand massage.',
        durationMinutes: 45,
        priceCents: 1800,
        isActive: true,
        createdAt: now,
        updatedAt: now,
        createdById: adminId,
      },
    ],
  });
}

async function upsertInventoryItem(data) {
  const existing = await prisma.inventory.findFirst({
    where: { name: data.name },
  });

  if (existing) {
    return existing;
  }

  return prisma.inventory.create({ data });
}

async function ensureSampleInventory() {
  const shampoo = await upsertInventoryItem({
    name: 'Clarifying Shampoo Base',
    description: 'Bulk liter bottle used before treatments.',
    stock: 3000,
    unit: 'ml',
    threshold: 750,
    isActive: true,
  });

  const gelPolish = await upsertInventoryItem({
    name: 'Gel Polish Kit',
    description: 'Single-use kit with polish, prep, and top coat.',
    stock: 40,
    unit: 'kit',
    threshold: 10,
    isActive: true,
  });

  const mask = await upsertInventoryItem({
    name: 'Keratin Hair Mask',
    description: '200ml jar used for premium treatments.',
    stock: 25,
    unit: 'jar',
    threshold: 5,
    isActive: true,
  });

  return { shampoo, gelPolish, mask };
}

async function ensureServiceInventoryLinks() {
  const services = await prisma.service.findMany({
    select: { id: true, name: true },
  });
  const inventory = await prisma.inventory.findMany({
    select: { id: true, name: true },
  });

  const findService = (name) => services.find((svc) => svc.name === name);
  const findInventory = (name) => inventory.find((item) => item.name === name);

  const haircut = findService('Signature Haircut');
  const manicure = findService('Gel Manicure');
  const shampoo = findInventory('Clarifying Shampoo Base');
  const gelPolish = findInventory('Gel Polish Kit');
  const mask = findInventory('Keratin Hair Mask');

  const operations = [
    haircut && shampoo
      ? prisma.serviceInventory.upsert({
          where: {
            serviceId_inventoryId: {
              serviceId: haircut.id,
              inventoryId: shampoo.id,
            },
          },
          update: {
            quantity: 100, // ml per appointment
          },
          create: {
            serviceId: haircut.id,
            inventoryId: shampoo.id,
            quantity: 100,
          },
        })
      : null,
    haircut && mask
      ? prisma.serviceInventory.upsert({
          where: {
            serviceId_inventoryId: {
              serviceId: haircut.id,
              inventoryId: mask.id,
            },
          },
          update: {
            quantity: 1,
          },
          create: {
            serviceId: haircut.id,
            inventoryId: mask.id,
            quantity: 1,
          },
        })
      : null,
    manicure && gelPolish
      ? prisma.serviceInventory.upsert({
          where: {
            serviceId_inventoryId: {
              serviceId: manicure.id,
              inventoryId: gelPolish.id,
            },
          },
          update: {
            quantity: 1,
          },
          create: {
            serviceId: manicure.id,
            inventoryId: gelPolish.id,
            quantity: 1,
          },
        })
      : null,
  ].filter(Boolean);

  if (operations.length > 0) {
    await prisma.$transaction(operations);
  }
}

async function main() {
  const admin = await upsertAdmin();
  await ensureSampleServices(admin.id);
  await ensureSampleInventory();
  await ensureServiceInventoryLinks();
}

main()
  .then(() => {
    console.log('Seed data applied successfully');
  })
  .catch((error) => {
    console.error('Seed failed', error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
