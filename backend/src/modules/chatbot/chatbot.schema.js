import { z } from 'zod';

export const createChatbotRuleSchema = z.object({
  pattern: z
    .string()
    .trim()
    .min(2, 'pattern must be at least 2 characters')
    .max(120, 'pattern must be 120 characters or less'),
  reply: z
    .string()
    .trim()
    .min(1, 'reply is required')
    .max(600, 'reply must be 600 characters or less'),
  priority: z.coerce
    .number()
    .int()
    .min(0, 'priority must be zero or greater')
    .max(1000, 'priority must be 1000 or less')
    .default(0),
  isActive: z.coerce.boolean().default(true),
});

export const updateChatbotRuleSchema = createChatbotRuleSchema
  .partial({
    pattern: true,
    reply: true,
    priority: true,
    isActive: true,
  })
  .refine((value) => Object.keys(value).length > 0, {
    message: 'At least one field must be provided for update',
  });

export const chatbotMessageSchema = z.object({
  message: z
    .string()
    .trim()
    .min(1, 'message is required')
    .max(600, 'message must be 600 characters or less'),
  sessionId: z.string().trim().max(120).optional(),
});
