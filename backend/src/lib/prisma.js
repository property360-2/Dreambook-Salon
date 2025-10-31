import { PrismaClient } from '@prisma/client';

import { env } from '../config/env.js';
import { logger } from '../config/logger.js';

export const prisma = new PrismaClient({
  log: env.isProduction ? ['error'] : ['query', 'warn', 'error'],
  datasources: {
    db: {
      url: env.DATABASE_URL,
    },
  },
});

process.on('beforeExit', async () => {
  await prisma.$disconnect();
  logger.info('Disconnected Prisma client');
});
