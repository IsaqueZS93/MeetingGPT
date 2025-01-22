# Usa uma imagem oficial do Python 3.11
FROM python:3.11

# Instala dependências do sistema necessárias para PyAudio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    alsa-utils \
    pulseaudio \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos para o container
COPY . /app

# Usa explicitamente o `python3` ao invés de `python`
RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Define o comando de inicialização
CMD ["streamlit", "run", "meeting_main.py", "--server.port=8501", "--server.address=0.0.0.0"]
