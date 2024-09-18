from sqlalchemy import create_engine, MetaData
from databases import Database
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# PostgreSQL connection string from environment variables
DATABASE_URL = "postgresql://shrinit:Simba1805@offerlicious.postgres.database.azure.com/postgres"

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Create an async Database instance
database = Database(DATABASE_URL)