import crypto from 'node:crypto';

import { prisma } from '../../lib/prisma.js';
import { logger } from '../../config/logger.js';
import { hashPassword } from '../../utils/password.js';
import {
  findBlockedRangesBetween,
  getOrCreateSettings,
} from '../settings/settings.service.js';

const ACTIVE_APPOINTMENT_STATUSES = ['PENDING', 'CONFIRMED', 'IN_PROGRESS'];
const TERMINAL_APPOINTMENT_STATUSES = ['COMPLETED', 'CANCELLED'];
const SLOT_INTERVAL_MINUTES = 15;
const OPERATING_START_MINUTES = 9 * 60;
const OPERATING_END_MINUTES = 18 * 60;

function addMinutes(date, minutes) {
  return new Date(date.getTime() + minutes * 60 * 1000);
}

function toLocalDay(dateInput) {
  const date = new Date(dateInput);
  const normalized = new Date(date);
  normalized.setHours(0, 0, 0, 0);
  return normalized;
}

function buildOperatingWindow(dateInput) {
  const dayStart = toLocalDay(dateInput);
  const open = new Date(dayStart);
  open.setMinutes(OPERATING_START_MINUTES, 0, 0);
  const close = new Date(dayStart);
  close.setMinutes(OPERATING_END_MINUTES, 0, 0);
  return { open, close };
}

function windowsOverlap(aStart, aEnd, bStart, bEnd) {
  return aStart < bEnd && bStart < aEnd;
}

function sanitizeEmail(value) {
  return value.toLowerCase().trim();
}

function generateTempPassword() {
  return crypto.randomBytes(9).toString('base64url');
}

function toAppointmentResource(record) {
  return {
    id: record.id,
    status: record.status,
    scheduledStart: record.scheduledStart,
    scheduledEnd: record.scheduledEnd,
    confirmationCode: record.confirmationCode,
    notes: record.notes ?? null,
    customer: record.customer
      ? {
          id: record.customer.id,
          name: record.customer.name,
          email: record.customer.email,
        }
      : {
          id: null,
          name: record.customerName,
          email: record.customerEmail,
          phone: record.customerPhone ?? null,
        },
    service: record.service
      ? {
          id: record.service.id,
          name: record.service.name,
          durationMinutes: record.service.durationMinutes,
          priceCents: record.service.priceCents,
        }
      : null,
    payment: record.payment
      ? {
          id: record.payment.id,
          status: record.payment.status,
          method: record.payment.method,
          amountCents: record.payment.amountCents,
          transactionId: record.payment.transactionId ?? null,
        }
      : null,
    events: Array.isArray(record.events)
      ? record.events.map((event) => ({
          id: event.id,
          status: event.status,
          notes: event.notes ?? null,
          createdAt: event.createdAt,
          createdById: event.createdById ?? null,
        }))
      : [],
    inventoryAdjustments: Array.isArray(record.inventoryAdjustments)
      ? record.inventoryAdjustments.map((adjustment) => ({
          id: adjustment.id,
          inventoryId: adjustment.inventoryId,
          change: adjustment.change,
          reason: adjustment.reason,
          createdAt: adjustment.createdAt,
        }))
      : [],
  };
}

function buildAppointmentInclude() {
  return {
    service: true,
    customer: {
      select: {
        id: true,
        name: true,
        email: true,
      },
    },
    payment: true,
    events: true,
    inventoryAdjustments: true,
  };
}

function ensureSettingsDefaults(settings) {
  return {
    maxConcurrentAppointments: Math.max(settings?.maxConcurrentAppointments ?? 1, 1),
    bookingWindowDays: Math.max(settings?.bookingWindowDays ?? 30, 1),
  };
}

function calculateSlots({ appointments, blockedRanges, settings, serviceDurationMinutes, window }) {
  const slots = [];
  const durationMs = serviceDurationMinutes * 60 * 1000;
  const intervalMs = SLOT_INTERVAL_MINUTES * 60 * 1000;

  for (
    let slotStartTime = window.open.getTime();
    slotStartTime + durationMs <= window.close.getTime();
    slotStartTime += intervalMs
  ) {
    const slotStart = new Date(slotStartTime);
    const slotEnd = addMinutes(slotStart, serviceDurationMinutes);

    if (blockedRanges.some((range) => windowsOverlap(range.startsAt, range.endsAt, slotStart, slotEnd))) {
      continue;
    }

    const overlappingAppointments = appointments.filter((appt) =>
      windowsOverlap(appt.scheduledStart, appt.scheduledEnd, slotStart, slotEnd),
    );

    if (overlappingAppointments.length >= settings.maxConcurrentAppointments) {
      continue;
    }

    slots.push({
      start: slotStart.toISOString(),
      end: slotEnd.toISOString(),
      remainingCapacity: settings.maxConcurrentAppointments - overlappingAppointments.length,
    });
  }

  return slots;
}

export async function listAppointments(filters = {}) {
  const where = {};

  if (filters.status?.length) {
    where.status = {
      in: filters.status,
    };
  }

  if (filters.from || filters.to) {
    where.scheduledStart = {};
    if (filters.from) {
      where.scheduledStart.gte = filters.from;
    }
    if (filters.to) {
      where.scheduledStart.lte = filters.to;
    }
  }

  const appointments = await prisma.appointment.findMany({
    where,
    include: buildAppointmentInclude(),
    orderBy: {
      scheduledStart: 'asc',
    },
  });

  return appointments.map(toAppointmentResource);
}

export async function getAvailability({ serviceId, date }) {
  const service = await prisma.service.findUnique({
    where: { id: serviceId },
  });

  if (!service || !service.isActive) {
    const error = new Error('Service not found');
    error.status = 404;
    throw error;
  }

  const settingsRecord = await getOrCreateSettings();
  const settings = ensureSettingsDefaults(settingsRecord);

  const requestedDay = new Date(`${date}T00:00:00`);
  const now = new Date();
  const bookingWindowLimit = new Date();
  bookingWindowLimit.setHours(0, 0, 0, 0);
  bookingWindowLimit.setDate(bookingWindowLimit.getDate() + settings.bookingWindowDays);

  if (requestedDay > bookingWindowLimit) {
    const error = new Error('Requested date exceeds booking window');
    error.status = 400;
    throw error;
  }

  const { open, close } = buildOperatingWindow(requestedDay);
  const appointments = await prisma.appointment.findMany({
    where: {
      scheduledStart: { lt: close },
      scheduledEnd: { gt: open },
      status: { in: ACTIVE_APPOINTMENT_STATUSES },
    },
    select: {
      scheduledStart: true,
      scheduledEnd: true,
    },
  });

  const blockedRanges = await findBlockedRangesBetween(open, close);

  const slots = calculateSlots({
    appointments,
    blockedRanges,
    settings,
    serviceDurationMinutes: service.durationMinutes,
    window: { open, close },
  });

  return {
    serviceId,
    date,
    generatedAt: now.toISOString(),
    slots,
    meta: {
      maxConcurrentAppointments: settings.maxConcurrentAppointments,
      bookingWindowDays: settings.bookingWindowDays,
      serviceDurationMinutes: service.durationMinutes,
    },
    blockedRanges: blockedRanges.map((range) => ({
      id: range.id,
      startsAt: range.startsAt,
      endsAt: range.endsAt,
      reason: range.reason ?? null,
    })),
  };
}

async function ensureCustomerUser(customer, tx) {
  const email = sanitizeEmail(customer.email);
  const existing = await tx.user.findUnique({
    where: { email },
  });

  if (existing) {
    return { user: existing, credentials: null };
  }

  const generatedPassword = generateTempPassword();
  const passwordHash = await hashPassword(generatedPassword);

  const created = await tx.user.create({
    data: {
      email,
      name: customer.name.trim(),
      passwordHash,
      role: 'CUSTOMER',
    },
  });

  return {
    user: created,
    credentials: {
      username: created.email,
      password: generatedPassword,
    },
  };
}

async function assertSlotIsAvailable({
  tx = prisma,
  start,
  end,
  appointmentIdToExclude,
  settings,
}) {
  const overlapCount = await tx.appointment.count({
    where: {
      ...(appointmentIdToExclude
        ? {
            id: {
              not: appointmentIdToExclude,
            },
          }
        : {}),
      scheduledStart: { lt: end },
      scheduledEnd: { gt: start },
      status: { in: ACTIVE_APPOINTMENT_STATUSES },
    },
  });

  const settingsRecord =
    settings ?? ensureSettingsDefaults(await getOrCreateSettings(tx));

  if (overlapCount >= settingsRecord.maxConcurrentAppointments) {
    const error = new Error('Time slot is fully booked');
    error.status = 409;
    throw error;
  }

  const blockedRanges = await findBlockedRangesBetween(start, end, tx);
  if (blockedRanges.length > 0) {
    const error = new Error('Time slot is blocked');
    error.status = 409;
    throw error;
  }

  return settingsRecord;
}

function ensureWithinBookingWindow(date, bookingWindowDays) {
  const now = new Date();
  const limit = new Date();
  limit.setHours(0, 0, 0, 0);
  limit.setDate(limit.getDate() + bookingWindowDays);

  if (date > limit) {
    const error = new Error('Requested appointment exceeds booking window');
    error.status = 400;
    throw error;
  }

  if (date < now) {
    const error = new Error('Cannot create appointments in the past');
    error.status = 400;
    throw error;
  }
}

export async function createAppointment(payload, actor) {
  const scheduledStart = new Date(payload.scheduledStart);

  if (Number.isNaN(scheduledStart.getTime())) {
    const error = new Error('scheduledStart must be a valid date');
    error.status = 400;
    throw error;
  }

  const service = await prisma.service.findUnique({
    where: { id: payload.serviceId },
    include: {
      inventoryLinks: {
        include: {
          inventory: true,
        },
      },
    },
  });

  if (!service || !service.isActive) {
    const error = new Error('Service not found');
    error.status = 404;
    throw error;
  }

  const scheduledEnd = addMinutes(scheduledStart, service.durationMinutes);

  const settingsRecord = await getOrCreateSettings();
  const settings = ensureSettingsDefaults(settingsRecord);

  ensureWithinBookingWindow(scheduledStart, settings.bookingWindowDays);

  await assertSlotIsAvailable({
    start: scheduledStart,
    end: scheduledEnd,
    settings,
  });

  const { appointment, credentials } = await prisma.$transaction(async (tx) => {
    const { user, credentials: generatedCredentials } = await ensureCustomerUser(payload.customer, tx);

    const createdAppointment = await tx.appointment.create({
      data: {
        status: 'PENDING',
        scheduledStart,
        scheduledEnd,
        notes: payload.notes ?? null,
        customerId: user.id,
        customerName: payload.customer.name.trim(),
        customerEmail: sanitizeEmail(payload.customer.email),
        customerPhone: payload.customer.phone ?? null,
        serviceId: service.id,
      },
      include: buildAppointmentInclude(),
    });

    await tx.appointmentEvent.create({
      data: {
        appointmentId: createdAppointment.id,
        status: 'PENDING',
        notes: 'Appointment created',
        createdById: actor?.id ?? user.id,
      },
    });

    return {
      appointment: createdAppointment,
      credentials: generatedCredentials,
    };
  });

  return {
    appointment: toAppointmentResource(appointment),
    credentials,
    requestedPaymentMethod: payload.paymentMethod ?? null,
  };
}

async function processInventoryForCompletion({ tx, appointment, actor }) {
  const serviceWithInventory = await tx.service.findUnique({
    where: { id: appointment.serviceId },
    include: {
      inventoryLinks: {
        include: {
          inventory: true,
        },
      },
    },
  });

  if (!serviceWithInventory) {
    return { adjustments: [], lowStock: [] };
  }

  const adjustments = [];
  const lowStock = [];

  for (const link of serviceWithInventory.inventoryLinks) {
    const inventory = link.inventory;
    const newStock = inventory.stock - link.quantity;

    if (newStock < 0) {
      const error = new Error(
        `Insufficient stock for ${inventory.name}. Required ${link.quantity}${inventory.unit ?? ''}.`,
      );
      error.status = 400;
      throw error;
    }

    const updated = await tx.inventory.update({
      where: { id: inventory.id },
      data: {
        stock: {
          decrement: link.quantity,
        },
      },
    });

    await tx.inventoryAdjustment.create({
      data: {
        inventoryId: inventory.id,
        appointmentId: appointment.id,
        change: -link.quantity,
        reason: 'APPOINTMENT_COMPLETED',
        createdById: actor?.id ?? null,
      },
    });

    adjustments.push({
      inventoryId: inventory.id,
      previousStock: inventory.stock,
      newStock: updated.stock,
      threshold: updated.threshold,
    });

    if (updated.stock <= updated.threshold) {
      lowStock.push({
        inventoryId: inventory.id,
        name: inventory.name,
        stock: updated.stock,
        threshold: updated.threshold,
      });
    }
  }

  if (adjustments.length) {
    logger.info(
      {
        appointmentId: appointment.id,
        adjustments,
      },
      'Inventory adjusted after appointment completion',
    );
  }

  return { adjustments, lowStock };
}

export async function updateAppointmentStatus(id, payload, actor) {
  const appointment = await prisma.appointment.findUnique({
    where: { id },
    include: buildAppointmentInclude(),
  });

  if (!appointment) {
    const error = new Error('Appointment not found');
    error.status = 404;
    throw error;
  }

  if (appointment.status === payload.status) {
    return {
      appointment: toAppointmentResource(appointment),
      inventory: {
        adjustments: [],
        lowStock: [],
      },
    };
  }

  if (TERMINAL_APPOINTMENT_STATUSES.includes(appointment.status)) {
    const error = new Error('Cannot modify a finalized appointment');
    error.status = 400;
    throw error;
  }

  const result = await prisma.$transaction(async (tx) => {
    const updated = await tx.appointment.update({
      where: { id },
      data: {
        status: payload.status,
      },
      include: buildAppointmentInclude(),
    });

    await tx.appointmentEvent.create({
      data: {
        appointmentId: id,
        status: payload.status,
        notes: payload.notes ?? null,
        createdById: actor?.id ?? null,
      },
    });

    let inventory = {
      adjustments: [],
      lowStock: [],
    };

    if (payload.status === 'COMPLETED') {
      inventory = await processInventoryForCompletion({
        tx,
        appointment: updated,
        actor,
      });
    }

    return {
      appointment: updated,
      inventory,
    };
  });

  return {
    appointment: toAppointmentResource(result.appointment),
    inventory: result.inventory,
  };
}
