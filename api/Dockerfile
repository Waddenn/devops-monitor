FROM python:3.11-slim AS builder

WORKDIR /install
COPY api/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install/deps -r requirements.txt

FROM python:3.11-slim AS runtime

WORKDIR /app
COPY --from=builder /install/deps /usr/local
COPY api ./api

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
