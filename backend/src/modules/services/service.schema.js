import { z } from 'zod';

export const createServiceSchema = z.object({
  name: z.string().min(2).max(120),
  description: z.string().max(1000).optional(),
  durationMinutes: z
    .coerce.number({
      required_error: 'durationMinutes is required',
      invalid_type_error: 'durationMinutes must be a number',
    })
    .min(15)
    .max(480),
  priceCents: z
    .coerce.number({
      required_error: 'priceCents is required',
      invalid_type_error: 'priceCents must be a number',
    })
    .min(0),
  isActive: z.boolean().optional(),
});

export const serviceInventoryLinkSchema = z.object({
  inventoryId: z.string().min(1),
  quantity: z
    .coerce.number({
      required_error: 'quantity is required',
      invalid_type_error: 'quantity must be a number',
    })
    .int()
    .min(1, 'quantity must be at least 1'),
});
