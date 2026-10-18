from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import shutil

# On Vercel / serverless platforms, root filesystem is read-only.
# We must store the SQLite database in /tmp.
raw_db_url = os.getenv("DATABASE_URL")

if raw_db_url:
    DATABASE_URL = raw_db_url
elif os.getenv("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    tmp_db_path = "/tmp/test.db"
    # Copy pre-existing test.db if available
    local_db_path = os.path.join(os.path.dirname(__file__), "test.db")
    if not os.path.exists(tmp_db_path) and os.path.exists(local_db_path):
        try:
            shutil.copy(local_db_path, tmp_db_path)
        except Exception:
            pass
    DATABASE_URL = f"sqlite:///{tmp_db_path}"
else:
    DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
