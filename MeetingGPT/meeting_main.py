import streamlit as st
from frontend.Screen_meeting import MeetingScreen
from frontend.Screen_dmental import DiaryScreen
from frontend.Screen_historico import HistoryScreen
from frontend.Screen_config import ConfigScreen
from frontend.Screen_login import LoginScreen
from database.database_user import DatabaseUser  # Importa o banco de usuários

def main():
    """
    Função principal para renderizar as telas do aplicativo.
    """
    if "first_run" not in st.session_state:
     st.session_state["first_run"] = True  # Marca que o app já rodou
     st.rerun()  # 🔄 Força um refresh automático

    # ✅ Verifica se o usuário está autenticado
    if "user_logged" not in st.session_state or not st.session_state["user_logged"]:
        st.sidebar.warning("🔒 Faça login para acessar o sistema.")

        screen = LoginScreen()
        # Renderiza a tela de login
        screen.render()
        # Encerra o aplicativo
        st.stop()
    # Apaga sidebar se o usuário estiver autenticado
    st.sidebar.title("")

    # ✅ Obtém o usuário logado e salva o `user_id` na sessão
    username = st.session_state["user_logged"]
    # ✅ Exibe a mensagem de boas-vindas
    st.sidebar.success(f"👋 Bem-vindo, {username}!")
    if "user_id" not in st.session_state:
        db_user = DatabaseUser()
        user_data = db_user.get_user(username)

        if not user_data:
            st.error("⚠️ Erro ao obter informações do usuário.")
            return

        st.session_state["user_id"] = user_data["id"]  # ✅ Salva `user_id` na sessão

    user_id = st.session_state["user_id"]  # ✅ Obtém o `user_id` da sessão


    # ✅ Verifica se a chave da API OpenAI foi configurada
    if "openai_api_key" not in st.session_state or not st.session_state["openai_api_key"]:
        st.sidebar.warning("⚠️ Acesse 'Configurações' para definir a chave da OpenAI antes de continuar.")

    # ✅ Opções de menu
    menu_options = [
        "📖 Tutorial de Uso",
        "📅 Tela de Reuniões",
        "📝 Tela de Diário Mental",
        "📂 Histórico",
        "⚙️ Configurações",
        "🚪 Logout"
    ]

    # ✅ Exibir menu lateral
    menu = st.sidebar.selectbox("📌 Menu de Navegação", menu_options)

    # ✅ Renderizar a página correspondente
    if menu == "📖 Tutorial de Uso":
        render_tutorial()
    elif menu == "📅 Tela de Reuniões":
        screen = MeetingScreen(user_id=user_id)  # ✅ Passa o `user_id` para a tela de reuniões
        screen.render()
    elif menu == "📝 Tela de Diário Mental":
        screen = DiaryScreen(user_id=user_id)  # ✅ Passa o `user_id` para a tela de diário mental
        screen.render()
    elif menu == "📂 Histórico":
        screen = HistoryScreen(user_id=user_id)  # ✅ Passa o `user_id` para a tela de histórico
        screen.render()
    elif menu == "⚙️ Configurações":
        screen = ConfigScreen()
        screen.render()
    elif menu == "🚪 Logout":
        st.cache_data.clear()
        st.cache_resource.clear()
        logout()

def render_tutorial():
    """
    Exibe um passo a passo de como utilizar o aplicativo MeetingGPT.
    """
    st.title("📖 Como Utilizar o MeetingGPT")
    st.markdown("""
    ## 🔹 **Passo 1: Configurar a Chave da API OpenAI 🔑**
    - Vá até **Configurações** no menu lateral.
    - Insira sua **chave da API OpenAI** para ativar os recursos de transcrição e insights.

    ## 🔹 **Passo 2: Criar uma Nova Reunião 🏢**
    - Acesse **Tela de Reuniões** no menu lateral.
    - Insira um **título para a reunião** e adicione os **participantes**.
    - Pressione **"Iniciar Reunião"** para começar a gravação de áudio.
    - Clique em **"Finalizar Reunião"** para salvar o áudio.

    ## 🔹 **Passo 3: Criar um Diário Mental 📝**
    - Vá até **Tela de Diário Mental**.
    - Insira um título e clique em **"Iniciar Diário"** para começar a gravação.
    - Após gravar seu diário, clique em **"Finalizar Diário"**.

    ## 🔹 **Passo 4: Transcrição e Geração de Insights 🧠**
    - Após finalizar uma gravação, clique em **"Gerar Transcrição e Insights"**.
    - O áudio será transcrito e analisado para gerar **insights valiosos**.

    ## 🔹 **Passo 5: Acessar o Histórico 📂**
    - Vá até **Histórico** para visualizar **reuniões e diários salvos**.
    - Clique em um registro para acessar os detalhes completos.

    ### 💡 **Dicas Extras:**
    - Você pode **editar qualquer informação** antes de salvar no banco de dados.
    - Todos os dados ficam armazenados localmente e podem ser acessados posteriormente.

    ---""")

    st.success("✅ Agora você está pronto para usar o MeetingGPT! Selecione uma opção no menu para começar.")

def logout():
    """
    Função para realizar logout do usuário.
    """
    st.session_state["user_logged"] = None  # Remove o usuário logado
    st.session_state["user_id"] = None  # Remove o `user_id`
    st.session_state["openai_api_key"] = None  # Reseta a API Key
    st.session_state.clear()  # Limpa todas as variáveis da sessão
    st.success("🚪 Logout realizado com sucesso! Retornando para a tela de login...")


    st.rerun()  # ✅ Reinicia a interface para exibir a tela de login

if __name__ == "__main__":
    main()
