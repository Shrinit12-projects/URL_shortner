# app/routes.py
from typing import Optional
from fastapi import APIRouter, HTTPException
from app.models import urls
from app.database import database
from app.schema import URLCreate, URLResponse
from shortuuid import uuid
from sqlalchemy import select, and_
from datetime import datetime, timedelta

router = APIRouter()

# Generate a shortened URL or alias
@router.post("/shorten", response_model=URLResponse)
async def shorten_url(url_data: URLCreate):
    # Check if custom alias already exists
    if url_data.alias:
        existing_alias = await database.fetch_one(query=select(urls).where(urls.c.alias == url_data.alias))
        if existing_alias:
            raise HTTPException(status_code=400, detail="Alias already exists")
        short_url = url_data.alias
    else:
        short_url = uuid()[:6]  # Generate short UUID if no alias is provided

    # Calculate TTL expiration date if provided
    ttl_date = datetime.utcnow() + timedelta(seconds=url_data.ttl) if url_data.ttl else None

    # Insert the new short URL record
    query = urls.insert().values(
        original_url=str(url_data.original_url),
        short_url=short_url,
        alias=url_data.alias,
        ttl=ttl_date
    )
    await database.execute(query)

    return URLResponse(
        original_url=url_data.original_url,
        short_url=short_url,
        alias=url_data.alias,
        ttl=ttl_date,
        created_at=datetime.utcnow()
    )


# Redirect to the original URL
@router.get("/{short_url}")
async def redirect_to_url(short_url: str):
    # Find the URL by its short_url
    query = select(urls).where(and_(urls.c.short_url == short_url, urls.c.is_active == True))
    url = await database.fetch_one(query)

    if not url:
        raise HTTPException(status_code=404, detail="URL not found or has expired")

    # Check if TTL has expired
    if url["ttl"] and url["ttl"] < datetime.utcnow():
        raise HTTPException(status_code=410, detail="URL has expired")

    return {"original_url": url["original_url"]}


# Delete a shortened URL
@router.delete("/delete/{short_url}")
async def delete_url(short_url: str):
    query = urls.delete().where(urls.c.short_url == short_url)
    result = await database.execute(query)

    if result == 0:
        raise HTTPException(status_code=404, detail="URL not found")

    return {"message": "URL deleted successfully"}


# Update URL alias or TTL
@router.put("/update/{short_url}")
async def update_url(short_url: str, alias: Optional[str] = None, ttl: Optional[int] = None):
    update_data = {}

    if alias:
        # Check if the new alias is already in use
        existing_alias = await database.fetch_one(query=select(urls).where(urls.c.alias == alias))
        if existing_alias:
            raise HTTPException(status_code=400, detail="Alias already exists")
        update_data["alias"] = alias
        update_data["short_url"] = alias

    if ttl:
        update_data["ttl"] = datetime.utcnow() + timedelta(seconds=ttl)

    query = urls.update().where(urls.c.short_url == short_url).values(update_data)
    result = await database.execute(query)

    if result == 0:
        raise HTTPException(status_code=404, detail="URL not found")

    return {"message": "URL updated successfully"}
