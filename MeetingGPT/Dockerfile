# Usa a imagem oficial do Python 3.11 como base
FROM python:3.11

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala as dependências do sistema necessárias para PyAudio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    alsa-utils \
    pulseaudio \
    ffmpeg \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do projeto para dentro do container
COPY . /app

# Cria um ambiente virtual e instala as dependências do projeto
RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Define a variável de ambiente para garantir que os pacotes Python possam ser acessados
ENV PATH="/opt/venv/bin:$PATH"

# Comando para rodar o aplicativo no Railway
CMD ["streamlit", "run", "meeting_main.py", "--server.port=8501", "--server.address=0.0.0.0"]
