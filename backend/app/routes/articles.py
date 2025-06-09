from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio

from app.models.article import Article, ArticleResponse, ArticleCreate
from app.services.database import get_database
from app.services.ai_services import AIService
from app.services.news_fetcher import NewsAggregator

router = APIRouter()

# Initialize services
ai_service = AIService()
news_aggregator = NewsAggregator()

@router.get("/", response_model=List[ArticleResponse])
async def get_articles(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    source: Optional[str] = None
):
    """Get articles with optional filtering"""
    try:
        db = await get_database()
        collection = db.articles
        
        # Build query
        query = {}
        if category:
            query["category"] = category
        if source:
            query["source"] = source
        
        # Get articles
        cursor = collection.find(query).skip(skip).limit(limit).sort("published_date", -1)
        articles = await cursor.to_list(length=limit)
        
        # Convert to response format
        response_articles = []
        for article in articles:
            response_articles.append(ArticleResponse(
                id=str(article["_id"]),
                title=article["title"],
                content=article["content"],
                url=article["url"],
                source=article["source"],
                published_date=article["published_date"],
                summary=article.get("summary"),
                credibility_score=article.get("credibility_score"),
                category=article.get("category"),
                tags=article.get("tags", []),
                image_url=article.get("image_url"),
                author=article.get("author")
            ))
        
        return response_articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching articles: {str(e)}")

@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: str):
    """Get a single article by ID"""
    try:
        from bson import ObjectId
        db = await get_database()
        collection = db.articles
        
        article = await collection.find_one({"_id": ObjectId(article_id)})
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return ArticleResponse(
            id=str(article["_id"]),
            title=article["title"],
            content=article["content"],
            url=article["url"],
            source=article["source"],
            published_date=article["published_date"],
            summary=article.get("summary"),
            credibility_score=article.get("credibility_score"),
            category=article.get("category"),
            tags=article.get("tags", []),
            image_url=article.get("image_url"),
            author=article.get("author")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching article: {str(e)}")

@router.post("/fetch", response_model=dict)
async def fetch_articles(background_tasks: BackgroundTasks):
    """Fetch and process new articles"""
    try:
        # Start background task for fetching articles
        background_tasks.add_task(fetch_and_process_articles)
        
        return {
            "message": "Article fetching started in background",
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting article fetch: {str(e)}")

async def fetch_and_process_articles():
    """Background task to fetch and process articles"""
    try:
        print("🔄 Starting article fetch...")
        
        # Fetch articles from news sources
        raw_articles = await news_aggregator.fetch_all_sources()
        
        db = await get_database()
        collection = db.articles
        
        processed_count = 0
        for article_data in raw_articles:
            try:
                # Check if article already exists
                existing = await collection.find_one({"url": article_data["url"]})
                if existing:
                    continue
                
                # Process with AI
                summary = await ai_service.summarize_text(article_data["content"])
                credibility = await ai_service.detect_fake_news(
                    article_data["title"], 
                    article_data["content"]
                )
                
                # Create article document
                article = {
                    "title": article_data["title"],
                    "content": article_data["content"],
                    "url": article_data["url"],
                    "source": article_data["source"],
                    "published_date": article_data.get("published_date", datetime.now()),
                    "summary": summary,
                    "credibility_score": credibility["score"],
                    "category": article_data.get("category"),
                    "tags": article_data.get("tags", []),
                    "image_url": article_data.get("image_url"),
                    "author": article_data.get("author"),
                }
                
                # Insert into database
                await collection.insert_one(article)
                processed_count += 1
                
                # Small delay to avoid overwhelming the AI API
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing article: {e}")
                continue
        
        print(f"✅ Processed {processed_count} new articles")
        
    except Exception as e:
        print(f"❌ Error in background article fetch: {e}")

@router.get("/stats/summary")
async def get_article_stats():
    """Get article statistics"""
    try:
        db = await get_database()
        collection = db.articles
        
        # Get total count
        total_articles = await collection.count_documents({})
        
        # Get count by source
        pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        sources = await collection.aggregate(pipeline).to_list(length=10)
        
        # Get recent articles count (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_count = await collection.count_documents({
            "published_date": {"$gte": yesterday}
        })
        
        return {
            "total_articles": total_articles,
            "recent_articles": recent_count,
            "top_sources": sources
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")
    

# backend/app/routes/articles.py - Add endpoint to trigger manual fetch
@router.post("/refresh", response_model=dict)
async def refresh_articles(background_tasks: BackgroundTasks):
    """Manually trigger article refresh"""
    background_tasks.add_task(fetch_and_process_articles)
    return {"message": "Article refresh triggered", "status": "processing"}

@router.get("/categories")
async def get_categories():
    """Get available categories"""
    try:
        db = await get_database()
        collection = db.articles
        
        categories = await collection.distinct("category")
        return {"categories": [cat for cat in categories if cat]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@router.get("/sources")
async def get_sources():
    """Get available sources"""
    try:
        db = await get_database()
        collection = db.articles
        
        sources = await collection.distinct("source")
        return {"sources": [source for source in sources if source]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sources: {str(e)}")