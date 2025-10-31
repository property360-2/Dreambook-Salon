import {
  createInventorySchema,
  updateInventorySchema,
} from './inventory.schema.js';
import {
  createInventory,
  listInventory,
  updateInventory,
} from './inventory.service.js';

function handleValidationError(error) {
  if (error.name === 'ZodError') {
    error.status = 400;
    error.message = error.errors?.[0]?.message ?? 'Invalid request payload';
  }
}

export async function getInventory(_req, res, next) {
  try {
    const inventory = await listInventory();
    res.json({ inventory });
  } catch (error) {
    next(error);
  }
}

export async function postInventory(req, res, next) {
  try {
    const payload = createInventorySchema.parse(req.body);
    const item = await createInventory(payload);
    res.status(201).json({ inventory: item });
  } catch (error) {
    handleValidationError(error);
    next(error);
  }
}

export async function putInventory(req, res, next) {
  try {
    const payload = updateInventorySchema.parse(req.body);
    const item = await updateInventory(req.params.id, payload);
    res.json({ inventory: item });
  } catch (error) {
    handleValidationError(error);
    if (error.code === 'P2025') {
      error.status = 404;
      error.message = 'Inventory item not found';
    }
    next(error);
  }
}
