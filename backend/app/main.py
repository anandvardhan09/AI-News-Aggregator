from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.routes import articles
from app.services.database import init_db

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print("✅ Database initialized")
    
    # Verify Hugging Face token
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    if not hf_token:
        print("⚠️  Warning: HUGGINGFACE_TOKEN not set. AI features may not work.")
    else:
        print("✅ Hugging Face token configured")
    
    yield
    # Shutdown
    print("🔄 Application shutting down")

app = FastAPI(
    title="AI News Aggregator API",
    description="Intelligent news aggregation with AI summarization and credibility analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])

@app.get("/")
async def root():
    return {
        "message": "AI News Aggregator API is running!",
        "version": "1.0.0",
        "ai_provider": "Hugging Face (Free)"
    }

@app.get("/api/health")
async def health_check():
    try:
        db = await get_database()
        await db.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))