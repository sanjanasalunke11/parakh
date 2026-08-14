"""WhatsApp channel, via Twilio's WhatsApp Sandbox/API.

This is the proof of the architecture's central claim: it calls the exact
same run_verification_pipeline() the browser's /api/verify/* routes call.
No claim-extraction, evidence-retrieval, verification, or ledger code is
touched to add this channel.
"""

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from twilio.request_validator import RequestValidator

from ..config import settings
from ..core.ocr import extract_text_from_image
from ..core.pipeline import run_verification_pipeline
from ..core.reply_formatting import format_error_reply, format_help_reply, format_whatsapp_reply
from ..database import get_db
from ..models import InputType

logger = logging.getLogger("parakh.routers.whatsapp")
router = APIRouter(prefix="/api/webhooks", tags=["whatsapp"])


def _twiml(message: str) -> Response:
    escaped = (
        message.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escaped}</Message></Response>'
    return Response(content=xml, media_type="application/xml")


def _verify_twilio_signature(request: Request, form: dict) -> bool:
    if not settings.TWILIO_AUTH_TOKEN:
        logger.warning(
            "TWILIO_AUTH_TOKEN not set — skipping webhook signature verification. "
            "Fine for local testing, do not run this way in production."
        )
        return True

    if not settings.PUBLIC_BASE_URL:
        logger.warning(
            "PUBLIC_BASE_URL not set — cannot verify Twilio's signature (it's "
            "computed against the exact public URL Twilio called). Rejecting."
        )
        return False

    signature = request.headers.get("X-Twilio-Signature", "")
    url = settings.PUBLIC_BASE_URL.rstrip("/") + "/api/webhooks/whatsapp"
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    return validator.validate(url, form, signature)


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    form = {key: value for key, value in form_data.items()}

    if not _verify_twilio_signature(request, form):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    body_text = (form.get("Body") or "").strip()
    num_media = int(form.get("NumMedia", "0") or "0")

    try:
        if num_media > 0 and form.get("MediaUrl0"):
            text_to_verify, input_type = await _extract_from_media(form["MediaUrl0"])
        elif body_text:
            text_to_verify, input_type = body_text, InputType.TEXT
        else:
            return _twiml(format_help_reply())

        if not text_to_verify or len(text_to_verify.strip()) < 3:
            return _twiml(
                "I couldn't find readable text in that message. Try sending the "
                "claim as plain text, or a clearer screenshot."
            )

        result = run_verification_pipeline(db, text_to_verify, input_type)
        return _twiml(format_whatsapp_reply(result))

    except Exception:
        logger.exception("WhatsApp webhook failed to process incoming message")
        return _twiml(format_error_reply())


async def _extract_from_media(media_url: str) -> tuple[str, InputType]:
    """Twilio media URLs require Basic Auth with the account credentials."""
    if not (settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN):
        raise RuntimeError("Cannot fetch WhatsApp media without Twilio credentials configured")

    response = httpx.get(
        media_url,
        auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
        timeout=20,
        follow_redirects=True,
    )
    response.raise_for_status()
    text = extract_text_from_image(response.content)
    return text, InputType.IMAGE
