# Phase 2 Follow-ups (Next Session)

- [ ] **Service editing** – allow admins to update existing services (name, price, image) and persist `imageUrl` changes via PUT `/api/services/:id`.
- [ ] **Image lifecycle** – delete or detatch previous Cloudinary asset when an admin uploads a replacement or removes an image; store Cloudinary `public_id` to support cleanup.
- [ ] **UX polish** – add inline error messaging for image upload failures (service form) and show a placeholder image when no `imageUrl` exists.
- [ ] **API hardening** – add backend tests for `/api/uploads/service-image` and validation around file type/size before sending to Cloudinary.
- [ ] **Docs & env** – update deployment checklist with Cloudinary requirements (env vars, allowed file size) and note optional rate limits.
- [ ] **Seed refresh** – rerun `npm run seed --workspace backend` after clearing dev DB so services pick up the sample image URLs.
