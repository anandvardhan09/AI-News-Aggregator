from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class Article(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    content: str
    url: str
    source: str
    published_date: datetime
    summary: Optional[str] = None
    credibility_score: Optional[float] = None
    category: Optional[str] = None
    tags: List[str] = []
    image_url: Optional[str] = None
    author: Optional[str] = None
    
    def to_dict(self):
        return {
            "_id": str(self.id),
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "source": self.source,
            "published_date": self.published_date,
            "summary": self.summary,
            "credibility_score": self.credibility_score,
            "category": self.category,
            "tags": self.tags,
            "image_url": self.image_url,
            "author": self.author
        }

class ArticleResponse(BaseModel):
    id: str
    title: str
    content: str
    url: str
    source: str
    published_date: datetime
    summary: Optional[str] = None
    credibility_score: Optional[float] = None
    category: Optional[str] = None
    tags: List[str] = []
    image_url: Optional[str] = None
    author: Optional[str] = None

class ArticleCreate(BaseModel):
    title: str
    content: str
    url: str
    source: str
    published_date: Optional[datetime] = None
    category: Optional[str] = None
    tags: List[str] = []
    image_url: Optional[str] = None
    author: Optional[str] = None