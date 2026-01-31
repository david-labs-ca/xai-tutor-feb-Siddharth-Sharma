# Development & Submission Guidelines

Follow these principles when working on this project.

---

## Core principles

1. **Focus on core functionality first, then add features incrementally**
   - Implement and verify one area (e.g. auth) before moving to the next (e.g. products, cart).
   - Prefer a small set of working endpoints over many half-finished ones.

2. **Test your application with `docker-compose up` before final submission**
   - The app **must** run with: `docker-compose up --build`
   - Run this before submitting to catch environment-specific issues (DB path, migrations, dependencies).

3. **A partially complete but working solution is better than a complete but broken one**
   - Prefer shipping working auth + products over broken cart.
   - If time is short, disable or simplify a feature rather than leaving it in a broken state.

---

## Before submission checklist

- [ ] **Run with Docker:** `docker-compose up --build` — app starts without errors.
- [ ] **Smoke test:** Health, register, login, and at least one protected endpoint work (e.g. GET /cart with token).
- [ ] **Migrations:** `python migrate.py upgrade` runs cleanly (or runs automatically in Docker CMD).
- [ ] **Tests:** `pytest tests/ -v` passes (use a clean test DB: `rm -f tests/test_app.db` if needed).

---

## Quick Docker smoke test

After `docker-compose up -d`:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"email":"u@example.com","password":"pass123"}'
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"u@example.com","password":"pass123"}'
# Use the token from login in: curl http://localhost:8000/cart -H "Authorization: Bearer <token>"
```

Or run the script: `./scripts/test_api.sh` (with server already running).
