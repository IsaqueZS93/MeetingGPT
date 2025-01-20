import os
import logging
import time
from datetime import datetime
import numpy as np
import av
import pydub
from streamlit_webrtc import WebRtcMode, webrtc_streamer
import streamlit as st

# Configuração do logger
logging.basicConfig(
    filename='audio_recorder.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Diretório para salvar os áudios
AUDIO_SAVE_PATH = r'C:\Users\Novaes Engenharia\MeetingGPT\data\audio'
os.makedirs(AUDIO_SAVE_PATH, exist_ok=True)

class AudioRecorder:
    def __init__(self):
        """ Inicializa o gravador de áudio. """
        self.audio_frames = []
        self.is_recording = False
        st.session_state["audio_ready"] = False
        logging.debug("✅ AudioRecorder inicializado.")

    def start_recording(self):
        """ Inicia a gravação de áudio usando streamlit-webrtc. """
        try:
            if self.is_recording:
                logging.warning("⚠️ Tentativa de iniciar uma gravação já em andamento.")
                return

            self.is_recording = True
            self.audio_frames = []  # Resetar os frames de áudio
            logging.info("🎬 Iniciando o webrtc_streamer...")

            def callback(frame: av.AudioFrame):
                """ Callback para capturar frames de áudio """
                self.audio_frames.append(frame)

            st.session_state["webrtc_ctx"] = webrtc_streamer(
                key="audio_capture",
                mode=WebRtcMode.SENDONLY,
                audio_receiver_size=1024,
                media_stream_constraints={"audio": True, "video": False},
                rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
                async_processing=True,
                on_audio_frame=callback
            )
            
            logging.info("🟢 Gravação iniciada com sucesso.")
            st.write("🎙️ Gravando... Pressione o botão para parar.")
        except Exception as e:
            logging.error(f"❌ Erro ao iniciar a gravação: {e}")
            st.error(f"Erro ao iniciar a gravação: {e}")

    def stop_recording(self):
        """ Finaliza a gravação de áudio e salva o arquivo. """
        try:
            if not self.is_recording:
                logging.warning("⚠️ Tentativa de parar uma gravação que não está em andamento.")
                st.warning("⚠️ Nenhuma gravação ativa encontrada.")
                return

            self.is_recording = False

            if self.audio_frames:
                self.process_audio()
                st.session_state["audio_ready"] = True
                logging.info("🔴 Gravação finalizada com sucesso.")
                st.write("🔴 Gravação finalizada.")
            else:
                logging.warning("⚠️ Nenhum áudio foi capturado.")
                st.warning("⚠️ Nenhum áudio foi capturado.")
        except Exception as e:
            logging.error(f"❌ Erro ao parar a gravação: {e}")
            st.error(f"Erro ao parar a gravação: {e}")

    def process_audio(self):
        """ Processa os frames de áudio capturados e converte para um arquivo de áudio. """
        try:
            audio_segments = []
            for frame in self.audio_frames:
                audio = np.frombuffer(frame.to_ndarray().tobytes(), dtype=np.int16)
                segment = pydub.AudioSegment(
                    data=audio.tobytes(),
                    sample_width=frame.format.bytes,
                    frame_rate=frame.sample_rate,
                    channels=len(frame.layout.channels),
                )
                audio_segments.append(segment)
            
            self.audio_data = sum(audio_segments)
            logging.info("✅ Áudio processado com sucesso.")
        except Exception as e:
            logging.error(f"❌ Erro ao processar frames de áudio: {e}")

    def save_audio(self, filename=None):
        """ Salva o áudio gravado em um arquivo .wav. """
        try:
            if not st.session_state.get("audio_ready"):
                logging.error("❌ Nenhum áudio capturado para salvar.")
                raise RuntimeError("Nenhum áudio capturado para salvar.")

            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"audio_{timestamp}.wav"

            filepath = os.path.join(AUDIO_SAVE_PATH, filename)
            self.audio_data.export(filepath, format="wav")

            logging.info(f"✅ Áudio salvo com sucesso: {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"❌ Erro ao salvar o áudio: {e}")
            st.error(f"Erro ao salvar o áudio: {e}")
            raise RuntimeError(f"Erro ao salvar o áudio: {e}")

# Exemplo de uso no Streamlit
if __name__ == "__main__":
    st.title("🎙️ Gravador de Áudio - Streamlit WebRTC")
    recorder = AudioRecorder()

    if st.button("▶️ Iniciar Gravação"):
        try:
            recorder.start_recording()
        except Exception as e:
            st.error(f"Erro ao iniciar gravação: {e}")

    if st.button("⏹️ Parar Gravação"):
        try:
            recorder.stop_recording()
            if st.session_state["audio_ready"]:
                filepath = recorder.save_audio()
                st.success(f"✅ Áudio salvo em: {filepath}")
            else:
                st.warning("⚠️ Nenhum áudio foi capturado. Verifique as permissões do microfone e tente novamente.")
        except Exception as e:
            st.error(f"Erro ao parar gravação: {e}")
