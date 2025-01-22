FROM python:3.11

WORKDIR /app
COPY . /app/

RUN apt-get update && apt-get install -y portaudio19-dev pulseaudio
RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "meeting_main.py", "--server.port=8501", "--server.address=0.0.0.0"]
