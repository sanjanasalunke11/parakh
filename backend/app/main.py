import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import dashboard, ledger, verify, whatsapp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("parakh.main")

app = FastAPI(
    title="Parakh Truth Agent API",
    description=(
        "Channel-agnostic misinformation verification API. The browser frontend is one "
        "client of this API today; a WhatsApp webhook can call the same /api/verify/* "
        "endpoints tomorrow without any change to the core engine."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(verify.router)
app.include_router(ledger.router)
app.include_router(dashboard.router)
app.include_router(whatsapp.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Parakh backend ready. LLM=%s Search=%s Embeddings=%s", settings.LLM_PROVIDER, settings.SEARCH_PROVIDER, settings.EMBEDDING_PROVIDER)


@app.get("/api/health", tags=["meta"])
def health_check():
    return {
        "status": "ok",
        "llm_provider": settings.LLM_PROVIDER,
        "search_provider": settings.SEARCH_PROVIDER,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
    }
