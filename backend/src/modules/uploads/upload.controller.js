import { z } from 'zod';

import { cloudinary } from '../../config/cloudinary.js';
import { env } from '../../config/env.js';

const uploadSchema = z.object({
  image: z
    .string()
    .min(1, 'Image data is required')
    .max(10_000_000, 'Image payload too large'),
});

export async function uploadServiceImage(req, res, next) {
  try {
    if (!env.isCloudinaryConfigured) {
      const error = new Error('Image uploads are not configured');
      error.status = 503;
      throw error;
    }

    const { image } = uploadSchema.parse(req.body);

    const result = await cloudinary.uploader.upload(image, {
      folder: 'dreambook-salon/services',
      overwrite: false,
      transformation: [{ width: 1600, height: 1600, crop: 'limit' }],
    });

    res.status(201).json({
      url: result.secure_url,
      publicId: result.public_id,
      width: result.width,
      height: result.height,
    });
  } catch (error) {
    if (error.name === 'ZodError') {
      const validationError = new Error(
        error.errors?.[0]?.message ?? 'Invalid image payload',
      );
      validationError.status = 400;
      return next(validationError);
    }

    next(error);
  }
}
