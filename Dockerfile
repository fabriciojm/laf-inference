# ---- build sd-cli ----
FROM ubuntu:24.04 AS builder

RUN apt-get update && apt-get install -y \
    ninja-build \
    build-essential \
    cmake \
    git \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

COPY scripts/build-sd.sh /tmp/build-sd.sh

RUN chmod +x /tmp/build-sd.sh && \
    /tmp/build-sd.sh /usr/local/bin


# ---- runtime ----
FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/fabriciojm/laf-inference"
LABEL org.opencontainers.image.description="FastAPI inference worker using stable-diffusion.cpp"
LABEL org.opencontainers.image.licenses="MIT"

RUN apt-get update && apt-get install -y \
    libopenblas0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/bin/sd-cli /usr/local/bin/sd-cli

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY app ./app

ENV SD_CLI=/usr/local/bin/sd-cli
ENV MODEL_PATH=/models/sd-turbo.safetensors

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
