# Repository Guidelines

## Project Structure & Module Organization
The Django project lives in `salon_system/` with domain apps in `core`, `services`, `inventory`, `appointments`, `payments`, `chatbot`, and `analytics`. Share utilities (email, permissions, mixins) via `core/`. Templates follow atomic design: place reusable pieces in `templates/components/atoms|molecules|organisms`, assemble screen-specific layouts in `templates/pages/`, and keep partials DRY with `{% include %}`. Static assets (CSS/JS/icons) belong in `static/` and should be CDN-friendly; reference them with `static` tags so `collectstatic` can sync to Cloudflare or S3. Put database fixtures and demo commands inside each app’s `management/` packages (e.g., `appointments/management/commands/seed_demo.py`).

## Build, Test, and Development Commands
Use `make dev` for the default `python manage.py runserver` + watcher setup, and `make migrate` to wrap `python manage.py migrate`. Execute `make test` (or `python manage.py test`) before every push. `make lint` runs `black`, `isort`, `flake8`, and `djlint`; fix issues locally before CI. For CDN prep, run `python manage.py collectstatic --noinput` and verify the bucket sync script in `Makefile deploy-static`.

## Coding Style & Naming Conventions
Follow 4-space indentation and PEP 8 for Python modules. Name Django apps, modules, and functions with `snake_case`; keep classes and Django models in `PascalCase`. Template blocks and CSS utility classes mirror the atomic taxonomy (e.g., `atom-button`, `molecule-service-card`). Always import Django settings via `from django.conf import settings`, and prefer environment access with `django-environ` helpers.

## Testing Guidelines
Co-locate tests beside their apps (`appointments/tests/test_availability.py`) and mirror the feature name in filenames. Target 80%+ coverage for scheduling and inventory flows; add regression tests for slot locking, stock deduction, and payment callbacks. Include Django test client scenarios for booking and dashboard views, and update the seed command so E2E smoke tests can run against seeded data.

## Commit & Pull Request Guidelines
History shows conventional prefixes (`feat:`, `fix:`, `chore:`); continue using them with concise, imperative summaries. Group unrelated changes into separate commits. PRs need: a short problem statement, bullet list of changes, linked phase/issue, screenshots or terminal output for UI/CLI updates, and confirmation that `make lint` and `make test` passed. Request review before merging to main.
