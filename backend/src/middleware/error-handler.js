import { logger } from '../config/logger.js';

export function errorHandler(err, _req, res, _next) {
  logger.error(
    {
      err,
      message: err.message,
    },
    'Unhandled error',
  );

  const status = err.status ?? 500;
  const message =
    status >= 500
      ? 'Something went wrong, please try again later.'
      : err.message;

  res.status(status).json({ message });
}
