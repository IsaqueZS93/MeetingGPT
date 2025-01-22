# Usa a imagem oficial do Python 3.11
FROM python:3.11

# Instala dependências do sistema necessárias para PyAudio e outras bibliotecas
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    alsa-utils \
    pulseaudio \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para dentro do container
COPY . /app

# Cria um ambiente virtual e instala as dependências do projeto
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Define o comando para iniciar o Streamlit no container
CMD ["streamlit", "run", "meeting_main.py", "--server.port=8501", "--server.address=0.0.0.0"]
