import os
import logging
import queue
import time
from datetime import datetime
import wave
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
from pydub import AudioSegment
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
    def __init__(self):
        """
        Inicializa o gravador de áudio usando WebRTC.
        """
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
            
            def callback(frame):
                if self.is_recording:
                    self.queue.put(frame)
                    self.frames.append(frame)
                return frame

            self.processor = webrtc_streamer(
                key="audio_recorder",
                mode=WebRtcMode.SENDONLY,
                audio_processor_factory=callback
            )

            logging.info("🟢 Gravação iniciada com sucesso.")
        except Exception as e:
            logging.error(f"❌ Erro ao iniciar a gravação: {e}")
            raise RuntimeError(f"Erro ao iniciar a gravação: {e}")

    def stop_recording(self):
        """
        Finaliza a gravação de áudio.
        """
        try:
            if not self.is_recording:
                logging.warning("Tentativa de parar uma gravação que não está em andamento.")
                raise RuntimeError("Nenhuma gravação está em andamento para parar.")

            self.is_recording = False
            logging.info("🔴 Gravação finalizada com sucesso.")
            print("🔴 Gravação finalizada.")  
        except Exception as e:
            logging.error(f"❌ Erro ao parar a gravação: {e}")
            raise RuntimeError(f"Erro ao parar a gravação: {e}")

    def save_audio(self, filename=None):
        """
        Salva o áudio gravado em um arquivo .wav (usando PyDub).
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
            audio_segment = AudioSegment(
                data=audio_data.tobytes(),
                sample_width=2,  # 16 bits por amostra
                frame_rate=44100,
                channels=1
            )
            
            audio_segment.export(filepath, format="wav")
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

        # Espera até que o usuário pressione ENTER para parar a gravação
        input("🔴 Pressione **ENTER** para parar a gravação.\n")

        recorder.stop_recording()
        filepath = recorder.save_audio()
        print(f"✅ Áudio salvo em: {filepath}")
    finally:
        recorder.cleanup()
