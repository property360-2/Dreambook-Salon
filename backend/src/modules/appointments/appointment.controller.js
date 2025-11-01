import {
  availabilityQuerySchema,
  createAppointmentSchema,
  listAppointmentsQuerySchema,
  updateAppointmentStatusSchema,
} from './appointment.schema.js';
import {
  createAppointment,
  getAvailability,
  listAppointments,
  updateAppointmentStatus,
} from './appointment.service.js';

export async function getAppointmentAvailability(req, res, next) {
  try {
    const params = availabilityQuerySchema.parse(req.query);
    const availability = await getAvailability(params);
    res.json(availability);
  } catch (error) {
    if (error.name === 'ZodError') {
      error.status = 400;
      error.message = error.errors?.[0]?.message ?? 'Invalid query parameters';
    }
    next(error);
  }
}

export async function getAppointments(req, res, next) {
  try {
    const filters = listAppointmentsQuerySchema.parse(req.query);
    const appointments = await listAppointments(filters);
    res.json({ appointments });
  } catch (error) {
    if (error.name === 'ZodError') {
      error.status = 400;
      error.message = error.errors?.[0]?.message ?? 'Invalid query parameters';
    }
    next(error);
  }
}

export async function postAppointment(req, res, next) {
  try {
    const payload = createAppointmentSchema.parse(req.body);
    const result = await createAppointment(payload, req.user);
    res.status(201).json(result);
  } catch (error) {
    if (error.name === 'ZodError') {
      error.status = 400;
      error.message = error.errors?.[0]?.message ?? 'Invalid request payload';
    }
    next(error);
  }
}

export async function putAppointmentStatus(req, res, next) {
  try {
    const payload = updateAppointmentStatusSchema.parse(req.body);
    const result = await updateAppointmentStatus(req.params.id, payload, req.user);
    res.json(result);
  } catch (error) {
    if (error.name === 'ZodError') {
      error.status = 400;
      error.message = error.errors?.[0]?.message ?? 'Invalid request payload';
    }
    next(error);
  }
}
