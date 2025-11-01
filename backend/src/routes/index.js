import { Router } from 'express';

import { authRouter } from '../modules/auth/auth.routes.js';
import { appointmentRouter } from '../modules/appointments/appointment.routes.js';
import { chatbotRouter } from '../modules/chatbot/chatbot.routes.js';
import { inventoryRouter } from '../modules/inventory/inventory.routes.js';
import { paymentRouter } from '../modules/payments/payment.routes.js';
import { settingsRouter } from '../modules/settings/settings.routes.js';
import { serviceRouter } from '../modules/services/service.routes.js';
import { uploadRouter } from '../modules/uploads/upload.routes.js';
import { userRouter } from '../modules/users/user.routes.js';

export const router = Router();

router.get('/', (_req, res) => {
  res.json({ message: 'Dreambook Salon API' });
});

router.use('/auth', authRouter);
router.use('/appointments', appointmentRouter);
router.use('/services', serviceRouter);
router.use('/users', userRouter);
router.use('/inventory', inventoryRouter);
router.use('/uploads', uploadRouter);
router.use('/settings', settingsRouter);
router.use('/payments', paymentRouter);
router.use('/chatbot', chatbotRouter);
