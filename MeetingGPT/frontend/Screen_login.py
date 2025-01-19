import streamlit as st
import bcrypt
from database.database_user import DatabaseUser

# ✅ Estilos CSS para um layout mais elegante e profissional
st.markdown("""
    <style>
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            text-align: center;
        }
        .login-box {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            width: 100%;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 20px;
        }
        .stButton > button {
            width: 100%;
            background-color: #3498db;
            color: white;
            padding: 10px;
            font-size: 16px;
            border-radius: 5px;
            border: none;
            margin-top: 10px;
            transition: 0.3s;
        }
        .stButton > button:hover {
            background-color: #2980b9;
        }
        .input-box {
            width: 100%;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

class LoginScreen:
    def __init__(self):
        """
        Inicializa a tela de login e a conexão com o banco de usuários.
        """
        self.db = DatabaseUser()

    def render(self):
        """
        Renderiza a interface da tela de login.
        """
        st.markdown('<div class="container">', unsafe_allow_html=True)
        st.markdown('<div class="login-box">', unsafe_allow_html=True)

        st.title("🔐 Login no MeetingGPT")

        # ✅ Campos de entrada do usuário
        username = st.text_input("👤 Usuário", placeholder="Digite seu usuário", key="username")
        password = st.text_input("🔑 Senha", type="password", placeholder="Digite sua senha", key="password")

        # ✅ Opção para exibir a senha digitada
        show_password = st.checkbox("👁️ Mostrar senha")
        if show_password:
            st.write(f"🔓 Senha: `{password}`")

        # ✅ Botão de login
        if st.button("Entrar"):
            if self.authenticate_user(username, password):
                st.success("✅ Login realizado com sucesso!")
                st.session_state["user_logged"] = username  # ✅ Armazena o usuário logado na sessão
                st.rerun()  # ✅ Atualiza a interface após login
            else:
                st.error("❌ Usuário ou senha incorretos!")

        # ✅ Botão para criar conta
        if st.button("Criar Conta"):
            self.create_account()

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    def authenticate_user(self, usuario, senha):
        """
        Verifica as credenciais do usuário no banco de dados.

        :param usuario: Nome de usuário digitado
        :param senha: Senha digitada
        :return: True se as credenciais forem válidas, False caso contrário
        """
        user_data = self.db.get_user(usuario)
        if not user_data:
            return False  # Usuário não encontrado

        stored_hashed_password = user_data.get("senha")
        return bcrypt.checkpw(senha.encode("utf-8"), stored_hashed_password.encode("utf-8"))

    def create_account(self):
        """
        Renderiza a tela de criação de conta.
        """
        st.subheader("🆕 Criar Nova Conta")

        nome = st.text_input("✍️ Nome Completo")
        usuario = st.text_input("👤 Nome de Usuário")
        senha = st.text_input("🔑 Senha", type="password")
        confirmar_senha = st.text_input("🔐 Confirmar Senha", type="password")

        if st.button("Registrar"):
            if senha != confirmar_senha:
                st.error("⚠️ As senhas não coincidem. Tente novamente.")
                return

            if self.db.insert_user(nome, usuario, senha):
                st.success("✅ Conta criada com sucesso! Faça login agora.")
                st.rerun()
            else:
                st.error("❌ Erro ao criar conta. Nome de usuário pode já estar em uso.")

    def cleanup(self):
        """
        Fecha a conexão com o banco de dados.
        """
        self.db.close_connection()

# ✅ Exemplo de uso
if __name__ == "__main__":
    screen = LoginScreen()
    try:
        screen.render()
    finally:
        screen.cleanup()
