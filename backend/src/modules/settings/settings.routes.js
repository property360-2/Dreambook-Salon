import { Router } from 'express';

import { requireAuth, requireRoles } from '../../middleware/auth.js';
import {
  deleteBlockedRangeHandler,
  getBlockedRanges,
  getSalonSettings,
  postBlockedRange,
  putSalonSettings,
} from './settings.controller.js';

export const settingsRouter = Router();

settingsRouter.get('/', requireAuth, requireRoles('ADMIN', 'STAFF'), getSalonSettings);
settingsRouter.put('/', requireAuth, requireRoles('ADMIN'), putSalonSettings);

settingsRouter.get(
  '/blocked',
  requireAuth,
  requireRoles('ADMIN', 'STAFF'),
  getBlockedRanges,
);
settingsRouter.post('/blocked', requireAuth, requireRoles('ADMIN'), postBlockedRange);
settingsRouter.delete(
  '/blocked/:id',
  requireAuth,
  requireRoles('ADMIN'),
  deleteBlockedRangeHandler,
);
