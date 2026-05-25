FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    pkg-config \
    libssl-dev \
    patchelf \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

COPY App/requirements.txt .
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

COPY App/ .

RUN /venv/bin/pip install --no-cache-dir maturin && \
    cd rust_services && \
    /venv/bin/maturin build --release --out /tmp/wheels && \
    /venv/bin/pip install --no-cache-dir /tmp/wheels/*.whl && \
    rm -rf /app/rust_services/target

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /venv /venv
COPY --from=builder /app /app

ENV PATH="/venv/bin:${PATH}" \
    PYTHONPATH="/app:${PYTHONPATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_PORT=5000

WORKDIR /app
USER appuser

EXPOSE 5000

CMD ["sh", "-c", "uvicorn graphql.server:app --host 0.0.0.0 --port ${APP_PORT:-5000}"]
