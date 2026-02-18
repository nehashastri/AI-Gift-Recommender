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

# Load environment variables from .env file
load_dotenv()

from pydantic import BaseModel, Field

from lib.database import Database
from lib.email_service import EmailService
from lib.recommender import GiftRecommender
from lib.types import GiftWizardState, Persona


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

# Email sender
email_service = EmailService()

# Database
db = Database()


class PersonaReminder(BaseModel):
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
    user_email: Optional[str] = None
    personas: Optional[List[PersonaReminder]] = None


class UserLoginRequest(BaseModel):
    email: str


class UserSignupRequest(BaseModel):
    full_name: str
    email: str
    password: str


class PersonaCreateRequest(BaseModel):
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
    name: Optional[str] = None
    birthday: Optional[str] = None
    loves: Optional[List[str]] = None
    hates: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    description: Optional[str] = None
    email_reminders: Optional[bool] = None


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


def _format_suggestions(persona: PersonaReminder) -> List[dict]:
    try:
        wizard_state = GiftWizardState(
            occasion="Birthday",
            delivery_date=None,
            recipient_name=persona.name,
            recipient_loves=persona.loves or [],
            recipient_hates=persona.hates or [],
            recipient_allergies=persona.allergies or [],
            recipient_dietary=persona.dietary_restrictions or [],
            recipient_description=persona.description or None,
        )
        recommendations = recommender.get_recommendations(wizard_state)
        picks = [
            ("Best Match", recommendations.best_match),
            ("Safe Bet", recommendations.safe_bet),
            ("Something Unique", recommendations.unique),
        ]
        suggestions = []
        for label, rec in picks:
            if rec is None:
                continue
            product = rec.product
            suggestions.append(
                {
                    "label": label,
                    "name": product.name,
                    "price": f"${product.price:.2f}",
                    "description": product.description or "",
                    "image_url": product.image_url or product.thumbnail_url or "",
                }
            )
        return suggestions[:3]
    except Exception as exc:
        logger.warning(
            "[REMINDER] Suggestion build failed for %s: %s", persona.name, exc
        )
        return []


def _build_email_html(
    persona: PersonaReminder,
    when_text: str,
    suggestions: List[dict],
) -> str:
    last_gift_line = (
        f'<p style="margin: 0 0 12px; color: #555;">Last gift picked: {persona.last_gift}</p>'
        if persona.last_gift
        else ""
    )
    cards_html = ""
    for suggestion in suggestions:
        image_html = (
            f'<img src="{suggestion["image_url"]}" alt="{suggestion["name"]}" '
            'style="display: block; width: 100%; height: 140px; object-fit: cover;">'
            if suggestion["image_url"]
            else '<div style="height: 140px; background: #f5f5f5; display: flex; align-items: center; justify-content: center; font-size: 32px;">🎁</div>'
        )
        cards_html += f"""
        <table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" style=\"border: 1px solid #e6e6e6; border-radius: 10px; overflow: hidden; margin-bottom: 16px;\">
            <tr>
                <td>{image_html}</td>
            </tr>
            <tr>
                <td style=\"padding: 16px;\">
                    <span style=\"display: inline-block; background: #d4403b; color: #ffffff; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;\">{suggestion["label"]}</span>
                    <h3 style=\"margin: 10px 0 4px; font-size: 16px; color: #333;\">{suggestion["name"]}</h3>
                    <p style=\"margin: 0 0 8px; color: #d4403b; font-weight: 700;\">{suggestion["price"]}</p>
                    <p style=\"margin: 0; color: #555; font-size: 13px; line-height: 1.4;\">{suggestion["description"]}</p>
                    <div style=\"margin-top: 12px;\">
                        <a href=\"#\" style=\"display: inline-block; padding: 8px 12px; background: #f5f5f5; color: #333; text-decoration: none; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px; font-weight: 600;\">View Product</a>
                    </div>
                </td>
            </tr>
        </table>
        """

    suggestions_block = (
        f"""
        <p style=\"margin: 0 0 12px; color: #555;\">Here are a few gift ideas:</p>
        {cards_html}
        """
        if suggestions
        else ""
    )

    return f"""
    <div style=\"background: #f6f6f6; padding: 24px; font-family: Arial, Helvetica, sans-serif;\">
        <div style=\"max-width: 560px; margin: 0 auto; background: #ffffff; border: 1px solid #e6e6e6; border-radius: 12px; overflow: hidden;\">
            <div style=\"background: #d4403b; color: #ffffff; padding: 20px 24px;\">
                <h1 style=\"margin: 0; font-size: 20px;\">Gift Genius Reminder</h1>
                <p style=\"margin: 8px 0 0; font-size: 14px; opacity: 0.9;\">Birthday coming up {when_text}</p>
            </div>
            <div style=\"padding: 24px;\">
                <p style=\"margin: 0 0 12px; color: #333; font-size: 16px;\">Hi there,</p>
                <p style=\"margin: 0 0 12px; color: #555;\">Reminder: {persona.name}'s birthday is {when_text}.</p>
                {last_gift_line}
                {suggestions_block}
                <div style=\"margin-top: 20px;\">
                    <a href=\"#\" style=\"display: inline-block; padding: 10px 16px; background: #d4403b; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: 600;\">View More Gift Ideas</a>
                </div>
            </div>
            <div style=\"padding: 16px 24px; background: #fafafa; color: #888; font-size: 12px;\">
                You are receiving this reminder because email reminders are enabled in Gift Genius.
            </div>
        </div>
    </div>
    """


def _send_birthday_reminders(
    personas: List[PersonaReminder],
    user_email: Optional[str] = None,
) -> List[dict]:
    today = datetime.now().date()
    sent = []

    for persona in personas:
        if not persona.email_reminders or not persona.birthday:
            continue

        try:
            birthday_date = datetime.strptime(persona.birthday, "%Y-%m-%d").date()
        except ValueError:
            logger.warning("[REMINDER] Invalid birthday format for %s", persona.name)
            continue

        next_birthday = birthday_date.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)

        days_until = (next_birthday - today).days
        if days_until < 0 or days_until > 10:
            continue

        when_text = "today" if days_until == 0 else f"in {days_until} days"
        subject = f"Gift reminder: {persona.name}'s birthday is {when_text}"
        body_lines = [
            "Hi there,",
            "",
            f"Reminder: {persona.name}'s birthday is {when_text}.",
            "",
        ]
        if persona.last_gift:
            body_lines.append(f"Last gift picked: {persona.last_gift}")
            body_lines.append("")

        suggestions = _format_suggestions(persona)
        if suggestions:
            body_lines.append("Here are a few gift ideas:")
            for suggestion in suggestions:
                body_lines.append(
                    f"- {suggestion['label']}: {suggestion['name']} ({suggestion['price']})"
                )
            body_lines.append("")

        body_lines.append("Open Gift Genius to see more gift suggestions.")
        body = "\n".join(body_lines)

        recipient = persona.user_email or user_email
        html_body = _build_email_html(persona, when_text, suggestions)
        ok, status = email_service.send_email(subject, body, recipient, html_body)

        message = {
            "to": recipient or os.getenv("EMAIL_TO"),
            "subject": subject,
            "body": body,
            "body_html": html_body,
            "sent_at": datetime.now().isoformat(),
            "status": status,
        }
        EMAIL_INBOX.append(message)
        if ok:
            sent.append({"name": persona.name, "status": status})

    return sent


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
        sent = _send_birthday_reminders(reminders)
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

# Initialize recommender
recommender = GiftRecommender()


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

    sent = _send_birthday_reminders(personas, payload.user_email)
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
