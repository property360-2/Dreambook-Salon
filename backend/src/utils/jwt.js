import jwt from 'jsonwebtoken';

import { env } from '../config/env.js';

const ACCESS_TOKEN_TTL = '1d';

export function signAccessToken(payload) {
  return jwt.sign(payload, env.JWT_SECRET, { expiresIn: ACCESS_TOKEN_TTL });
}

export function verifyAccessToken(token) {
  return jwt.verify(token, env.JWT_SECRET);
}
