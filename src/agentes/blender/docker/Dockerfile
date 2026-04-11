# =====================================================
# BLENDER RENDER SERVER — Docker headless
# =====================================================
# Build context = pasta blender/ (não docker/)
#
# Build:  docker build -t gadgethub-blender -f docker/Dockerfile .
# Run:    docker run -p 8585:8585 -v "%cd%/output:/app/output" gadgethub-blender
# =====================================================

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV BLENDER_VERSION=4.1
ENV BLENDER_URL=https://mirror.clarkson.edu/blender/release/Blender4.1/blender-4.1.0-linux-x64.tar.xz

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    xz-utils \
    libxi6 \
    libxxf86vm1 \
    libxfixes3 \
    libxrender1 \
    libgl1 \
    libsm6 \
    python3 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Instalar Blender
RUN wget -q ${BLENDER_URL} -O /tmp/blender.tar.xz \
    && tar -xf /tmp/blender.tar.xz -C /opt/ \
    && rm /tmp/blender.tar.xz \
    && ln -s /opt/blender-*/blender /usr/local/bin/blender

# Verificar instalação
RUN blender --version

# Dependências Python para o servidor API
RUN pip3 install --no-cache-dir \
    fastapi==0.109.0 \
    uvicorn==0.27.0 \
    python-multipart==0.0.6

# Diretório de trabalho
WORKDIR /app

# Copiar servidor API
COPY docker/server.py /app/server.py

# Copiar scripts do Blender
COPY scripts/ /app/scripts/

# Copiar templates
COPY templates/ /app/templates/

# Criar diretórios de trabalho
RUN mkdir -p /app/output /app/jobs /app/logs

# Porta da API
EXPOSE 8585

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8585/api/health')"

# Iniciar servidor
CMD ["python3", "server.py"]
