import { z } from 'zod';

function isIsoDate(value) {
  const date = new Date(value);
  return !Number.isNaN(date.getTime());
}

const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
const optionalIsoDateString = z
  .string()
  .refine(isIsoDate, 'must be a valid ISO date')
  .optional();

export const availabilityQuerySchema = z.object({
  serviceId: z.string().min(1, 'serviceId is required'),
  date: z
    .string()
    .regex(dateRegex, 'date must be formatted as YYYY-MM-DD'),
});

export const listAppointmentsQuerySchema = z
  .object({
    status: z
      .string()
      .transform((value) => value.split(',').map((item) => item.trim()).filter(Boolean))
      .optional(),
    from: optionalIsoDateString,
    to: optionalIsoDateString,
  })
  .transform((value) => ({
    status: value.status,
    from: value.from ? new Date(value.from) : undefined,
    to: value.to ? new Date(value.to) : undefined,
  }));

export const createAppointmentSchema = z.object({
  serviceId: z.string().min(1, 'serviceId is required'),
  scheduledStart: z
    .string()
    .refine(isIsoDate, 'scheduledStart must be a valid ISO date'),
  customer: z.object({
    name: z.string().min(1, 'customer.name is required'),
    email: z.string().email('customer.email must be a valid email'),
    phone: z
      .string()
      .min(6, 'customer.phone must be at least 6 characters')
      .max(32, 'customer.phone must be 32 characters or less')
      .optional(),
  }),
  notes: z
    .string()
    .trim()
    .max(500, 'notes must be less than 500 characters')
    .optional(),
  paymentMethod: z
    .enum(['DEMO_GCASH', 'DEMO_PAYMAYA', 'ONSITE'])
    .optional(),
});

export const updateAppointmentStatusSchema = z.object({
  status: z.enum(['PENDING', 'CONFIRMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),
  notes: z
    .string()
    .trim()
    .max(500, 'notes must be less than 500 characters')
    .optional(),
});
