from sqlalchemy import create_engine, MetaData
from app.core.config import settings
engine=create_engine(settings.database_url,pool_pre_ping=True,pool_recycle=1800,connect_args={'connect_timeout':10}) if settings.database_url else None
metadata=MetaData()
def reflect_schema():
    if engine is None:return []
    metadata.reflect(bind=engine);return sorted(metadata.tables)
