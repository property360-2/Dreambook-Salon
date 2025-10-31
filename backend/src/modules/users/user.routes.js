import { Router } from 'express';

import { requireAuth } from '../../middleware/auth.js';

import { getCurrentUser } from './user.controller.js';

export const userRouter = Router();

userRouter.get('/me', requireAuth, getCurrentUser);
