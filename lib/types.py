from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

# ===== PRODUCT TYPES =====


class Product(BaseModel):
    """Product from Edible API"""

    id: str
    name: str
    description: str
    meta_description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    ingredients: Optional[str] = None
    popularity_rank: Optional[int] = None
    occasions: List[str] = Field(
        default_factory=list
    )  # Occasion tags from API: ["Anniversary", "Birthday", "Wedding"]


class ProductAttributes(BaseModel):
    """
    Structured attributes extracted by AI from product details
    AI analyzes: name, description, meta_description, ingredients
    """

    product_id: str

    # Chocolate analysis
    has_chocolate: bool = False
    chocolate_types: List[str] = Field(
        default_factory=list
    )  # ["dark", "milk", "white"]

    # Fruit analysis
    fruits: List[str] = Field(
        default_factory=list
    )  # ["strawberry", "pineapple", "grape"]

    # Other ingredients
    has_nuts: bool = False
    nut_types: List[str] = Field(default_factory=list)  # ["almond", "peanut", "cashew"]
    has_caramel: bool = False
    has_cookies: bool = False
    has_brownies: bool = False

    # Dietary
    is_sugar_free: bool = False
    is_vegan: bool = False
    is_gluten_free: bool = False

    # Category
    product_type: str = (
        "mixed"  # "chocolate_dipped", "fresh_fruit", "baked_goods", "mixed"
    )


# ===== PERSONA TYPES =====


class Persona(BaseModel):
    """Recipient profile saved by user"""

    id: Optional[str] = None
    user_id: str = "default_user"
    name: str
    birthday: Optional[datetime] = None
    loves: List[str] = Field(default_factory=list)
    hates: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    email_reminders: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ===== WIZARD STATE =====


class GiftWizardState(BaseModel):
    """State for the gift discovery wizard"""

    # Step 1: Basics
    recipient_name: Optional[str] = None
    occasion: str
    budget: Optional[str] = None  # Kept for backward compatibility
    budget_max: Optional[float] = None  # Structured budget - max price
    budget_min: Optional[float] = None  # Structured budget - min price
    delivery_date: Optional[datetime]

    # Step 2: Preferences (recipient's preferences)
    recipient_loves: Annotated[List[str], Field(max_length=3)] = Field(
        default_factory=list
    )
    recipient_hates: Optional[List[str]] = Field(default_factory=list)
    recipient_allergies: Optional[List[str]] = Field(default_factory=list)
    recipient_dietary: Optional[List[str]] = Field(default_factory=list)

    # Step 3: Description
    recipient_description: Optional[str] = None

    # Internal state
    current_step: int = 1
    persona_id: Optional[str] = None


# ===== RECOMMENDATION TYPES =====


class ProductScore(BaseModel):
    """Scores for a single product"""

    product: Product
    attributes: Optional[ProductAttributes] = None
    best_match_score: float = 0
    safe_bet_score: float = 0
    unique_score: float = 0
    score_breakdown: List[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    """Final recommendation with explanation"""

    product: Product
    attributes: Optional[ProductAttributes] = None
    score: float
    category: str  # "best_match", "safe_bet", "unique"
    explanation: str
    score_breakdown: List[str] = Field(default_factory=list)


class ThreePickRecommendations(BaseModel):
    """The three final picks"""

    best_match: Recommendation
    safe_bet: Recommendation
    unique: Optional[Recommendation] = None


# ===== AI SAFETY TYPES =====


class SafetyValidation(BaseModel):
    """AI safety check result for a single product"""

    product_id: str
    reject: bool
    reason: Optional[str] = None


class SafetyValidationResponse(BaseModel):
    """Batch safety validation response from AI"""

    validations: List[SafetyValidation]


# ===== ATTRIBUTE EXTRACTION TYPES =====


class AttributeExtractionResponse(BaseModel):
    """
    Response from AI when extracting product attributes
    AI analyzes: name, description, meta_description, ingredients
    """

    attributes: List[ProductAttributes]


# ===== API REQUEST/RESPONSE TYPES =====


class PersonaReminder(BaseModel):
    """Persona data for reminder checks"""

    name: str
    birthday: Optional[str] = None  # YYYY-MM-DD
    email_reminders: bool = True
    last_gift: Optional[str] = None
    user_email: Optional[str] = None
    loves: Optional[List[str]] = None
    hates: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    description: Optional[str] = None


class ReminderCheckRequest(BaseModel):
    """Request to check for upcoming birthdays and send reminders"""

    user_email: Optional[str] = None
    personas: Optional[List[PersonaReminder]] = None


class UserLoginRequest(BaseModel):
    """User login request"""

    email: str


class UserSignupRequest(BaseModel):
    """User signup request"""

    full_name: str
    email: str
    password: str


class PersonaCreateRequest(BaseModel):
    """Request to create a new persona"""

    user_id: str
    name: str
    birthday: Optional[str] = None
    loves: List[str] = Field(default_factory=list)
    hates: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    email_reminders: bool = True


class PersonaUpdateRequest(BaseModel):
    """Request to update an existing persona"""

    name: Optional[str] = None
    birthday: Optional[str] = None
    loves: Optional[List[str]] = None
    hates: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    description: Optional[str] = None
    email_reminders: Optional[bool] = None
