from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.models import (
    SummarizeRequest, SummarizeResponse,
    RecommendRequest, RecommendResponse, ArticleResponse
)
from app.services.summarization import summarization_service
from app.services.recommendation import recommendation_service
from datetime import datetime

app = FastAPI(
    title="AI News ML Service",
    description="Text Summarization & Article Recommendation API",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lifecycle Events
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    print("🚀 FastAPI ML Service Started")

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
    print("🛑 FastAPI ML Service Stopped")

# ============= ROOT =============
@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "AI News ML Service",
        "version": "1.0.0",
        "endpoints": {
            "summarize": "POST /summarize",
            "recommend": "POST /recommend",
            "health": "GET /health"
        }
    }

# ============= HEALTH CHECK =============
@app.get("/health")
async def health_check(db=Depends(get_database)):
    try:
        # Ping MongoDB
        await db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# ============= SUMMARIZE =============
@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    """
    Summarize article content using BART model
    
    Input:
    - content: Full article text
    
    Output:
    - summary: Condensed summary
    - original_length: Word count of original
    - summary_length: Word count of summary
    """
    try:
        content = request.content.strip()
        
        if not content:
            raise HTTPException(
                status_code=400, 
                detail="Content cannot be empty"
            )
        
        # Generate summary
        result = summarization_service.summarize(content)
        
        return SummarizeResponse(
            summary=result['summary'],
            original_length=result['original_length'],
            summary_length=result['summary_length']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Summarization endpoint error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Summarization failed: {str(e)}"
        )

# ============= RECOMMEND =============
@app.post("/recommend", response_model=RecommendResponse)
async def recommend(
    request: RecommendRequest,
    db=Depends(get_database)
):
    """
    Recommend articles based on user preferences and interactions
    
    Input:
    - preferences: List of topics/keywords
    - userId: (Optional) User ID for personalization
    
    Output:
    - articles: Ranked list of articles with scores
    - total: Number of recommendations
    """
    try:
        preferences = request.preferences
        user_id = request.userId
        
        # Validate preferences
        if not preferences or len(preferences) == 0:
            raise HTTPException(
                status_code=400, 
                detail="Preferences cannot be empty"
            )
        
        # Fetch all articles from MongoDB
        articles_cursor = db.news.find({})
        articles_list = await articles_cursor.to_list(length=2000)
        
        if not articles_list:
            return RecommendResponse(
                articles=[], 
                total=0,
                userId=user_id
            )
        
        # Convert MongoDB documents to dict
        articles = []
        for doc in articles_list:
            # Handle publishedAt conversion
            published_at = doc.get('publishedAt')
            if published_at:
                if hasattr(published_at, 'isoformat'):
                    published_at = published_at.isoformat()
                else:
                    published_at = str(published_at)
            
            article = {
                'id': str(doc.get('_id')),
                'title': doc.get('title', ''),
                'description': doc.get('description'),
                'content': doc.get('content'),
                'url': doc.get('url'),
                'image': doc.get('image'),
                'publishedAt': published_at,
                'lang': doc.get('lang'),
                'sourceId': doc.get('sourceId'),
                'sourceName': doc.get('sourceName'),
                'sourceUrl': doc.get('sourceUrl'),
                'sourceCountry': doc.get('sourceCountry')
            }
            articles.append(article)
        
        # Fetch user events if userId provided
        user_events = []
        if user_id:
            events_cursor = db.user_events.find({"userId": user_id})
            user_events = await events_cursor.to_list(length=None)
        
        # Get recommendations
        recommendations = await recommendation_service.recommend_articles(
            preferences=preferences,
            articles=articles,
            user_events=user_events,
            top_k=request.limit  # ← dynamic from request
        )
        
        # Convert to response model
        article_objects = [
            ArticleResponse(
                id=rec['id'],
                title=rec['title'],
                description=rec.get('description'),
                content=rec.get('content'),
                url=rec.get('url'),
                image=rec.get('image'),
                publishedAt=rec.get('publishedAt'),
                lang=rec.get('lang'),
                sourceId=rec.get('sourceId'),
                sourceName=rec.get('sourceName'),
                sourceUrl=rec.get('sourceUrl'),
                sourceCountry=rec.get('sourceCountry'),
                score=rec['score']
            )
            for rec in recommendations
        ]
        
        return RecommendResponse(
            articles=article_objects,
            total=len(article_objects),
            userId=user_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Recommendation endpoint error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Recommendation failed: {str(e)}"
        )