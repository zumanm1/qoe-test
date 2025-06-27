# Database Migrations

This directory contains database migrations for the MTN Network QoE Web Application.

## How to Run Migrations

To initialize and run migrations:

1. Initialize migrations (first-time only):
```
flask db init
```

2. Create a new migration after model changes:
```
flask db migrate -m "Description of changes"
```

3. Apply migrations to the database:
```
flask db upgrade
```

4. Revert migrations if needed:
```
flask db downgrade
```

## Migration Files

- `versions/`: Contains version files for each migration
- `script.py.mako`: Template for migration files
- `alembic.ini`: Alembic configuration file
- `env.py`: Environment configuration for migrations
