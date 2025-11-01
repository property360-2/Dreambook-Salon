import { Router } from 'express';

import { requireAuth, requireRoles } from '../../middleware/auth.js';
import {
  getAppointmentAvailability,
  getAppointments,
  postAppointment,
  putAppointmentStatus,
} from './appointment.controller.js';

export const appointmentRouter = Router();

appointmentRouter.get('/available', getAppointmentAvailability);
appointmentRouter.get('/', requireAuth, requireRoles('ADMIN', 'STAFF'), getAppointments);
appointmentRouter.post('/', postAppointment);
appointmentRouter.put(
  '/:id/status',
  requireAuth,
  requireRoles('ADMIN', 'STAFF'),
  putAppointmentStatus,
);
