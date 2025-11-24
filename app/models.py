from pydantic import BaseModel, Field
from typing import List, Optional

# ============= SUMMARIZE =============
class SummarizeRequest(BaseModel):
    content: str

class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int

# ============= RECOMMEND =============
class RecommendRequest(BaseModel):
    preferences: List[str]
    userId: Optional[str] = None
    limit: Optional[int] = 20

class ArticleResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    image: Optional[str] = None
    publishedAt: Optional[str] = None
    lang: Optional[str] = None
    sourceId: Optional[str] = None
    sourceName: Optional[str] = None
    sourceUrl: Optional[str] = None
    sourceCountry: Optional[str] = None
    score: float

class RecommendResponse(BaseModel):
    articles: List[ArticleResponse]
    total: int
    userId: Optional[str] = None