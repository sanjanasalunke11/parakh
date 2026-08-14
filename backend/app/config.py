from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central app configuration, loaded from environment / .env file.

    Every external dependency (LLM, search, embeddings) has a safe default
    so the app can run fully offline with mock/local providers.
    """

    APP_NAME: str = "Parakh"
    ENV: str = "development"

    # ---- Database ----
    DATABASE_URL: str = "sqlite:///./parakh.db"

    # ---- LLM (claim extraction + verification reasoning) ----
    LLM_PROVIDER: str = "mock"  # anthropic | groq | mock
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-5"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # ---- Evidence search ----
    SEARCH_PROVIDER: str = "mock"  # tavily | mock
    TAVILY_API_KEY: str = ""
    MAX_EVIDENCE_RESULTS: int = 6

    # ---- Semantic similarity / embeddings ----
    EMBEDDING_PROVIDER: str = "sentence_transformer"  # sentence_transformer | hashing
    SIMILARITY_THRESHOLD: float = 0.85
    SEMANTIC_SCAN_LIMIT: int = 3000

    # ---- OCR ----
    TESSERACT_CMD: str = ""

    # ---- CORS ----
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # ---- WhatsApp (Twilio) ----
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    # The exact public URL Twilio calls, e.g. https://parakh-backend.onrender.com
    # or an ngrok URL for local testing. Required for webhook signature
    # verification — without it, Twilio's signature can't be recomputed
    # correctly (the app still works, but skips verification and logs a
    # warning, so local testing isn't blocked on this being set).
    PUBLIC_BASE_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
