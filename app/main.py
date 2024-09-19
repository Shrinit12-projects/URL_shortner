import logging
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from app.routes import router as url_router
from app.database import database, engine, metadata
from datetime import datetime
from app.models import urls

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function for cleaning up expired URLs (async)
async def cleanup_expired_urls():
    logger.info("Running cleanup job")
    query = urls.delete().where(urls.c.ttl < datetime.utcnow())
    result = await database.execute(query)
    logger.info(f"Deleted {result} expired URLs")

# Scheduler setup
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    metadata.create_all(engine)
    await database.connect()

    # Schedule the background cleanup job to run every minute
    logger.info("Scheduling cleanup job")
    scheduler.add_job(cleanup_expired_urls, 'interval', minutes=1)
    scheduler.start()

    # Yield control back to FastAPI to run the app
    yield

    # Shutdown event
    logger.info("Shutting down scheduler")
    scheduler.shutdown()
    await database.disconnect()

# Pass the lifespan context to the FastAPI instance
app = FastAPI(lifespan=lifespan)

# Include your routes
app.include_router(url_router)

# Root endpoint
@app.get("/")
def root():
    return {"message": "URL Shortener API"}
