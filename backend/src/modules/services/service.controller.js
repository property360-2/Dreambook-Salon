import { createServiceSchema, serviceInventoryLinkSchema } from './service.schema.js';
import {
  createService,
  linkInventoryToService,
  listServices,
  unlinkInventoryFromService,
} from './service.service.js';

export async function getServices(req, res, next) {
  try {
    const includeInactive = req.query.includeInactive === 'true';
    const services = await listServices({ includeInactive });
    res.json({ services });
  } catch (error) {
    next(error);
  }
}

export async function postService(req, res, next) {
  try {
    const payload = createServiceSchema.parse(req.body);
    const service = await createService(payload, req.user);
    res.status(201).json({ service });
  } catch (error) {
    if (error.name === 'ZodError') {
      error.status = 400;
      error.message = error.errors?.[0]?.message ?? 'Invalid request payload';
    }
    next(error);
  }
}

export async function postServiceInventory(req, res, next) {
  try {
    const payload = serviceInventoryLinkSchema.parse(req.body);
    const link = await linkInventoryToService(req.params.id, payload);
    res.status(201).json({ link });
  } catch (error) {
    if (error.name === 'ZodError') {
      error.status = 400;
      error.message = error.errors?.[0]?.message ?? 'Invalid request payload';
    }
    if ((error.code === 'P2025' || error.code === 'P2003') && !error.status) {
      error.status = 404;
      error.message = 'Service or inventory item not found';
    }
    next(error);
  }
}

export async function deleteServiceInventory(req, res, next) {
  try {
    await unlinkInventoryFromService(req.params.id, req.params.inventoryId);
    res.status(204).send();
  } catch (error) {
    if (error.code === 'P2025' && !error.status) {
      error.status = 404;
      error.message = 'Service inventory link not found';
    }
    next(error);
  }
}
