import { env } from '../../config/env.js';
import { prisma } from '../../lib/prisma.js';

export const SETTINGS_ID = 'singleton';

export async function getOrCreateSettings(tx = prisma) {
  const client = tx ?? prisma;
  const existing = await client.settings.findUnique({
    where: { id: SETTINGS_ID },
  });

  if (existing) {
    return existing;
  }

  return client.settings.create({
    data: {
      id: SETTINGS_ID,
      maxConcurrentAppointments: env.salonMaxConcurrentDefault,
      bookingWindowDays: env.salonBookingWindowDaysDefault,
    },
  });
}

export async function getSettings({ includeBlockedRanges = false } = {}) {
  const settings = await getOrCreateSettings();

  if (!includeBlockedRanges) {
    return {
      settings,
      blockedRanges: [],
    };
  }

  const blockedRanges = await prisma.blockedRange.findMany({
    where: {
      settingsId: SETTINGS_ID,
      endsAt: {
        gte: new Date(),
      },
    },
    orderBy: {
      startsAt: 'asc',
    },
  });

  return {
    settings,
    blockedRanges,
  };
}

export async function updateSettings(values) {
  await getOrCreateSettings();
  const updated = await prisma.settings.update({
    where: { id: SETTINGS_ID },
    data: {
      ...(values.maxConcurrentAppointments !== undefined
        ? { maxConcurrentAppointments: values.maxConcurrentAppointments }
        : {}),
      ...(values.bookingWindowDays !== undefined
        ? { bookingWindowDays: values.bookingWindowDays }
        : {}),
    },
  });

  return updated;
}

export async function listBlockedRanges(filters = {}) {
  await getOrCreateSettings();
  const where = {
    settingsId: SETTINGS_ID,
  };

  if (filters.from) {
    where.endsAt = { gte: filters.from };
  }
  if (filters.to) {
    where.startsAt = {
      ...(where.startsAt ?? {}),
      lte: filters.to,
    };
  }

  const ranges = await prisma.blockedRange.findMany({
    where,
    orderBy: {
      startsAt: 'asc',
    },
  });

  return ranges;
}

export async function createBlockedRange(data, actor) {
  await getOrCreateSettings();
  const startsAt = new Date(data.startsAt);
  const endsAt = new Date(data.endsAt);

  const overlapping = await prisma.blockedRange.count({
    where: {
      settingsId: SETTINGS_ID,
      startsAt: { lt: endsAt },
      endsAt: { gt: startsAt },
    },
  });

  if (overlapping > 0) {
    const error = new Error('Blocked range overlaps with an existing entry');
    error.status = 409;
    throw error;
  }

  return prisma.blockedRange.create({
    data: {
      startsAt,
      endsAt,
      reason: data.reason ?? null,
      createdById: actor?.id ?? null,
      settingsId: SETTINGS_ID,
    },
  });
}

export async function deleteBlockedRange(id) {
  await prisma.blockedRange.delete({
    where: { id },
  });
}

export async function findBlockedRangesBetween(start, end, tx = prisma) {
  const client = tx ?? prisma;
  return client.blockedRange.findMany({
    where: {
      settingsId: SETTINGS_ID,
      startsAt: { lt: end },
      endsAt: { gt: start },
    },
    orderBy: {
      startsAt: 'asc',
    },
  });
}
