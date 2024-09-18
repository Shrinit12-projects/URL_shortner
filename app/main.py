# app/main.py
from fastapi import FastAPI
from fastapi import Depends
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from app.routes import router as url_router
from app.database import database, engine, metadata
from datetime import datetime
from app.models import urls

# Function for cleaning up expired URLs
async def cleanup_expired_urls():
    query = urls.delete().where(urls.c.ttl < datetime.utcnow())
    await database.execute(query)

# Scheduler setup
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    metadata.create_all(engine)
    await database.connect()

    # Schedule the background cleanup job to run every hour
    scheduler.add_job(cleanup_expired_urls, 'interval', hours=1)
    scheduler.start()

    # Yield control back to FastAPI to run the app
    yield

    # Shutdown event
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
