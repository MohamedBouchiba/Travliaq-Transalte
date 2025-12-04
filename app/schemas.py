from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to translate")
    source_language: str = Field(..., description="Source language code")
    target_language: str = Field(..., description="Target language code")


class TranslationResponse(BaseModel):
    translated_text: str
    target_language: str
