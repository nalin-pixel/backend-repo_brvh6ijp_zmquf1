"""
Database Schemas for Meme Generator Marketplace

Each Pydantic model represents a MongoDB collection. The collection name
is the lowercase of the class name (e.g., Project -> "project").
"""
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl

class Project(BaseModel):
    name: str = Field(..., description="Project display name")
    description: Optional[str] = Field(None, description="What this crypto project is about")
    token_symbol: str = Field(..., description="Token symbol (e.g., ETH, SOL)")
    logo_url: Optional[HttpUrl] = Field(None, description="Logo image URL")

class Meme(BaseModel):
    project_id: str = Field(..., description="Associated project id as string")
    title: str = Field(..., description="Short title for the meme")
    image_url: HttpUrl = Field(..., description="Direct link to the generated meme image")
    top_text: Optional[str] = Field(None, description="Top caption text")
    bottom_text: Optional[str] = Field(None, description="Bottom caption text")
    creator_name: Optional[str] = Field(None, description="Display name of creator")
    creator_wallet: Optional[str] = Field(None, description="Creator wallet address for rewards")
    upvotes: int = Field(0, ge=0, description="Number of upvotes")
    tokens_earned: int = Field(0, ge=0, description="Simple counter for demo rewards")

class User(BaseModel):
    name: str
    wallet: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    bio: Optional[str] = None
