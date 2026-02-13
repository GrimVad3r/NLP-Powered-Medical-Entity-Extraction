"""Pydantic schemas for API requests/responses."""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
class ChannelSchema(BaseModel):
"""Channel schema."""
id: Optional[int] = None
name: str
description: Optional[str] = None
member_count: int = 0
class Config:
    from_attributes = True
class MessageSchema(BaseModel):
"""Message schema."""
id: Optional[int] = None
text: str
date: datetime
views: int = 0
is_medical: bool = False
quality_score: float = 0.0
class Config:
    from_attributes = True
class EntitySchema(BaseModel):
"""Entity schema."""
id: Optional[int] = None
text: str
entity_type: str
confidence: float
normalized: Optional[str] = None
class Config:
    from_attributes = True
class ProductSchema(BaseModel):
"""Product schema."""
id: Optional[int] = None
name: str
category: str
mention_count: int = 0
avg_price: Optional[float] = None
class Config:
    from_attributes = True