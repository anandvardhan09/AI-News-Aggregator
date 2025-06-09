# backend/app/services/database.py - Fix the global client issue
from motor.motor_asyncio import AsyncIOMotorClient
import os

class Database:
    def __init__(self):
        self.client = None

db = Database()

async def get_database():
    if not db.client:
        await init_db()
    return db.client.ai_news_aggregator

async def init_db():
    if not db.client:
        db.client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
        try:
            await db.client.admin.command('ping')
            print("✅ Connected to MongoDB")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise

async def close_db():
    if db.client:
        db.client.close()