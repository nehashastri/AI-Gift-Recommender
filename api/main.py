import logging
import os
import sys
from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from lib.database import Database
from lib.recommender import GiftRecommender
from lib.reminder_service import ReminderService
from lib.types import (
    GiftWizardState,
    Persona,
    PersonaCreateRequest,
    PersonaReminder,
    PersonaUpdateRequest,
    ReminderCheckRequest,
    UserLoginRequest,
    UserSignupRequest,
)

# Load environment variables from .env file
load_dotenv()


# ===== LOGGING SETUP =====
class FlushingStreamHandler(logging.StreamHandler):
    """Stream handler that flushes after every log"""

    def emit(self, record):
        super().emit(record)
        self.flush()


class FlushingFileHandler(logging.FileHandler):
    """File handler that flushes after every log"""

    def emit(self, record):
        super().emit(record)
        self.flush()


# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Disable uvicorn access logs
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# Remove any existing handlers and create a clean setup
root_logger = logging.getLogger()
root_logger.handlers.clear()

# Create flushing handler for console
handler = FlushingStreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
handler.setFormatter(formatter)

root_logger.addHandler(handler)

# Create file handler - new log file for each run
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"logs/gift_genius_{timestamp}.log"
file_handler = FlushingFileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    "[%(asctime)s] [%(name)s] %(levelname)s: %(message)s"
)
file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)

root_logger.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.info("=" * 60)
logger.info("Gift Genius API - Logging Initialized")
logger.info(f"Log file: {log_file}")
logger.info("=" * 60)

app = FastAPI(title="Gift Genius API", version="1.0.0")

# In-memory email inbox for demo
EMAIL_INBOX: List[dict] = []

# Database
db = Database()

# Initialize recommender
recommender = GiftRecommender()

# Initialize reminder service
reminder_service = ReminderService(recommender, EMAIL_INBOX)


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d")


def _persona_to_response(persona: Persona) -> dict:
    return {
        "id": persona.id,
        "user_id": persona.user_id,
        "name": persona.name,
        "birthday": persona.birthday.date().isoformat() if persona.birthday else None,
        "loves": persona.loves,
        "hates": persona.hates,
        "allergies": persona.allergies,
        "dietary_restrictions": persona.dietary_restrictions,
        "description": persona.description,
        "email_reminders": persona.email_reminders,
        "created_at": persona.created_at.isoformat(),
        "updated_at": persona.updated_at.isoformat(),
    }


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _hash_password(password: str) -> str:
    import hashlib

    # Simple hash for demo purposes; replace with a proper password hasher in production.
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@app.on_event("startup")
async def startup_event():
    """Log on application startup"""
    logger.info("[STARTUP] Gift Genius API starting up...")
    logger.info("[STARTUP] Logging is now active")
    try:
        personas = db.get_all_personas()
        reminders = [
            PersonaReminder(
                name=p.name,
                birthday=p.birthday.date().isoformat() if p.birthday else None,
                email_reminders=p.email_reminders,
                user_email=p.user_id,
                loves=p.loves,
                hates=p.hates,
                allergies=p.allergies,
                dietary_restrictions=p.dietary_restrictions,
                description=p.description,
            )
            for p in personas
        ]
        sent = reminder_service.send_birthday_reminders(reminders)
        logger.info("[STARTUP] Reminder check sent %s emails", len(sent))
    except Exception as exc:
        logger.warning("[STARTUP] Reminder check failed: %s", exc)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/api/recommendations")
def get_recommendations(state: GiftWizardState):
    """
    Get gift recommendations based on user preferences.

    Takes a GiftWizardState with user input and returns 3 product recommendations.
    """
    logger.info("\n" + "=" * 60)
    logger.info(">>> NEW RECOMMENDATION REQUEST RECEIVED <<<")
    logger.info("=" * 60)

    try:
        logger.info(f"Request occasion: {state.occasion}")
        logger.info(f"Request recipient: {state.recipient_name}")
        logger.info(f"Request loves: {state.recipient_loves}")
        logger.info(f"Request hates: {state.recipient_hates}")
        logger.info(f"Request allergies: {state.recipient_allergies}")

        logger.info("Calling recommender.get_recommendations()...")
        recommendations = recommender.get_recommendations(state)

        logger.info("[SUCCESS] Recommendations generated successfully!")
        logger.info(f"Best match: {recommendations.best_match.product.name}")
        logger.info(f"Safe bet: {recommendations.safe_bet.product.name}")
        if recommendations.unique:
            logger.info(f"Unique: {recommendations.unique.product.name}")

        return {
            "success": True,
            "data": {
                "best_match": recommendations.best_match.dict(),
                "safe_bet": recommendations.safe_bet.dict(),
                "unique": recommendations.unique.dict()
                if recommendations.unique
                else None,
            },
        }
    except Exception as e:
        logger.error(f"[ERROR] in get_recommendations: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=400, detail=str(e))


# Serve static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # Directory doesn't exist yet, will be created
    pass


@app.get("/")
def serve_index():
    """Serve the main index page"""
    return FileResponse("static/index.html", media_type="text/html")


@app.post("/api/reminders/check")
def check_reminders(payload: ReminderCheckRequest):
    """Check for birthdays happening tomorrow and send reminder emails."""
    personas = payload.personas
    if personas is None:
        if payload.user_email:
            db_personas = db.get_user_personas(user_id=payload.user_email)
        else:
            db_personas = db.get_all_personas()

        personas = [
            PersonaReminder(
                name=p.name,
                birthday=p.birthday.date().isoformat() if p.birthday else None,
                email_reminders=p.email_reminders,
                user_email=p.user_id,
                loves=p.loves,
                hates=p.hates,
                allergies=p.allergies,
                dietary_restrictions=p.dietary_restrictions,
                description=p.description,
            )
            for p in db_personas
        ]

    sent = reminder_service.send_birthday_reminders(personas, payload.user_email)
    return {"sent": sent, "count": len(sent)}


@app.get("/api/inbox")
def get_inbox(user_email: Optional[str] = None):
    """Return demo inbox messages."""
    if user_email:
        filtered = [m for m in EMAIL_INBOX if m.get("to") == user_email]
        return {"messages": filtered}
    return {"messages": EMAIL_INBOX}


@app.post("/api/login")
def login(payload: UserLoginRequest):
    """Simple demo login that returns a user_id derived from email."""
    email = _normalize_email(payload.email)
    user = db.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")

    return {"user_id": email, "full_name": user.full_name, "email": email}


@app.post("/api/signup")
def signup(payload: UserSignupRequest):
    """Create a new account."""
    email = _normalize_email(payload.email)
    existing = db.get_user_by_email(email)
    if existing:
        raise HTTPException(status_code=409, detail="Account already exists")

    user = db.create_user(
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=_hash_password(payload.password),
    )
    return {"user_id": email, "full_name": user.full_name, "email": email}


@app.get("/api/personas")
def get_personas(user_id: str):
    personas = db.get_user_personas(user_id=user_id)
    return {"personas": [_persona_to_response(p) for p in personas]}


@app.post("/api/personas")
def create_persona(payload: PersonaCreateRequest):
    persona = Persona(
        user_id=payload.user_id,
        name=payload.name,
        birthday=_parse_date(payload.birthday),
        loves=payload.loves,
        hates=payload.hates,
        allergies=payload.allergies,
        dietary_restrictions=payload.dietary_restrictions,
        description=payload.description,
        email_reminders=payload.email_reminders,
    )
    persona_id = db.create_persona(persona)
    created = db.get_persona(persona_id)
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create persona")
    return {"persona": _persona_to_response(created)}


@app.put("/api/personas/{persona_id}")
def update_persona(persona_id: str, payload: PersonaUpdateRequest):
    updates = payload.dict(exclude_unset=True)
    if "birthday" in updates:
        updates["birthday"] = _parse_date(updates.get("birthday"))

    ok = db.update_persona(persona_id, updates)
    if not ok:
        raise HTTPException(status_code=404, detail="Persona not found")

    persona = db.get_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return {"persona": _persona_to_response(persona)}


@app.delete("/api/personas/{persona_id}")
def delete_persona(persona_id: str):
    ok = db.delete_persona(persona_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Persona not found")
    return {"deleted": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
