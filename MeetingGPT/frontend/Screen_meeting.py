import streamlit as st
import logging
import datetime
from database.database_meeting import DatabaseMeeting
from audio_processing.audio_recorder import AudioRecorder
from audio_processing.transcribe import AudioTranscriber
from insights.insights_generator import InsightsGenerator

# Configuração inicial do logger
logging.basicConfig(
    filename='screen_meeting.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MeetingScreen:
    def __init__(self, user_id=None):
        """
        Inicializa a tela de reuniões, conectando-se ao banco de dados e configurando os módulos.
        """
        self.db = DatabaseMeeting()
        self.transcriber = AudioTranscriber()
        self.insights_generator = InsightsGenerator()
        self.user_id = user_id or st.session_state.get("user_id")

        # Inicializa variáveis no session_state
        self.init_session_state()

    def init_session_state(self):
        """Inicializa variáveis da sessão do Streamlit para evitar erros."""
        if "recording" not in st.session_state:
            st.session_state["recording"] = False
        if "audio_file_path" not in st.session_state:
            st.session_state["audio_file_path"] = None
        if "audio_recorder" not in st.session_state:
            st.session_state["audio_recorder"] = AudioRecorder()
        if "user_id" not in st.session_state:
            st.session_state["user_id"] = self.user_id
        if "audio_ready" not in st.session_state:
            st.session_state["audio_ready"] = False
        if "meeting_data" not in st.session_state:
            st.session_state["meeting_data"] = {
                "user_id": self.user_id,
                "type": "meeting",
                "title": "",
                "participants": "",
                "date": datetime.date.today().strftime("%Y-%m-%d"),
                "start_time": datetime.datetime.now().time().strftime("%H:%M"),
                "end_time": (datetime.datetime.now() + datetime.timedelta(hours=1)).time().strftime("%H:%M"),
                "transcript": "",
                "insights": ""
            }

    def render(self):
        """
        Renderiza a interface da tela de reuniões usando Streamlit.
        """
        try:
            st.title("📌 Tela de Reuniões")

            # Verifica se o usuário está autenticado
            if not self.user_id:
                st.error("⚠️ Usuário não identificado. Faça login novamente.")
                return

            # Atualiza user_id na sessão
            st.session_state["meeting_data"]["user_id"] = self.user_id

            # Campos de entrada
            st.session_state["meeting_data"]["title"] = st.text_input("📌 Título da Reunião:", st.session_state["meeting_data"]["title"])
            st.session_state["meeting_data"]["participants"] = st.text_area("👥 Participantes:", st.session_state["meeting_data"]["participants"])
            st.session_state["meeting_data"]["date"] = st.date_input("📅 Data da Reunião:", datetime.datetime.strptime(st.session_state["meeting_data"]["date"], "%Y-%m-%d")).strftime("%Y-%m-%d")
            st.session_state["meeting_data"]["start_time"] = st.time_input("⏳ Horário de Início:", datetime.datetime.strptime(st.session_state["meeting_data"]["start_time"], "%H:%M")).strftime("%H:%M")
            st.session_state["meeting_data"]["end_time"] = st.time_input("⏳ Horário de Término:", datetime.datetime.strptime(st.session_state["meeting_data"]["end_time"], "%H:%M")).strftime("%H:%M")

            # 🚀 Botões de controle da reunião
            if not st.session_state["recording"]:
                if st.button("▶️ Iniciar Reunião"):
                    self.start_meeting()

            if st.session_state["recording"]:
                if st.button("⏹️ Finalizar Reunião"):
                    self.stop_meeting()

            if st.session_state["audio_file_path"]:
                if st.button("📝 Gerar Transcrição e Insights"):
                    self.generate_transcription_and_insights()

            st.write("💡 **Nota:** Você pode editar as informações antes de salvar no banco de dados.")

        except Exception as e:
            logging.error(f"❌ Erro ao renderizar a tela de reuniões: {e}")
            st.error("Ocorreu um erro ao carregar a tela de reuniões.")

    def start_meeting(self):
        """Inicia a gravação de áudio da reunião."""
        try:
            st.session_state["audio_recorder"].start_recording()
            st.session_state["recording"] = True
            logging.info("🟢 Reunião iniciada e gravação de áudio em andamento.")
            st.success("✅ Reunião iniciada com sucesso. Gravação de áudio em andamento.")
        except Exception as e:
            logging.error(f"❌ Erro ao iniciar a gravação: {e}")
            st.error("Erro ao iniciar a gravação de áudio.")

    def stop_meeting(self):
        """Finaliza a gravação da reunião e salva o áudio."""
        try:
            if st.session_state["recording"] and st.session_state["audio_ready"]:
                st.session_state["audio_recorder"].stop_recording()
                st.session_state["recording"] = False
                audio_path = st.session_state["audio_recorder"].save_audio()

                if audio_path:
                    st.session_state["audio_file_path"] = audio_path
                    logging.info(f"🔴 Gravação finalizada e salva em: {audio_path}")
                    st.success(f"✅ Gravação finalizada. Áudio salvo em: {audio_path}")
                else:
                    st.error("❌ Erro ao salvar o áudio. O arquivo não foi gerado.")
            else:
                st.warning("⚠️ Nenhum áudio foi capturado. Verifique as permissões do microfone.")
        except Exception as e:
            logging.error(f"❌ Erro ao parar a gravação: {e}")
            st.error(f"Erro ao parar a gravação: {e}")

    def generate_transcription_and_insights(self):
        """Gera a transcrição e insights do áudio gravado e salva no banco de dados."""
        try:
            if not self.user_id:
                st.error("⚠️ Usuário não identificado. Faça login novamente.")
                return

            audio_file_path = st.session_state["audio_file_path"]

            if not audio_file_path:
                st.error("⚠️ Nenhum áudio foi salvo. Verifique se a gravação foi finalizada corretamente.")
                return

            # Transcrição do áudio
            transcription_data = self.transcriber.transcribe_audio(audio_file_path)
            st.session_state["meeting_data"]["transcript"] = transcription_data.get("text", "")

            # Geração de insights
            insights_data = self.insights_generator.generate_insights(st.session_state["meeting_data"]["transcript"])
            st.session_state["meeting_data"]["insights"] = insights_data.get("insights", "")

            # Atualiza o user_id no dicionário antes de salvar no banco
            st.session_state["meeting_data"]["user_id"] = self.user_id

            # Insere no banco de dados
            record_id = self.db.insert_record(st.session_state["meeting_data"])
            st.success(f"✅ Dados salvos com sucesso no banco de dados! ID: {record_id}")
            logging.info(f"💾 Transcrição e insights gerados e salvos no banco de dados. ID: {record_id}.")

        except Exception as e:
            logging.error(f"❌ Erro ao gerar transcrição e insights: {e}")
            st.error("Erro ao gerar transcrição e insights.")

if __name__ == "__main__":
    screen = MeetingScreen()
    try:
        screen.render()
    finally:
        screen.cleanup()
