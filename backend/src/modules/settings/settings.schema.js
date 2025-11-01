import { z } from 'zod';

function isIsoDate(value) {
  const date = new Date(value);
  return !Number.isNaN(date.getTime());
}

const isoDateString = z
  .string()
  .refine(isIsoDate, 'must be a valid ISO date');

export const updateSettingsSchema = z
  .object({
    maxConcurrentAppointments: z
      .coerce.number()
      .int()
      .min(1, 'maxConcurrentAppointments must be at least 1')
      .max(20, 'maxConcurrentAppointments must be 20 or less')
      .optional(),
    bookingWindowDays: z
      .coerce.number()
      .int()
      .min(1, 'bookingWindowDays must be at least 1')
      .max(180, 'bookingWindowDays must be 180 or less')
      .optional(),
  })
  .refine((data) => Object.keys(data).length > 0, {
    message: 'At least one setting must be provided',
  });

export const createBlockedRangeSchema = z
  .object({
    startsAt: isoDateString,
    endsAt: isoDateString,
    reason: z
      .string()
      .trim()
      .max(200, 'reason must be 200 characters or less')
      .optional(),
  })
  .refine((value) => new Date(value.endsAt) > new Date(value.startsAt), {
    message: 'endsAt must be after startsAt',
  });

export const listBlockedRangesQuerySchema = z
  .object({
    from: isoDateString.optional(),
    to: isoDateString.optional(),
  })
  .transform((value) => ({
    from: value.from ? new Date(value.from) : undefined,
    to: value.to ? new Date(value.to) : undefined,
  }));
