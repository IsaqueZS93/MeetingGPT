import os
import logging
import queue
import time
from datetime import datetime
import numpy as np
import av
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import streamlit as st

# Configuração do logger
logging.basicConfig(
    filename='audio_recorder.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Diretório para salvar os áudios
AUDIO_SAVE_PATH = r'C:\Users\Novaes Engenharia\MeetingGPT\data\audio'
os.makedirs(AUDIO_SAVE_PATH, exist_ok=True)

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        """
        Inicializa o processador de áudio.
        """
        self.audio_data = []

    def recv_audio(self, frame: av.AudioFrame):
        """
        Captura e armazena os frames de áudio.
        """
        audio = frame.to_ndarray()
        self.audio_data.append(audio)
        return frame

class AudioRecorder:
    def __init__(self):
        """
        Inicializa o gravador de áudio.
        """
        self.audio_processor = None
        self.is_recording = False

    def start_recording(self):
        """
        Inicia a gravação de áudio usando streamlit-webrtc.
        """
        if self.is_recording:
            logging.warning("Tentativa de iniciar uma gravação já em andamento.")
            return

        self.audio_processor = webrtc_streamer(
            key="audio",
            mode=WebRtcMode.SENDRECV,
            audio_processor_factory=AudioProcessor,
            media_stream_constraints={"audio": True, "video": False},
        )
        
        if self.audio_processor.audio_processor:
            self.is_recording = True
            logging.info("🟢 Gravação iniciada com sucesso.")
            st.write("🎙️ Gravando... Pressione o botão para parar.")
        else:
            logging.error("❌ Erro ao iniciar a gravação.")
            raise RuntimeError("Erro ao iniciar a gravação.")

    def stop_recording(self):
        """
        Finaliza a gravação de áudio.
        """
        if not self.is_recording:
            logging.warning("Tentativa de parar uma gravação que não está em andamento.")
            raise RuntimeError("Nenhuma gravação está em andamento para parar.")

        self.is_recording = False
        logging.info("🔴 Gravação finalizada com sucesso.")
        st.write("🔴 Gravação finalizada.")

    def save_audio(self, filename=None):
        """
        Salva o áudio gravado em um arquivo .wav.
        """
        try:
            if not self.audio_processor or not self.audio_processor.audio_processor:
                logging.error("❌ Nenhum áudio capturado para salvar.")
                raise RuntimeError("Nenhum áudio capturado para salvar.")
            
            audio_data = np.concatenate(self.audio_processor.audio_processor.audio_data, axis=0)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"audio_{timestamp}.wav"
            
            filepath = os.path.join(AUDIO_SAVE_PATH, filename)
            
            with open(filepath, 'wb') as f:
                f.write(audio_data.tobytes())
            
            logging.info(f"✅ Áudio salvo com sucesso: {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"❌ Erro ao salvar o áudio: {e}")
            raise RuntimeError(f"Erro ao salvar o áudio: {e}")

# Exemplo de uso no Streamlit
if __name__ == "__main__":
    st.title("Gravador de Áudio - Streamlit WebRTC")
    recorder = AudioRecorder()
    
    if st.button("Iniciar Gravação"):
        recorder.start_recording()
    
    if st.button("Parar Gravação"):
        recorder.stop_recording()
        filepath = recorder.save_audio()
        st.success(f"✅ Áudio salvo em: {filepath}")
