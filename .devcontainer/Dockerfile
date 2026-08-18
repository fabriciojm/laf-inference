# Base image
FROM mcr.microsoft.com/devcontainers/python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    ninja-build \
    build-essential \
    cmake \
    bash \
    curl \
    libgomp1 \
    libopenblas0 \
    && rm -rf /var/lib/apt/lists/*

# Copy latest mise image
COPY --from=jdxcode/mise:latest /usr/local/bin/mise /usr/local/bin/

RUN echo 'eval "$(mise activate bash)"' >> /home/vscode/.bashrc && \
    echo 'eval "$(mise activate zsh)"' >> /home/vscode/.zshrc

