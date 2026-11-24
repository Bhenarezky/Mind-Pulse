import logging
from fastapi import APIRouter, HTTPException
from app.schemas.classify_schema import JournalRequest

from app.services.classification_service import (
    classify_journal
)

from app.services.translation_service import (
    TranslationError
)

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/classify")
def classify(request: JournalRequest):
    try:

        result = classify_journal(
            request.content
        )

        return result

    except TranslationError as e:
        logger.error(
            f"Translation failed: {e}"
        )

        raise HTTPException(
            status_code=503,
            detail={
                "error": "TRANSLATION_FAILED",
                "message": str(e)
            }
        )

    except Exception:
        logger.exception(
            "Classification failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "CLASSIFICATION_FAILED",
                "message": "An error occurred during classification."
            }
        )