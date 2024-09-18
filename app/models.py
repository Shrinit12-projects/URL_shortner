from sqlalchemy import Table, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import metadata

# SQLAlchemy model for the URLs table
urls = Table(
    "urls",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("original_url", Text, nullable=False),
    Column("short_url", String(255), unique=True, nullable=False),  # Auto-generated or custom alias
    Column("alias", String(255), unique=True, nullable=True),  # Custom alias
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("ttl", DateTime, nullable=True),  # Expiry time
    Column("is_active", Boolean, default=True)
)