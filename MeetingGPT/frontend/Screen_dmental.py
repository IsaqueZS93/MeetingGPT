import streamlit as st
import logging
import datetime
from database.database_meeting import DatabaseMeeting
from audio_processing.audio_recorder import AudioRecorder
from audio_processing.transcribe import AudioTranscriber
from insights.insights_generator import InsightsGenerator

# Configuração inicial do logger
logging.basicConfig(
    filename='screen_dmental.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DiaryScreen:
    def __init__(self, user_id=None):
        """
        Inicializa a tela de diário mental, conectando-se ao banco de dados e configurando os módulos.
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
            st.session_state["audio_recorder"] = None
        if "user_id" not in st.session_state:
            st.session_state["user_id"] = self.user_id
        if "diary_data" not in st.session_state:
            st.session_state["diary_data"] = {
                "user_id": self.user_id,
                "type": "diary",
                "title": "",
                "participants": "Diário Pessoal",
                "date": datetime.date.today().strftime("%Y-%m-%d"),
                "start_time": datetime.datetime.now().time().strftime("%H:%M"),
                "end_time": (datetime.datetime.now() + datetime.timedelta(hours=1)).time().strftime("%H:%M"),
                "transcript": "",
                "insights": ""
            }

    def render(self):
        """
        Renderiza a interface da tela de diário mental usando Streamlit.
        """
        try:
            st.title("📖 Diário Mental")

            # Verifica se o usuário está autenticado
            if not self.user_id:
                st.error("⚠️ Usuário não identificado. Faça login novamente.")
                return

            # Atualiza user_id na sessão
            st.session_state["diary_data"]["user_id"] = self.user_id

            # Campos de entrada
            st.session_state["diary_data"]["title"] = st.text_input("📌 Título do Diário:", st.session_state["diary_data"]["title"])
            st.session_state["diary_data"]["date"] = st.date_input("📅 Data do Diário:", datetime.datetime.strptime(st.session_state["diary_data"]["date"], "%Y-%m-%d")).strftime("%Y-%m-%d")
            st.session_state["diary_data"]["start_time"] = st.time_input("⏳ Horário de Início:", datetime.datetime.strptime(st.session_state["diary_data"]["start_time"], "%H:%M")).strftime("%H:%M")
            st.session_state["diary_data"]["end_time"] = st.time_input("⏳ Horário de Término:", datetime.datetime.strptime(st.session_state["diary_data"]["end_time"], "%H:%M")).strftime("%H:%M")

            # 🚀 Botões de controle do diário
            if not st.session_state["recording"]:
                if st.button("🎙️ Iniciar Diário"):
                    self.start_diary()

            if st.session_state["recording"]:
                if st.button("🛑 Finalizar Diário"):
                    self.stop_diary()

            if st.session_state["audio_file_path"]:
                if st.button("📝 Gerar Transcrição e Insights"):
                    self.generate_transcription_and_insights()

            st.write("💡 **Nota:** Você pode editar as informações antes de salvar no banco de dados.")

        except Exception as e:
            logging.error(f"❌ Erro ao renderizar a tela de diário mental: {e}")
            st.error("Ocorreu um erro ao carregar a tela de diário mental.")

    def start_diary(self):
        """Inicia a gravação de áudio do diário mental."""
        try:
            st.session_state["audio_recorder"] = AudioRecorder()
            st.session_state["audio_recorder"].start_recording()
            st.session_state["recording"] = True
            logging.info("🟢 Diário iniciado e gravação de áudio em andamento.")
            st.success("✅ Diário iniciado com sucesso. Gravação de áudio em andamento.")
        except Exception as e:
            logging.error(f"❌ Erro ao iniciar a gravação: {e}")
            st.error("Erro ao iniciar a gravação de áudio.")

    def stop_diary(self):
        """Finaliza a gravação do diário mental e salva o áudio."""
        try:
            if st.session_state["audio_recorder"]:
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
                st.error("❌ Nenhuma gravação ativa foi encontrada.")
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

            # Transcrição do áudio
            transcription_data = self.transcriber.transcribe_audio(audio_file_path)
            st.session_state["diary_data"]["transcript"] = transcription_data.get("text", "")

            # Geração de insights
            insights_data = self.insights_generator.generate_insights(st.session_state["diary_data"]["transcript"])
            st.session_state["diary_data"]["insights"] = insights_data.get("insights", "")

            # Atualiza o user_id no dicionário antes de salvar no banco
            st.session_state["diary_data"]["user_id"] = self.user_id

            # Insere no banco de dados
            record_id = self.db.insert_record(st.session_state["diary_data"])
            st.success(f"✅ Dados salvos com sucesso no banco de dados! ID: {record_id}")
            logging.info(f"💾 Transcrição e insights gerados e salvos no banco de dados. ID: {record_id}.")

        except Exception as e:
            logging.error(f"❌ Erro ao gerar transcrição e insights: {e}")
            st.error("Erro ao gerar transcrição e insights.")

    def cleanup(self):
        """Encerra a conexão com o banco de dados."""
        self.db.close_connection()

if __name__ == "__main__":
    screen = DiaryScreen()
    try:
        screen.render()
    finally:
        screen.cleanup()
