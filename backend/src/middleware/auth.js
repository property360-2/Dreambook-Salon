import { prisma } from '../lib/prisma.js';
import { verifyAccessToken } from '../utils/jwt.js';

const UNAUTHORIZED_MESSAGE = 'Authentication required';

function extractToken(req) {
  const header = req.headers.authorization;
  if (header?.startsWith('Bearer ')) {
    return header.slice('Bearer '.length);
  }
  return null;
}

export async function authenticate(req, _res, next) {
  try {
    const token = extractToken(req);
    if (!token) {
      return next();
    }

    const payload = verifyAccessToken(token);

    const user = await prisma.user.findUnique({
      where: { id: payload.sub },
    });

    if (!user) {
      return next();
    }

    req.user = {
      id: user.id,
      email: user.email,
      name: user.name,
      role: user.role,
    };

    next();
  } catch (error) {
    error.status = 401;
    next(error);
  }
}

export async function requireAuth(req, res, next) {
  await authenticate(req, res, async (err) => {
    if (err) return next(err);
    if (!req.user) {
      return res.status(401).json({ message: UNAUTHORIZED_MESSAGE });
    }
    next();
  });
}

export function requireRoles(...roles) {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ message: UNAUTHORIZED_MESSAGE });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ message: 'Forbidden' });
    }

    next();
  };
}
