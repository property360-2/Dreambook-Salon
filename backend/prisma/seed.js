import { config as loadEnv } from 'dotenv';
import { PrismaClient } from '@prisma/client';

import { hashPassword } from '../src/utils/password.js';
import { env } from '../src/config/env.js';

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
        imageUrl:
          'https://res.cloudinary.com/demo/image/upload/v1690470332/haircut_female.jpg',
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
        imageUrl:
          'https://res.cloudinary.com/demo/image/upload/v1690470332/nails_polish.jpg',
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

function makeDateWithOffset(daysOffset, hour, minute) {
  const date = new Date();
  date.setHours(0, 0, 0, 0);
  date.setDate(date.getDate() + daysOffset);
  date.setHours(hour, minute, 0, 0);
  return date;
}

async function ensureSalonSettings() {
  await prisma.settings.upsert({
    where: { id: 'singleton' },
    update: {
      maxConcurrentAppointments: env.salonMaxConcurrentDefault,
      bookingWindowDays: env.salonBookingWindowDaysDefault,
    },
    create: {
      id: 'singleton',
      maxConcurrentAppointments: env.salonMaxConcurrentDefault,
      bookingWindowDays: env.salonBookingWindowDaysDefault,
    },
  });
}

async function ensureBlockedRanges() {
  const count = await prisma.blockedRange.count();
  if (count > 0) {
    return;
  }

  const trainingStart = makeDateWithOffset(7, 12, 0);
  const trainingEnd = makeDateWithOffset(7, 18, 0);

  await prisma.blockedRange.create({
    data: {
      startsAt: trainingStart,
      endsAt: trainingEnd,
      reason: 'Team training',
      settingsId: 'singleton',
    },
  });
}

async function ensureSampleCustomer() {
  const email = 'customer@dreambook.local';

  const existing = await prisma.user.findUnique({
    where: { email },
  });

  if (existing) {
    return existing;
  }

  const passwordHash = await hashPassword('Customer123!');

  return prisma.user.create({
    data: {
      email,
      name: 'Sample Customer',
      passwordHash,
      role: 'CUSTOMER',
    },
  });
}

async function ensureChatbotRules(adminId) {
  const count = await prisma.chatbotRule.count();
  if (count > 0) {
    return;
  }

  await prisma.chatbotRule.createMany({
    data: [
      {
        pattern: 'hello',
        reply: 'Hi there! Ready to book a service or see our top treatments?',
        priority: 100,
        isActive: true,
        createdById: adminId,
      },
      {
        pattern: 'price',
        reply:
          'Prices vary by service — tap into the booking flow to see exact totals.',
        priority: 80,
        isActive: true,
        createdById: adminId,
      },
      {
        pattern: 'hours',
        reply:
          'We’re open 9am – 6pm daily, with last-call appointments at 5pm.',
        priority: 70,
        isActive: true,
        createdById: adminId,
      },
      {
        pattern: 'where',
        reply:
          'Find us at the Dreambook Building, 3rd Floor. Parking is free for guests!',
        priority: 60,
        isActive: true,
        createdById: adminId,
      },
    ],
  });
}

async function ensureSampleAppointments(customer) {
  const existing = await prisma.appointment.count();
  if (existing > 0) {
    return;
  }

  const services = await prisma.service.findMany({
    where: { isActive: true },
    include: {
      inventoryLinks: {
        include: {
          inventory: true,
        },
      },
    },
  });

  if (!services.length) {
    return;
  }

  const pickService = (name) => services.find((svc) => svc.name === name) ?? services[0];

  const haircut = pickService('Signature Haircut');
  const manicure = pickService('Gel Manicure');

  async function createAppointment({
    status,
    daysOffset,
    hour,
    minute,
    service,
    notes,
    paymentMethod,
  }) {
    const scheduledStart = makeDateWithOffset(daysOffset, hour, minute);
    const scheduledEnd = new Date(
      scheduledStart.getTime() + service.durationMinutes * 60 * 1000,
    );

    const appointment = await prisma.appointment.create({
      data: {
        status: 'PENDING',
        scheduledStart,
        scheduledEnd,
        notes: notes ?? null,
        customerId: customer.id,
        customerName: customer.name,
        customerEmail: customer.email,
        serviceId: service.id,
      },
    });

    await prisma.appointmentEvent.create({
      data: {
        appointmentId: appointment.id,
        status: 'PENDING',
        notes: 'Seeded appointment created',
        createdById: customer.id,
      },
    });

    if (paymentMethod) {
      const isPaid = status === 'CONFIRMED' || status === 'COMPLETED';
      await prisma.payment.create({
        data: {
          appointmentId: appointment.id,
          method: paymentMethod,
          status: isPaid ? 'PAID' : 'PENDING',
          amountCents: service.priceCents ?? 0,
          transactionId: isPaid
            ? `TXN-SEED-${Math.random().toString(36).slice(2, 10).toUpperCase()}`
            : null,
        },
      });
    }

    if (status !== 'PENDING') {
      await prisma.appointment.update({
        where: { id: appointment.id },
        data: {
          status,
        },
      });

      await prisma.appointmentEvent.create({
        data: {
          appointmentId: appointment.id,
          status,
          notes: `Seeded status: ${status}`,
          createdById: customer.id,
        },
      });
    }

    if (status === 'COMPLETED' && service.inventoryLinks?.length) {
      for (const link of service.inventoryLinks) {
        await prisma.inventory.update({
          where: { id: link.inventoryId },
          data: {
            stock: {
              decrement: link.quantity,
            },
          },
        });

        await prisma.inventoryAdjustment.create({
          data: {
            inventoryId: link.inventoryId,
            appointmentId: appointment.id,
            change: -link.quantity,
            reason: 'SEED_COMPLETION',
            createdById: customer.id,
          },
        });
      }
    }
  }

  await createAppointment({
    status: 'PENDING',
    daysOffset: 1,
    hour: 10,
    minute: 0,
    service: haircut,
    notes: 'First-time guest, prefers warm tones.',
  });

  await createAppointment({
    status: 'CONFIRMED',
    daysOffset: 2,
    hour: 13,
    minute: 30,
    service: manicure ?? haircut,
    paymentMethod: 'DEMO_GCASH',
    notes: 'Add nail art sample designs to consultation.',
  });

  await createAppointment({
    status: 'COMPLETED',
    daysOffset: -1,
    hour: 15,
    minute: 0,
    service: haircut,
    paymentMethod: 'DEMO_PAYMAYA',
    notes: 'Requested retail product recommendations.',
  });
}

async function main() {
  const admin = await upsertAdmin();
  await ensureSampleServices(admin.id);
  await ensureSampleInventory();
  await ensureServiceInventoryLinks();
  await ensureSalonSettings();
  await ensureBlockedRanges();
  const customer = await ensureSampleCustomer();
  await ensureSampleAppointments(customer);
  await ensureChatbotRules(admin.id);
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
