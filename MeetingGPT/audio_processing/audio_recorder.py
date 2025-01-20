import os

# Tenta instalar PortAudio e PyAudio antes da execução
os.system("apt-get update && apt-get install -y libportaudio2 portaudio19-dev && pip install sounddevice")

import pyaudio
import wave
import logging
import queue
import time
from datetime import datetime

# Configuração do logger
logging.basicConfig(
    filename='audio_recorder.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Diretório para salvar os áudios
AUDIO_SAVE_PATH = r'C:\Users\Novaes Engenharia\MeetingGPT\data\audio'
os.makedirs(AUDIO_SAVE_PATH, exist_ok=True)

class AudioRecorder:
    def __init__(self):
        """
        Inicializa o gravador de áudio com as configurações padrão.
        """
        self.audio = pyaudio.PyAudio()
        self.stream = None
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

            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024,
                stream_callback=self.callback
            )
            self.is_recording = True
            self.frames = []
            self.stream.start_stream()
            logging.info("🟢 Gravação iniciada com sucesso.")
            print("🎙️ Gravando... Digite **ENTER** para parar a gravação.")  
        except Exception as e:
            logging.error(f"❌ Erro ao iniciar a gravação: {e}")
            raise RuntimeError(f"Erro ao iniciar a gravação: {e}")

    def callback(self, in_data, frame_count, time_info, status):
        """
        Captura os frames de áudio enquanto a gravação estiver ativa.
        """
        if self.is_recording:
            self.queue.put(in_data)
            self.frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    def process_audio(self):
        """
        Processa os dados de áudio enquanto a gravação está ativa.
        """
        try:
            while self.is_recording:
                try:
                    data = self.queue.get(timeout=1)
                    self.frames.append(data)  # Adiciona os dados capturados
                except queue.Empty:
                    time.sleep(0.1)
                    continue
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
                raise RuntimeError("Nenhuma gravação está em andamento para parar.")

            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            logging.info("🔴 Gravação finalizada com sucesso.")
            print("🔴 Gravação finalizada.")  

        except Exception as e:
            logging.error(f"❌ Erro ao parar a gravação: {e}")
            raise RuntimeError(f"Erro ao parar a gravação: {e}")

    def save_audio(self, filename=None):
        """
        Salva o áudio gravado em um arquivo .wav (sem precisar de FFmpeg).
        """
        try:
            if not self.frames:
                logging.error("❌ Tentativa de salvar um arquivo sem áudio.")
                raise RuntimeError("Nenhum áudio capturado para salvar.")

            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"audio_{timestamp}.wav"

            filepath = os.path.join(AUDIO_SAVE_PATH, filename)

            # Salva o áudio em formato WAV usando wave (NÃO PRECISA DE FFMPEG)
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.frames))

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
            self.audio.terminate()
            logging.info("⚡ Recursos de áudio liberados com sucesso.")
        except Exception as e:
            logging.error(f"❌ Erro ao liberar recursos de áudio: {e}")
            raise

# Exemplo de uso
if __name__ == "__main__":
    recorder = AudioRecorder()
    try:
        recorder.start_recording()

        # Espera até que o usuário pressione ENTER para parar a gravação
        input("🔴 Pressione **ENTER** para parar a gravação.\n")

        recorder.stop_recording()
        filepath = recorder.save_audio()
        print(f"✅ Áudio salvo em: {filepath}")

    finally:
        recorder.cleanup()


