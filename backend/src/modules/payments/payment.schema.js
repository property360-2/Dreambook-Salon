import { z } from 'zod';

export const createDemoPaymentSchema = z.object({
  appointmentId: z.string().min(1, 'appointmentId is required'),
  method: z.enum(['DEMO_GCASH', 'DEMO_PAYMAYA', 'ONSITE']).default('DEMO_GCASH'),
});

export const updateDemoPaymentSchema = z.object({
  status: z.enum(['PAID', 'FAILED', 'CANCELLED']),
});
