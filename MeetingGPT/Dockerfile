FROM python:3.11

# Instala dependências do sistema necessárias para PyAudio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    alsa-utils \
    pulseaudio \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Cria um ambiente virtual e instala as dependências do projeto
WORKDIR /app
COPY . /app
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "meeting_main.py", "--server.port=8501", "--server.address=0.0.0.0"]
