FROM python:3.12-slim

# tesseract-ocr: the Image tab's OCR needs the system binary, not just the
# pytesseract Python wrapper. tesseract-ocr-hin adds Hindi OCR support.
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-hin \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-deploy.txt ./
RUN pip install --no-cache-dir -r requirements-deploy.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Render sets $PORT at runtime; default to 8000 for local `docker run`.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
