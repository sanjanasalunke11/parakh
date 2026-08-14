import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..core.ocr import extract_text_from_image
from ..core.pipeline import run_verification_pipeline
from ..core.url_extraction import extract_article_text
from ..database import get_db
from ..models import InputType
from ..schemas import ClaimResult, TextVerifyRequest, UrlVerifyRequest, VoiceVerifyRequest

logger = logging.getLogger("parakh.routers.verify")
router = APIRouter(prefix="/api/verify", tags=["verify"])

MAX_IMAGE_BYTES = 8 * 1024 * 1024


@router.post("/text", response_model=ClaimResult)
def verify_text(payload: TextVerifyRequest, db: Session = Depends(get_db)):
    try:
        return run_verification_pipeline(db, payload.text, InputType.TEXT)
    except Exception as exc:
        logger.exception("Text verification failed")
        raise HTTPException(status_code=502, detail=f"Verification failed: {exc}") from exc


@router.post("/voice", response_model=ClaimResult)
def verify_voice(payload: VoiceVerifyRequest, db: Session = Depends(get_db)):
    try:
        return run_verification_pipeline(db, payload.text, InputType.VOICE)
    except Exception as exc:
        logger.exception("Voice verification failed")
        raise HTTPException(status_code=502, detail=f"Verification failed: {exc}") from exc


@router.post("/image", response_model=ClaimResult)
async def verify_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    if len(contents) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image too large (max 8MB).")

    try:
        extracted_text = extract_text_from_image(contents)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if not extracted_text or len(extracted_text.strip()) < 5:
        raise HTTPException(
            status_code=422,
            detail="No readable text was found in this image. Try a clearer screenshot.",
        )

    try:
        return run_verification_pipeline(db, extracted_text, InputType.IMAGE)
    except Exception as exc:
        logger.exception("Image verification failed")
        raise HTTPException(status_code=502, detail=f"Verification failed: {exc}") from exc


@router.post("/url", response_model=ClaimResult)
def verify_url(payload: UrlVerifyRequest, db: Session = Depends(get_db)):
    try:
        article_text = extract_article_text(payload.url)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if not article_text or len(article_text.strip()) < 20:
        raise HTTPException(
            status_code=422,
            detail="Could not extract readable article content from this URL.",
        )

    try:
        return run_verification_pipeline(db, article_text, InputType.URL, source_url=payload.url)
    except Exception as exc:
        logger.exception("URL verification failed")
        raise HTTPException(status_code=502, detail=f"Verification failed: {exc}") from exc
