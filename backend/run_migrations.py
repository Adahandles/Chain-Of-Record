"""Helper script to run Alembic migrations."""
import sys
from alembic.config import Config
from alembic import command

def run_migrations():
    """Run Alembic migrations."""
    try:
        alembic_cfg = Config("alembic.ini")
        
        if len(sys.argv) > 1:
            cmd = sys.argv[1]
            if cmd == "revision":
                message = sys.argv[2] if len(sys.argv) > 2 else "Automated migration"
                command.revision(alembic_cfg, autogenerate=True, message=message)
                print(f"Migration created successfully: {message}")
            elif cmd == "upgrade":
                command.upgrade(alembic_cfg, "head")
                print("Migrations applied successfully")
            elif cmd == "downgrade":
                # Accept optional revision argument, default to "-1"
                revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
                command.downgrade(alembic_cfg, revision)
                print(f"Migration downgraded successfully to revision: {revision}")
            else:
                print(f"Unknown command: {cmd}")
                print("Usage: python run_migrations.py [revision|upgrade|downgrade] [message|revision]")
                sys.exit(1)
        else:
            print("Usage: python run_migrations.py [revision|upgrade|downgrade] [message|revision]")
            sys.exit(1)
    except Exception as e:
        print(f"Error running migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
