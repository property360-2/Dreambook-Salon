import { signAccessToken } from '../../utils/jwt.js';

import { loginSchema, registerSchema } from './auth.schema.js';
import {
  authenticateUser,
  registerUser,
  toPublicProfile,
} from './auth.service.js';

export async function register(req, res, next) {
  try {
    const payload = registerSchema.parse(req.body);
    const user = await registerUser(payload);

    const token = signAccessToken({
      sub: user.id,
      role: user.role,
    });

    res.status(201).json({
      user: toPublicProfile(user),
      token,
    });
  } catch (error) {
    if (error.name === 'ZodError') {
      const validationError = new Error(
        error.errors?.[0]?.message ?? 'Invalid request payload',
      );
      validationError.status = 400;
      validationError.details = error.errors;
      return next(validationError);
    }
    next(error);
  }
}

export async function login(req, res, next) {
  try {
    const payload = loginSchema.parse(req.body);
    const user = await authenticateUser(payload);

    const token = signAccessToken({
      sub: user.id,
      role: user.role,
    });

    res.json({
      user: toPublicProfile(user),
      token,
    });
  } catch (error) {
    if (error.name === 'ZodError') {
      const validationError = new Error(
        error.errors?.[0]?.message ?? 'Invalid request payload',
      );
      validationError.status = 400;
      validationError.details = error.errors;
      return next(validationError);
    }
    next(error);
  }
}
