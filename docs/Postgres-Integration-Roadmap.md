# Roadmap: Integrating PostgreSQL Database with the App

## Objective
Implement a PostgreSQL database to support persistent storage for the application, replacing or complementing current file-based storage.

---

## Documentation Index
- [Data Model Design](postgres-integration/data-model.md)
- [Migration Scripts](postgres-integration/migration-scripts.md)
- [Backend Integration Guide](postgres-integration/backend-integration.md)
- [Testing & Validation](postgres-integration/testing.md)
- [Troubleshooting & FAQ](postgres-integration/troubleshooting.md)

---

> **Icon legend:**
> - 🚧 Started
> - ✅ Completed
> - ⬜️ Not started

## 1. Planning and Preparation
- ✅ Review current data usage: [see details](postgres-integration/PIR-data-usage-review.md)
- 🚧 Define data models: [see details](postgres-integration/data-model.md)
- ⬜️ Decide migration scope

---

## 2. Docker & Environment Setup
- Add a PostgreSQL service to `docker-compose.yml`.
- Configure environment variables for DB connection in `.env` and app config files.
- Expose and map the default PostgreSQL port (5432).

---

## 3. Backend Integration
- Install and configure an async PostgreSQL client (e.g., `asyncpg` or `SQLAlchemy` with async support) in the backend (FastAPI).
- Create database connection utilities and dependency injection for FastAPI endpoints.
- Implement CRUD operations for:
  - Historical price data
  - Strategy configurations
  - Backtest results
  - (Optional) User/session data
- Update API endpoints to use the database instead of file-based storage where appropriate.

---

## 4. Data Migration
- Write scripts to migrate essential data from CSVs to PostgreSQL tables.
- Validate data integrity after migration.
- Archive or deprecate old CSVs if no longer needed.

---

## 5. Frontend Adjustments
- Update frontend API calls if endpoints or data formats change due to DB integration.
- Ensure UI reflects new data sources and supports new features (e.g., filtering, pagination).

---

## 6. Testing & Validation
- Add tests for DB connection, migrations, and CRUD operations.
- Check performance and error handling for DB operations.
- Validate that all features work as expected with the new database.

---

## 7. Documentation
- Update README and developer docs to include DB setup, environment variables, and usage instructions.

---

## What May Not Need Migration
- Static configuration files (e.g., `config.yaml`) if not frequently changed.
- Log files (unless you want to store logs in the DB).
- Large historical CSVs that are only used for initial import.
- Temporary or cache data.

---

## Checklist Before Production
- [ ] Database service runs and is accessible from backend
- [ ] All required tables and indexes are created
- [ ] Environment variables are set and loaded correctly
- [ ] Data migration scripts tested and validated
- [ ] All endpoints using DB are tested
- [ ] Rollback/backup strategy in place
- [ ] Security: DB user permissions, password management, network access

---

## Future Improvements & Features
- User authentication and authorization with DB-backed sessions
- Advanced analytics and reporting using SQL queries
- Real-time data ingestion and event storage
- Support for multiple users and roles
- Automated backups and monitoring
- Integration with other data sources (APIs, external DBs)
- Data versioning and audit trails

---

**This roadmap provides a step-by-step guide for integrating PostgreSQL into the app, ensuring a robust and scalable data layer for current and future needs.**
