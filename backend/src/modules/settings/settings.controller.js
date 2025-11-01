import {
  createBlockedRangeSchema,
  listBlockedRangesQuerySchema,
  updateSettingsSchema,
} from './settings.schema.js';
import {
  createBlockedRange,
  deleteBlockedRange,
  getSettings,
  listBlockedRanges,
  updateSettings,
} from './settings.service.js';

export async function getSalonSettings(_req, res, next) {
  try {
    const data = await getSettings({ includeBlockedRanges: true });
    res.json({
      settings: data.settings,
      blockedRanges: data.blockedRanges,
    });
  } catch (error) {
    next(error);
  }
}

export async function putSalonSettings(req, res, next) {
  try {
    const payload = updateSettingsSchema.parse(req.body);
    const updated = await updateSettings(payload);
    res.json({ settings: updated });
  } catch (error) {
    if (error.name === 'ZodError') {
      error.status = 400;
      error.message = error.errors?.[0]?.message ?? 'Invalid request payload';
    }
    next(error);
  }
}

export async function getBlockedRanges(req, res, next) {
  try {
    const filters = listBlockedRangesQuerySchema.parse(req.query);
    const ranges = await listBlockedRanges(filters);
    res.json({ blockedRanges: ranges });
  } catch (error) {
    if (error.name === 'ZodError') {
      error.status = 400;
      error.message = error.errors?.[0]?.message ?? 'Invalid query parameters';
    }
    next(error);
  }
}

export async function postBlockedRange(req, res, next) {
  try {
    const payload = createBlockedRangeSchema.parse(req.body);
    const range = await createBlockedRange(payload, req.user);
    res.status(201).json({ blockedRange: range });
  } catch (error) {
    if (error.name === 'ZodError') {
      error.status = 400;
      error.message = error.errors?.[0]?.message ?? 'Invalid request payload';
    }
    next(error);
  }
}

export async function deleteBlockedRangeHandler(req, res, next) {
  try {
    await deleteBlockedRange(req.params.id);
    res.status(204).send();
  } catch (error) {
    if (error.code === 'P2025' && !error.status) {
      error.status = 404;
      error.message = 'Blocked range not found';
    }
    next(error);
  }
}
