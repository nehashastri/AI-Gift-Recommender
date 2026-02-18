import logging
import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Load environment variables from .env file
load_dotenv()

from lib.recommender import GiftRecommender
from lib.types import GiftWizardState


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


@app.on_event("startup")
async def startup_event():
    """Log on application startup"""
    logger.info("[STARTUP] Gift Genius API starting up...")
    logger.info("[STARTUP] Logging is now active")


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
