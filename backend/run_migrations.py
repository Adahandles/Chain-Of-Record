"""Helper script to run Alembic migrations."""
import sys
from alembic.config import Config
from alembic import command

def run_migrations():
    """Run Alembic migrations."""
    alembic_cfg = Config("alembic.ini")
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "revision":
            message = sys.argv[2] if len(sys.argv) > 2 else "auto migration"
            command.revision(alembic_cfg, autogenerate=True, message=message)
        elif cmd == "upgrade":
            command.upgrade(alembic_cfg, "head")
        elif cmd == "downgrade":
            command.downgrade(alembic_cfg, "-1")
    else:
        print("Usage: python run_migrations.py [revision|upgrade|downgrade] [message]")

if __name__ == "__main__":
    run_migrations()
