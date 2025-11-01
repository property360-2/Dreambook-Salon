import {
  createDemoPaymentSchema,
  updateDemoPaymentSchema,
} from './payment.schema.js';
import {
  createDemoPayment,
  getPayment,
  updateDemoPayment,
} from './payment.service.js';

export async function getDemoPayment(req, res, next) {
  try {
    const payment = await getPayment(req.params.id);
    res.json({ payment });
  } catch (error) {
    if (error.code === 'P2025' && !error.status) {
      error.status = 404;
      error.message = 'Payment not found';
    }
    next(error);
  }
}

export async function postDemoPayment(req, res, next) {
  try {
    const payload = createDemoPaymentSchema.parse(req.body);
    const payment = await createDemoPayment(payload, req.user);
    res.status(201).json({ payment });
  } catch (error) {
    if (error.name === 'ZodError') {
      error.status = 400;
      error.message = error.errors?.[0]?.message ?? 'Invalid request payload';
    }
    next(error);
  }
}

export async function putDemoPayment(req, res, next) {
  try {
    const payload = updateDemoPaymentSchema.parse(req.body);
    const payment = await updateDemoPayment(req.params.id, payload, req.user);
    res.json({ payment });
  } catch (error) {
    if (error.name === 'ZodError') {
      error.status = 400;
      error.message = error.errors?.[0]?.message ?? 'Invalid request payload';
    }
    next(error);
  }
}
