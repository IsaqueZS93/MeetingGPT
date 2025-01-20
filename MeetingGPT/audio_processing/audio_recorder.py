import sounddevice as sd
import wave
import os
import logging
import queue
import time
from datetime import datetime
import numpy as np

# Configuração do logger
logging.basicConfig(
    filename='audio_recorder.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Diretório para salvar os áudios
AUDIO_SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "audio")
os.makedirs(AUDIO_SAVE_PATH, exist_ok=True)

class AudioRecorder:
    def __init__(self, samplerate=44100, channels=1):
        """
        Inicializa o gravador de áudio com as configurações padrão.
        """
        self.samplerate = samplerate
        self.channels = channels
        self.frames = []
        self.queue = queue.Queue()
        self.is_recording = False

    def start_recording(self):
        """
        Inicia a gravação de áudio.
        """
        try:
            if self.is_recording:
                logging.warning("Tentativa de iniciar uma gravação já em andamento.")
                return

            self.is_recording = True
            self.frames = []
            print("🎙️ Gravando... Digite **ENTER** para parar a gravação.")
            self.stream = sd.InputStream(samplerate=self.samplerate, channels=self.channels, dtype='int16', callback=self.callback)
            self.stream.start()
            logging.info("🟢 Gravação iniciada com sucesso.")
        except Exception as e:
            logging.error(f"❌ Erro ao iniciar a gravação: {e}")
            raise RuntimeError(f"Erro ao iniciar a gravação: {e}")

    def callback(self, indata, frames, time, status):
        """
        Captura os frames de áudio enquanto a gravação estiver ativa.
        """
        if status:
            logging.warning(f"⚠️ Status de erro na captura de áudio: {status}")
        self.queue.put(indata.copy())

    def process_audio(self):
        """
        Processa os dados de áudio enquanto a gravação está ativa.
        """
        try:
            while self.is_recording:
                try:
                    data = self.queue.get(timeout=1)
                    self.frames.append(data)
                except queue.Empty:
                    time.sleep(0.1)
        except Exception as e:
            logging.error(f"❌ Erro no processamento de áudio: {e}")
            raise

    def stop_recording(self):
        """
        Finaliza a gravação de áudio.
        """
        try:
            if not self.is_recording:
                logging.warning("Tentativa de parar uma gravação que não está em andamento.")
                return

            self.is_recording = False
            self.stream.stop()
            self.stream.close()
            logging.info("🔴 Gravação finalizada com sucesso.")
            print("🔴 Gravação finalizada.")
        except Exception as e:
            logging.error(f"❌ Erro ao parar a gravação: {e}")
            raise RuntimeError(f"Erro ao parar a gravação: {e}")

    def save_audio(self, filename=None):
        """
        Salva o áudio gravado em um arquivo .wav.
        """
        try:
            if not self.frames:
                logging.error("❌ Tentativa de salvar um arquivo sem áudio.")
                raise RuntimeError("Nenhum áudio capturado para salvar.")

            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"audio_{timestamp}.wav"

            filepath = os.path.join(AUDIO_SAVE_PATH, filename)
            audio_data = np.concatenate(self.frames, axis=0)

            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16 bits por amostra
                wf.setframerate(self.samplerate)
                wf.writeframes(audio_data.tobytes())

            logging.info(f"✅ Áudio salvo com sucesso: {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"❌ Erro ao salvar o áudio: {e}")
            raise RuntimeError(f"Erro ao salvar o áudio: {e}")

    def cleanup(self):
        """
        Libera os recursos utilizados pelo gravador de áudio.
        """
        try:
            logging.info("⚡ Recursos de áudio liberados com sucesso.")
        except Exception as e:
            logging.error(f"❌ Erro ao liberar recursos de áudio: {e}")
            raise

# Exemplo de uso
if __name__ == "__main__":
    recorder = AudioRecorder()
    try:
        recorder.start_recording()
        input("🔴 Pressione **ENTER** para parar a gravação.")
        recorder.stop_recording()
        filepath = recorder.save_audio()
        print(f"✅ Áudio salvo em: {filepath}")
    finally:
        recorder.cleanup()
