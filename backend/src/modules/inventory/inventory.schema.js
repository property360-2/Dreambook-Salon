import { z } from 'zod';

export const baseInventorySchema = z.object({
  name: z.string().min(2).max(120),
  description: z.string().max(1000).optional().nullable(),
  stock: z
    .coerce.number({
      invalid_type_error: 'stock must be a number',
    })
    .int()
    .min(0)
    .optional(),
  unit: z
    .string()
    .max(32)
    .optional()
    .nullable(),
  threshold: z
    .coerce.number({
      invalid_type_error: 'threshold must be a number',
    })
    .int()
    .min(0)
    .optional(),
  isActive: z.boolean().optional(),
});

export const createInventorySchema = baseInventorySchema.extend({
  stock: baseInventorySchema.shape.stock.default(0),
  threshold: baseInventorySchema.shape.threshold.default(0),
});

export const updateInventorySchema = baseInventorySchema.partial().refine(
  (data) => Object.keys(data).length > 0,
  {
    message: 'At least one field must be provided to update inventory',
  },
);
