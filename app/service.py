from typing import Dict

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from app.config import Settings


class TranslatorService:
    LANG_CODE_MAP: Dict[str, str] = {
        "EN": "eng_Latn",
        "FR": "fra_Latn",
        "ES": "spa_Latn",
        "DE": "deu_Latn",
        "PT": "por_Latn",
        "IT": "ita_Latn",
        "NL": "nld_Latn",
        "RU": "rus_Cyrl",
        "AR": "arb_Arab",
        "ZH": "zho_Hans",
    }

    def __init__(self, settings: Settings):
        self.settings = settings
        self.tokenizer = AutoTokenizer.from_pretrained(
            settings.model_name, cache_dir=settings.transformers_cache
        )
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            settings.model_name, cache_dir=settings.transformers_cache
        )

    def _resolve_language(self, language_code: str) -> str:
        if not language_code:
            raise ValueError("Language code must be provided")
        clean_code = language_code.strip()
        mapped_code = self.LANG_CODE_MAP.get(clean_code.upper())
        if mapped_code:
            return mapped_code
        if clean_code in self.tokenizer.lang_code_to_id:
            return clean_code
        raise ValueError(f"Unsupported language code: {language_code}")

    def normalize_language_code(self, language_code: str) -> str:
        """Return the NLLB-compatible code for the given language identifier."""
        return self._resolve_language(language_code)

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        if not text:
            raise ValueError("Text to translate must not be empty")

        source_lang_code = self._resolve_language(source_language)
        target_lang_code = self._resolve_language(target_language)

        self.tokenizer.src_lang = source_lang_code
        inputs = self.tokenizer(text, return_tensors="pt")
        forced_bos_token_id = self.tokenizer.lang_code_to_id.get(target_lang_code)
        if forced_bos_token_id is None:
            raise ValueError(f"Unsupported target language code: {target_language}")

        generated_tokens = self.model.generate(
            **inputs,
            forced_bos_token_id=forced_bos_token_id,
            max_length=512,
        )
        return self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
