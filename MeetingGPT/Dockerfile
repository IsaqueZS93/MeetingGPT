

# Define o diretório de trabalho
WORKDIR /app

# Copia todos os arquivos para dentro do contêiner
COPY . /app/

# Instala dependências do sistema necessárias para o PyAudio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    pulseaudio \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

FROM python:3.11

# Cria um ambiente virtual e instala as dependências do projeto
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Define o comando para rodar o Streamlit
CMD ["streamlit", "run", "meeting_main.py", "--server.port=8501", "--server.address=0.0.0.0"]
