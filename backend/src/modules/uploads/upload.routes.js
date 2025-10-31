import { Router } from 'express';

import { requireAuth, requireRoles } from '../../middleware/auth.js';

import { uploadServiceImage } from './upload.controller.js';

export const uploadRouter = Router();

uploadRouter.post(
  '/service-image',
  requireAuth,
  requireRoles('ADMIN'),
  uploadServiceImage,
);
