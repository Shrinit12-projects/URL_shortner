# app/schemas.py
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class URLCreate(BaseModel):
    original_url: HttpUrl  # Validates the original URL
    alias: Optional[str] = None  # Optional custom alias
    ttl: Optional[int] = None  # TTL in seconds (optional)

class URLResponse(BaseModel):
    original_url: HttpUrl
    short_url: str
    alias: Optional[str] = None
    ttl: Optional[datetime] = None
    created_at: datetime
