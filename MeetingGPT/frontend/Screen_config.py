import streamlit as st
import logging
import os

# Configuração do logger
logging.basicConfig(
    filename='screen_config.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ConfigScreen:
    def __init__(self):
        """
        Inicializa a tela de configuração para definir a chave da OpenAI.
        """
        self.api_key = None  # Inicializa a variável

    def render(self):
        """
        Renderiza a interface da tela de configuração usando Streamlit.
        """
        try:
            st.title("Configuração da Chave OpenAI")
            st.write("Forneça a chave da OpenAI para habilitar as funcionalidades de transcrição e insights.")

            # Verifica se a chave já está armazenada na sessão
            if "openai_api_key" not in st.session_state:
                st.session_state["openai_api_key"] = ""

            # Campo para entrada da chave da API
            self.api_key = st.text_input(
                "Chave da OpenAI:", 
                value=st.session_state["openai_api_key"], 
                placeholder="Insira sua chave aqui", 
                type="password"
            )

            # Botão para salvar a chave
            if st.button("Salvar Chave"):
                if self.api_key:
                    st.session_state["openai_api_key"] = self.api_key  # Salva no session_state
                    os.environ["OPENAI_API_KEY"] = self.api_key  # Define no ambiente do sistema (opcional)
                    st.success("✅ Chave da OpenAI salva com sucesso para esta sessão.")
                    logging.info("✅ Chave da OpenAI configurada com sucesso.")

                    # Debug para verificar se está salvando corretamente
                    st.write(f"🔑 Chave armazenada: {st.session_state['openai_api_key'][:10]}... (ocultado para segurança)")
                else:
                    st.error("❌ A chave da OpenAI não pode estar vazia.")
                    logging.warning("⚠️ Tentativa de salvar uma chave vazia.")

            st.write("🔹 Nota: A chave será usada apenas durante esta sessão e não será salva permanentemente.")

        except Exception as e:
            logging.error(f"❌ Erro ao renderizar a tela de configuração: {e}")
            st.error("Ocorreu um erro ao carregar a tela de configuração.")

# Exemplo de uso
if __name__ == "__main__":
    config_screen = ConfigScreen()
    config_screen.render()
