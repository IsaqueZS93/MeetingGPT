import streamlit as st
import logging
from database.database_meeting import DatabaseMeeting

# Configuração inicial do logger
logging.basicConfig(
    filename='screen_historico.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class HistoryScreen:
    def __init__(self, user_id):
        """
        Inicializa a tela de histórico, conectando-se ao banco de dados e ao usuário logado.

        :param user_id: ID do usuário logado para filtrar os registros.
        """
        self.db = DatabaseMeeting()
        self.user_id = user_id  # ID do usuário logado

    def render(self):
        """
        Renderiza a interface da tela de histórico usando Streamlit.
        """
        try:
            st.title("📜 Histórico de Reuniões e Diários Mentais")

            # Obtém apenas os registros do usuário logado
            records = self.db.fetch_records_by_user(self.user_id)

            if not records:
                st.info("📌 Nenhum registro encontrado para este usuário.")
                return

            # Exibe os registros em uma tabela interativa
            st.write("### 📂 Registros Salvos")
            for record in records:
                with st.expander(f"📌 {record['type'].capitalize()} - {record['title']} (ID: {record['id']})"):
                    st.text(f"👤 Criado por: Usuário {record['user_id']}")
                    st.text(f"👥 Participantes: {record['participants']}")
                    st.text(f"📅 Data: {record['date']}")
                    st.text(f"⏳ Início: {record['start_time']} | Fim: {record['end_time']}")
                    st.text_area("📝 Transcrição:", record['transcript'], height=150)
                    st.text_area("💡 Insights:", record['insights'], height=100)

                    # Botão para excluir o registro
                    if st.button(f"🗑️ Excluir Registro {record['id']}", key=f"delete_{record['id']}"):
                        self.delete_record(record['id'])
                        st.rerun()  # Atualiza a página após exclusão

        except Exception as e:
            logging.error(f"❌ Erro ao renderizar a tela de histórico: {e}")
            st.error("❌ Ocorreu um erro ao carregar o histórico.")

    def delete_record(self, record_id):
        """
        Exclui um registro do banco de dados.

        :param record_id: ID do registro a ser excluído.
        """
        try:
            self.db.cursor.execute("DELETE FROM meetings WHERE id = ?", (record_id,))
            self.db.connection.commit()
            logging.info(f"🗑️ Registro ID {record_id} excluído com sucesso.")
        except Exception as e:
            logging.error(f"❌ Erro ao excluir registro ID {record_id}: {e}")
            st.error(f"Erro ao excluir o registro {record_id}: {e}")

    def cleanup(self):
        """
        Encerra a conexão com o banco de dados.
        """
        self.db.close_connection()

# Exemplo de uso
if __name__ == "__main__":
    user_id = 1  # Simulação de um usuário logado
    screen = HistoryScreen(user_id)
    try:
        screen.render()
    finally:
        screen.cleanup()
