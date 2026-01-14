from src.db.models import Base
from src.db.session import engine


# PUBLIC_INTERFACE
def init_db() -> None:
    """Initialize database schema required by this backend (creates missing tables)."""
    Base.metadata.create_all(bind=engine)
