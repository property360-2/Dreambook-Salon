import { Router } from 'express';

import { requireAuth, requireRoles } from '../../middleware/auth.js';

import {
  deleteServiceInventory,
  getServices,
  postService,
  postServiceInventory,
} from './service.controller.js';

export const serviceRouter = Router();

serviceRouter.get('/', getServices);
serviceRouter.post('/', requireAuth, requireRoles('ADMIN'), postService);
serviceRouter.post(
  '/:id/inventory',
  requireAuth,
  requireRoles('ADMIN'),
  postServiceInventory,
);
serviceRouter.delete(
  '/:id/inventory/:inventoryId',
  requireAuth,
  requireRoles('ADMIN'),
  deleteServiceInventory,
);
