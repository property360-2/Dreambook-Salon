import { beforeEach, describe, expect, jest, test } from '@jest/globals';

const mockLoggerError = jest.fn();

jest.unstable_mockModule('../config/logger.js', () => ({
  logger: {
    error: mockLoggerError,
  },
}));

const { errorHandler } = await import('./error-handler.js');

const createResponse = () => {
  const status = jest.fn().mockReturnThis();
  const json = jest.fn();

  return {
    res: {
      status,
      json,
    },
    status,
    json,
  };
};

describe('errorHandler', () => {
  beforeEach(() => {
    mockLoggerError.mockClear();
  });

  test('returns provided status and message for application errors', () => {
    const err = new Error('Invalid input');
    err.status = 400;
    const { res, status, json } = createResponse();

    errorHandler(err, {}, res, () => {});

    expect(status).toHaveBeenCalledWith(400);
    expect(json).toHaveBeenCalledWith({ message: 'Invalid input' });
    expect(mockLoggerError).toHaveBeenCalledTimes(1);
    expect(mockLoggerError.mock.calls[0][0]).toMatchObject({
      message: 'Invalid input',
    });
  });

  test('falls back to 500 status and generic message for server errors', () => {
    const err = new Error('Database unavailable');
    const { res, status, json } = createResponse();

    errorHandler(err, {}, res, () => {});

    expect(status).toHaveBeenCalledWith(500);
    expect(json).toHaveBeenCalledWith({
      message: 'Something went wrong, please try again later.',
    });
    expect(mockLoggerError).toHaveBeenCalledTimes(1);
    expect(mockLoggerError.mock.calls[0][0]).toMatchObject({
      message: 'Database unavailable',
    });
  });
});
