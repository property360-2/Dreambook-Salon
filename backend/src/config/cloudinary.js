import { v2 as cloudinary } from 'cloudinary';

import { env } from './env.js';

if (env.CLOUDINARY_URL) {
  process.env.CLOUDINARY_URL = env.CLOUDINARY_URL;
  cloudinary.config({ secure: true });
} else if (env.CLOUDINARY_CLOUD_NAME && env.CLOUDINARY_API_KEY && env.CLOUDINARY_API_SECRET) {
  cloudinary.config({
    cloud_name: env.CLOUDINARY_CLOUD_NAME,
    api_key: env.CLOUDINARY_API_KEY,
    api_secret: env.CLOUDINARY_API_SECRET,
    secure: true,
  });
}

export { cloudinary };
