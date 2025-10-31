import { Router } from 'express';

import { requireAuth, requireRoles } from '../../middleware/auth.js';

import {
  getInventory,
  postInventory,
  putInventory,
} from './inventory.controller.js';

export const inventoryRouter = Router();

inventoryRouter.use(requireAuth, requireRoles('ADMIN'));

inventoryRouter.get('/', getInventory);
inventoryRouter.post('/', postInventory);
inventoryRouter.put('/:id', putInventory);
