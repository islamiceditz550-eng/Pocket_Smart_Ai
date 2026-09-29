from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

PlannerType = Literal["home", "party", "jewelry"]

class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: str
    password: str

class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=100_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    rooms: list[str] = Field(default_factory=lambda: ["Living Room"], min_length=1, max_length=8)
    style: str = Field(default="Modern", max_length=100)
    priorities: str = Field(default="Value for money", max_length=500)
    quantities: dict[str, int] = Field(default_factory=dict)

class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=100_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    guests: int = Field(gt=0, le=100_000)
    event_type: str = Field(default="Birthday", max_length=100)
    venue: str = Field(default="Flexible", max_length=300)
    food_preference: str = Field(default="Mixed", max_length=100)
    priorities: str = Field(default="Good experience within budget", max_length=500)

class RecommendationItem(BaseModel):
    name: str
    category: str
    estimated_price: float = Field(ge=0)
    reason: str
    platform: str
    search_url: str

class RecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    planner_type: PlannerType
    title: str
    summary: str
    budget: float
    currency: str
    budget_breakdown: dict[str, float]
    items: list[RecommendationItem]
    tips: list[str]
    disclaimer: str
    source_mode: Literal["gemini", "fallback"]

class JewelryResponse(RecommendationResponse):
    image_analysis: str | None = None
