# Repository Guidelines

## Project Structure & Module Organization
- Planning docs live in `documentation/`; keep them aligned with delivered features and update the relevant phase outline when scope shifts.
- Add backend sources under `backend/src` (Express controllers, services, Prisma client) and keep Prisma schema and migrations in `backend/prisma`.
- Place React screens and feature slices in `frontend/src/features`, with shared UI atoms in `frontend/src/components` and routing in `frontend/src/app`.

## Build, Test, and Development Commands
- `npm install` from the repo root installs workspace dependencies; run this after pulling.
- `npm run dev` should start API and web via `concurrently`; default to ports 4000 (API) and 3000 (web).
- `npm run migrate` bridges Prisma schema to the database (`prisma migrate dev` under the hood); call before seeding.
- `npm run seed` populates the demo admin, baseline services, and inventory.

## Coding Style & Naming Conventions
- Use modern ES modules with 2-space indentation and required semicolons; lint with ESLint and Prettier before pushing.
- Name files by responsibility: `*.controller.js`, `*.service.js`, and React components in `PascalCase.jsx`.
- Keep environment variables camel-cased with a `SALON_` prefix (for example, `SALON_DATABASE_URL`) and mirror them in `.env.example`.
- Document new routes and models in `documentation/pages.md` or `documentation/concept.md` as appropriate.

## Testing Guidelines
- Rely on Jest for backend unit tests (`backend/src/**/*.test.js`) and React Testing Library for UI tests (`frontend/src/**/*.test.jsx`).
- Add end-to-end coverage with Playwright or Cypress focusing on booking, inventory deduction, and payment demo flows.
- `npm run test` executes unit suites; `npm run test:e2e` should boot disposable services and run end-to-end specs.

## Commit & Pull Request Guidelines
- Follow Conventional Commits (`feat:`, `fix:`, `chore:`) for searchable history; scope by layer when possible (`feat(api): add booking cap`).
- Keep commits focused; run lint, tests, and migrations locally before pushing.
- Pull requests need a summary, checklist of affected docs, linked issue, and screenshots or GIFs for UI changes.
- Mention data migrations and required environment variables in the PR description so deployments stay predictable.

## Environment & Security Notes
- Never commit `.env` or Prisma migration outputs containing secrets; share credentials through the password manager.
- Use per-developer `.env.local` files and document required variables in `.env.example`.
- Rotate seeded admin passwords after demos and revoke leaked credentials immediately in both the database and seed scripts.
