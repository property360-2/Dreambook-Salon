import { config as loadEnv } from 'dotenv';
import { z } from 'zod';

loadEnv();

const envSchema = z.object({
  NODE_ENV: z
    .enum(['development', 'test', 'production'])
    .default('development'),
  PORT: z.coerce.number().default(4000),
  DATABASE_URL: z
    .string()
    .min(1, 'DATABASE_URL is required')
    .default('file:./dev.db'),
  JWT_SECRET: z
    .string()
    .min(32, 'JWT_SECRET must be at least 32 characters long')
    .default('change-me-change-me-change-me-change-me'),
  CORS_ORIGIN: z.string().optional(),
  ADMIN_EMAIL: z.string().email().default('admin@dreambook.local'),
  ADMIN_PASSWORD: z.string().min(8).default('ChangeMe123!'),
  CLOUDINARY_URL: z.string().optional(),
  CLOUDINARY_CLOUD_NAME: z.string().optional(),
  CLOUDINARY_API_KEY: z.string().optional(),
  CLOUDINARY_API_SECRET: z.string().optional(),
  SALON_MAX_CONCURRENT_DEFAULT: z.string().optional(),
  SALON_BOOKING_WINDOW_DAYS: z.string().optional(),
  SALON_CHATBOT_RATE_LIMIT: z.string().optional(),
  SALON_CHATBOT_FALLBACK_REPLY: z.string().optional(),
});

const rawEnv = envSchema.parse(process.env);

function parseOptionalInt(value, { fallback, min, max }) {
  if (!value) {
    return fallback;
  }

  const parsed = Number.parseInt(value, 10);
  if (Number.isNaN(parsed)) {
    return fallback;
  }

  if (min !== undefined && parsed < min) {
    return min;
  }

  if (max !== undefined && parsed > max) {
    return max;
  }

  return parsed;
}

const corsOrigins = rawEnv.CORS_ORIGIN
  ? rawEnv.CORS_ORIGIN.split(',').map((origin) => origin.trim())
  : ['http://localhost:3000'];

const salonMaxConcurrentDefault = parseOptionalInt(
  rawEnv.SALON_MAX_CONCURRENT_DEFAULT,
  { fallback: 1, min: 1, max: 20 },
);
const salonBookingWindowDaysDefault = parseOptionalInt(
  rawEnv.SALON_BOOKING_WINDOW_DAYS,
  { fallback: 30, min: 1, max: 180 },
);
const chatbotRateLimitMs = parseOptionalInt(rawEnv.SALON_CHATBOT_RATE_LIMIT, {
  fallback: 800,
  min: 200,
  max: 5000,
});

export const env = {
  ...rawEnv,
  corsOrigins,
  isProduction: rawEnv.NODE_ENV === 'production',
  isTest: rawEnv.NODE_ENV === 'test',
  isCloudinaryConfigured:
    Boolean(rawEnv.CLOUDINARY_URL) ||
    (Boolean(rawEnv.CLOUDINARY_CLOUD_NAME) &&
      Boolean(rawEnv.CLOUDINARY_API_KEY) &&
      Boolean(rawEnv.CLOUDINARY_API_SECRET)),
  salonMaxConcurrentDefault,
  salonBookingWindowDaysDefault,
  chatbotRateLimitMs,
  chatbotFallbackReply: rawEnv.SALON_CHATBOT_FALLBACK_REPLY ?? null,
};
