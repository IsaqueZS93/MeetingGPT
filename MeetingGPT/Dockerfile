# Usa uma imagem oficial do Python 3.11 como base
FROM python:3.11

# Garante que 'python' sempre aponte para 'python3'
RUN ln -s /usr/bin/python3 /usr/bin/python

# Instala dependências do sistema necessárias para PyAudio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    alsa-utils \
    pulseaudio \
    ffmpeg \
    build-essential \
    python3-pyaudio \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para o container
COPY . /app

# Cria e ativa um ambiente virtual
RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando para rodar o Streamlit automaticamente no Railway
CMD ["streamlit", "run", "meeting_main.py", "--server.port=8501", "--server.address=0.0.0.0"]
