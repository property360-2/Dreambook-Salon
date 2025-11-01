import { Router } from 'express';

import { getDemoPayment, postDemoPayment, putDemoPayment } from './payment.controller.js';

export const paymentRouter = Router();

paymentRouter.get('/demo/:id', getDemoPayment);
paymentRouter.post('/demo', postDemoPayment);
paymentRouter.put('/demo/:id', putDemoPayment);
