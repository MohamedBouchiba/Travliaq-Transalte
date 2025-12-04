from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException

from app.config import settings
from app.schemas import TranslationRequest, TranslationResponse
from app.service import TranslatorService

translator_service: Optional[TranslatorService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global translator_service
    translator_service = TranslatorService(settings)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest) -> TranslationResponse:
    if translator_service is None:
        raise HTTPException(status_code=503, detail="Translator not initialized")

    try:
        translated_text = translator_service.translate(
            request.text, request.source_language, request.target_language
        )
        normalized_target = translator_service.normalize_language_code(
            request.target_language
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return TranslationResponse(
        translated_text=translated_text,
        target_language=normalized_target,
    )
