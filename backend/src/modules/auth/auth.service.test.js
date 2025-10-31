import { beforeEach, describe, expect, jest, test } from '@jest/globals';

const mockFindUnique = jest.fn();
const mockCreate = jest.fn();
const mockHashPassword = jest.fn();
const mockVerifyPassword = jest.fn();

jest.unstable_mockModule('../../lib/prisma.js', () => ({
  prisma: {
    user: {
      findUnique: mockFindUnique,
      create: mockCreate,
    },
  },
}));

jest.unstable_mockModule('../../utils/password.js', () => ({
  hashPassword: mockHashPassword,
  verifyPassword: mockVerifyPassword,
}));

const { registerUser, authenticateUser, toPublicProfile } = await import('./auth.service.js');

const baseUser = {
  id: 'user_123',
  name: 'Alex Stylist',
  email: 'alex@salon.test',
  passwordHash: 'hashed',
  role: 'CUSTOMER',
  createdAt: new Date('2024-01-01T00:00:00.000Z'),
  updatedAt: new Date('2024-01-02T00:00:00.000Z'),
};

beforeEach(() => {
  jest.clearAllMocks();
});

describe('registerUser', () => {
  test('creates a customer with hashed password when email is available', async () => {
    mockFindUnique.mockResolvedValueOnce(null);
    mockHashPassword.mockResolvedValueOnce('hashed-secret');
    mockCreate.mockResolvedValueOnce({
      ...baseUser,
      email: baseUser.email,
      passwordHash: 'hashed-secret',
    });

    const result = await registerUser({
      name: 'Alex Stylist',
      email: 'Alex@Salon.Test',
      password: 'secret123',
    });

    expect(mockFindUnique).toHaveBeenCalledWith({
      where: { email: 'alex@salon.test' },
    });
    expect(mockHashPassword).toHaveBeenCalledWith('secret123');
    expect(mockCreate).toHaveBeenCalledWith({
      data: {
        name: 'Alex Stylist',
        email: 'alex@salon.test',
        passwordHash: 'hashed-secret',
        role: 'CUSTOMER',
      },
    });
    expect(result).toMatchObject({
      id: 'user_123',
      name: 'Alex Stylist',
      email: 'alex@salon.test',
      role: 'CUSTOMER',
    });
    expect(result).not.toHaveProperty('passwordHash');
  });

  test('throws a 409 error when email already exists', async () => {
    mockFindUnique.mockResolvedValueOnce(baseUser);

    await expect(
      registerUser({
        name: 'Alex Stylist',
        email: 'alex@salon.test',
        password: 'secret123',
      }),
    ).rejects.toMatchObject({
      message: 'Email already in use',
      status: 409,
    });
    expect(mockCreate).not.toHaveBeenCalled();
  });
});

describe('authenticateUser', () => {
  test('returns sanitized user when password matches', async () => {
    mockFindUnique.mockResolvedValueOnce(baseUser);
    mockVerifyPassword.mockResolvedValueOnce(true);

    const result = await authenticateUser({
      email: 'Alex@Salon.Test',
      password: 'secret123',
    });

    expect(mockFindUnique).toHaveBeenCalledWith({
      where: { email: 'alex@salon.test' },
    });
    expect(mockVerifyPassword).toHaveBeenCalledWith('secret123', 'hashed');
    expect(result).toEqual({
      id: 'user_123',
      name: 'Alex Stylist',
      email: 'alex@salon.test',
      role: 'CUSTOMER',
      createdAt: baseUser.createdAt,
      updatedAt: baseUser.updatedAt,
    });
  });

  test('throws a 401 error when user does not exist', async () => {
    mockFindUnique.mockResolvedValueOnce(null);

    await expect(
      authenticateUser({
        email: 'missing@salon.test',
        password: 'secret123',
      }),
    ).rejects.toMatchObject({
      message: 'Invalid email or password',
      status: 401,
    });
  });

  test('throws a 401 error when password is incorrect', async () => {
    mockFindUnique.mockResolvedValueOnce(baseUser);
    mockVerifyPassword.mockResolvedValueOnce(false);

    await expect(
      authenticateUser({
        email: 'alex@salon.test',
        password: 'wrong',
      }),
    ).rejects.toMatchObject({
      message: 'Invalid email or password',
      status: 401,
    });
  });
});

describe('toPublicProfile', () => {
  test('strips sensitive fields while retaining public metadata', () => {
    const profile = toPublicProfile(baseUser);
    expect(profile).toEqual({
      id: 'user_123',
      name: 'Alex Stylist',
      email: 'alex@salon.test',
      role: 'CUSTOMER',
      createdAt: baseUser.createdAt,
      updatedAt: baseUser.updatedAt,
    });
  });
});
