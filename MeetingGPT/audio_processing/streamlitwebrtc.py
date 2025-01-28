import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import queue
import os
import wave
from datetime import datetime

# 📌 Exibir que o programa foi iniciado
st.markdown("### 🚀 Iniciando Gravador de Áudio WebRTC...")

# 📁 Diretório onde os áudios serão salvos
AUDIO_SAVE_PATH = r"C:\Users\Novaes Engenharia\MeetingGPT\data\audio"
os.makedirs(AUDIO_SAVE_PATH, exist_ok=True)
st.markdown(f"✅ **Diretório de áudio configurado:** `{AUDIO_SAVE_PATH}`")

# 🔹 Configuração WebRTC
RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
st.markdown("✅ **Configuração WebRTC carregada!**")

# 🔊 Fila para armazenar os frames de áudio
audio_queue = queue.Queue()
st.markdown("✅ **Fila de áudio inicializada!**")


def audio_callback(frame: av.AudioFrame):
    """Captura os frames de áudio e os coloca na fila."""
    audio_data = frame.to_ndarray()
    audio_queue.put(audio_data.tobytes())
    st.markdown("🎤 **Frame de áudio capturado e adicionado à fila!**")


def salvar_audio():
    """Salva o áudio capturado em um arquivo WAV e converte para MP3."""
    if audio_queue.empty():
        st.warning("⚠️ Nenhum áudio capturado.")
        return None

    st.markdown("🟡 **Iniciando processo de salvamento do áudio...**")

    # 🔹 Nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_wav = f"audio_{timestamp}.wav"
    filename_mp3 = f"audio_{timestamp}.mp3"

    filepath_wav = os.path.join(AUDIO_SAVE_PATH, filename_wav)
    filepath_mp3 = os.path.join(AUDIO_SAVE_PATH, filename_mp3)

    st.markdown(f"📁 **Criando arquivo de áudio:** `{filename_wav}`")

    # 🔹 Processar e salvar o áudio
    with wave.open(filepath_wav, "wb") as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16 bits
        wf.setframerate(44100)  # Taxa de amostragem padrão
        while not audio_queue.empty():
            wf.writeframes(audio_queue.get())

    st.markdown(f"✅ **Áudio salvo em WAV:** `{filepath_wav}`")

    # 🔥 Converter para MP3
    try:
        from pydub import AudioSegment
        st.markdown("🟡 **Convertendo áudio WAV para MP3...**")
        audio = AudioSegment.from_wav(filepath_wav)
        audio.export(filepath_mp3, format="mp3")
        os.remove(filepath_wav)  # Remove o arquivo WAV após conversão
        st.markdown(f"✅ **Áudio convertido para MP3:** `{filepath_mp3}`")
        return filepath_mp3
    except Exception as e:
        st.error(f"❌ Erro ao converter para MP3: {e}")
        return filepath_wav


# 🔹 Interface do Streamlit (Fluxo principal)
st.title("🎙️ Gravador de Áudio WebRTC")

# ✅ O WebRTC deve estar no fluxo principal do Streamlit
with st.container():
    st.markdown("🟡 **Iniciando WebRTC para captura de áudio...**")

    webrtc_ctx = webrtc_streamer(
        key="audio-recorder",
        mode=WebRtcMode.SENDONLY,
        rtc_configuration=RTC_CONFIG,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True,
    )

    if webrtc_ctx and webrtc_ctx.state.playing:
        st.markdown("🎙️ **Gravando... Pressione 'Stop' para finalizar.**")

        while webrtc_ctx.state.playing:
            if webrtc_ctx.audio_receiver:
                try:
                    frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                    for frame in frames:
                        audio_queue.put(frame.to_ndarray().tobytes())
                        st.markdown("🎤 **Adicionando frame de áudio à fila...**")  # <- Debug
                except queue.Empty:
                    st.markdown("⚠️ **Fila de áudio vazia. Nenhum frame recebido.**")  # <- Debug
                    continue
            else:
                st.markdown("⚠️ **WebRTC não está recebendo áudio!**")  # <- Debug
                break

        # 🔥 Salvar automaticamente após pressionar "Stop"
        st.markdown("🟡 **Processando áudio após interrupção...**")
        filepath = salvar_audio()
        if filepath:
            st.markdown(f"✅ **Áudio salvo com sucesso:** `{filepath}`")
            st.audio(filepath, format="audio/mp3")
        else:
            st.markdown("⚠️ **Erro ao salvar áudio.**")
