# Usa a imagem oficial do Python 3.11
FROM python:3.11

# Instala dependências do sistema necessárias para PyAudio e outras bibliotecas
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    alsa-utils \
    pulseaudio \
    ffmpeg \
    build-essential \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto para dentro do contêiner
COPY . /app

# Cria e ativa o ambiente virtual e instala as dependências
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Define o ambiente virtual como padrão para os comandos subsequentes
ENV PATH="/opt/venv/bin:$PATH"

# Define o comando de execução do container
CMD ["streamlit", "run", "meeting_main.py", "--server.port=8501", "--server.address=0.0.0.0"]
