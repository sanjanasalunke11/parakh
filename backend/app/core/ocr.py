import io

import pytesseract
from PIL import Image

from ..config import settings

if settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


def extract_text_from_image(image_bytes: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Invalid or unreadable image file: {exc}") from exc

    try:
        text = pytesseract.image_to_string(image, lang="eng+hin")
    except pytesseract.TesseractNotFoundError as exc:
        raise RuntimeError(
            "Tesseract OCR engine not found on this machine. Install it and, on Windows, "
            "set TESSERACT_CMD in backend/.env to its full path (see README OCR setup)."
        ) from exc
    except pytesseract.pytesseract.TesseractError:
        # Hindi ("hin") language pack likely not installed — retry with English only.
        text = pytesseract.image_to_string(image, lang="eng")

    return text.strip()
