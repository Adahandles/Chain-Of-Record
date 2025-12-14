# Database Migrations with Alembic

## Initial Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Alembic installation:**
   ```bash
   python -m alembic --version
   ```

## Running Migrations

### Method 1: Using Python Module (Recommended)
```bash
cd /workspaces/Chain-Of-Record/backend
python -m alembic revision --autogenerate -m "initial core tables"
python -m alembic upgrade head
```

### Method 2: Using Helper Script
```bash
cd /workspaces/Chain-Of-Record/backend
python run_migrations.py revision "initial core tables"
python run_migrations.py upgrade
```

### Method 3: Direct CLI (if alembic is on PATH)
```bash
cd /workspaces/Chain-Of-Record/backend
alembic revision --autogenerate -m "initial core tables"
alembic upgrade head
```

## Common Issues

### "Command not found" error
- Use `python -m alembic` instead of `alembic`
- Ensure you're in the correct directory (`backend`)
- Verify Alembic is installed: `pip show alembic`

### "No file system provider" error
- This indicates a PATH or environment issue
- Use the Python module invocation method
- Consider reloading the Codespace

## Creating New Migrations

```bash
python -m alembic revision --autogenerate -m "description of changes"
python -m alembic upgrade head
```

## Viewing Migration History

```bash
python -m alembic history
python -m alembic current
```
