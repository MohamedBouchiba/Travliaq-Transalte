FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_NAME=facebook/nllb-200-distilled-600M \
    TRANSFORMERS_CACHE=/app/model_cache

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

RUN mkdir -p ${TRANSFORMERS_CACHE}
RUN python -c "import os; from transformers import AutoModelForSeq2SeqLM, AutoTokenizer; model=os.environ.get('MODEL_NAME'); cache=os.environ.get('TRANSFORMERS_CACHE'); AutoTokenizer.from_pretrained(model, cache_dir=cache); AutoModelForSeq2SeqLM.from_pretrained(model, cache_dir=cache)"

COPY app ./app

CMD ["sh", "-c", "uvicorn app.main:app --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000}"]
