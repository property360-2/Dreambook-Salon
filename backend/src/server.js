import { app } from './app.js';
import { env } from './config/env.js';
import { logger } from './config/logger.js';

const port = env.PORT;

const server = app.listen(port, () => {
  logger.info(`API listening on port ${port}`);
});

server.on('error', (error) => {
  if (error.code === 'EADDRINUSE') {
    logger.error(
      `Port ${port} is busy. Set PORT to a free port or stop the other process.`,
    );
    process.exit(1);
  }

  logger.error(error, 'Server failed to start');
  process.exit(1);
});
