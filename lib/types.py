# Define all pydantic models here

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class Product(BaseModel):
    """Product from Edible API"""

    id: str
    name: str
    description: str
    price: float
    image_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    category: Optional[str] = None
    raw_data: Optional[Dict] = None


class ProductAttributes(BaseModel):
    """Structured attributes extracted by AI"""

    product_id: str
    ingredients: List[str] = Field(default_factory=list)
    chocolate_type: Optional[Literal["dark", "milk", "white"]] = None
    contains_nuts: bool = False
    fruit_types: List[str] = Field(default_factory=list)
    dietary_labels: List[str] = Field(default_factory=list)  # vegan, gluten-free, etc.
    category: Literal[
        "chocolate_dipped", "fresh_fruit", "baked_goods", "mixed", "other"
    ] = "other"


# ===== PERSONA TYPES =====
# Permanent (until deleted), stored in database.


class Persona(BaseModel):
    """Recipient profile saved by user"""

    id: Optional[str] = None
    user_id: str
    name: str
    birthday: Optional[datetime] = None
    loves: List[str] = Field(default_factory=list)
    hates: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)
    description: Optional[str] = None  # Free-form text
    email_reminders: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ===== WIZARD STATE =====
# One shopping session
class GiftWizardState(BaseModel):
    """State for the gift discovery wizard"""

    # Step 1: Basics
    recipient_name: Optional[str] = None
    occasion: str
    budget: Optional[float] = None
    delivery_date: datetime

    # Step 2: Preferences (recipient's preferences)
    recipient_loves: List[str] = Field(default_factory=list)
    recipient_hates: List[str] = Field(default_factory=list)
    recipient_allergies: List[str] = Field(default_factory=list)
    recipient_dietary: List[str] = Field(default_factory=list)
    unknown_preferences: bool = False

    # Step 3: Description
    recipient_description: Optional[str] = None

    # Internal state
    current_step: int = 1
    persona_id: Optional[str] = None  # If shopping for saved persona


# ===== RECOMMENDATION TYPES =====


class ProductScore(BaseModel):
    """Scores for a single product"""

    product: Product
    best_match_score: float = 0
    safe_bet_score: float = 0
    unique_score: float = 0
    score_breakdown: List[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    """Final recommendation with explanation"""

    product: Product
    attributes: Optional[ProductAttributes] = None
    score: float
    category: Literal["best_match", "safe_bet", "unique"]
    explanation: str
    score_breakdown: List[str] = Field(default_factory=list)


class ThreePickRecommendations(BaseModel):
    """The three final picks"""

    best_match: Recommendation
    safe_bet: Recommendation
    unique: Optional[Recommendation] = None


# ===== AI TYPES =====


class SafetyValidation(BaseModel):
    """AI safety check result for a product"""

    product_id: str
    reject: bool
    reason: Optional[str] = None


class SafetyValidationResponse(BaseModel):
    """Batch safety validation response"""

    validations: List[SafetyValidation]
