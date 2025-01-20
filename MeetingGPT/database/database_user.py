import sqlite3
import os
import logging
import bcrypt

# Configuração inicial do logger
logging.basicConfig(
    filename='database_user.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuração inicial do logger
logging.basicConfig(
    filename='database_meeting.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DatabaseUser:
    def __init__(self):
        """
        Inicializa a conexão com o banco de dados SQLite e cria a tabela de usuários, se necessário.
        """
        try:
            self.connection = sqlite3.connect(DATABASE_PATH)
            self.cursor = self.connection.cursor()
            logging.info("Conexão com o banco de dados estabelecida.")
            self.create_users_table()
        except Exception as e:
            logging.error(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def create_users_table(self):
        """
        Cria a tabela de usuários no banco de dados, se ainda não existir.
        """
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    usuario TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL
                )
            ''')
            self.connection.commit()
            logging.info("Tabela de usuários criada/verificada com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao criar tabela de usuários: {e}")
            raise

    def insert_user(self, nome, usuario, senha):
        """
        Insere um novo usuário no banco de dados.

        :param nome: Nome completo do usuário.
        :param usuario: Nome de usuário único.
        :param senha: Senha em texto plano (será armazenada de forma segura).
        :return: ID do usuário inserido.
        """
        try:
            # Hash da senha antes de armazenar
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            self.cursor.execute('''
                INSERT INTO users (nome, usuario, senha)
                VALUES (?, ?, ?)
            ''', (nome, usuario, senha_hash))
            self.connection.commit()
            user_id = self.cursor.lastrowid
            logging.info(f"Usuário '{usuario}' cadastrado com sucesso. ID: {user_id}")
            return user_id
        except sqlite3.IntegrityError:
            logging.error(f"Erro: O nome de usuário '{usuario}' já está em uso.")
            return None
        except Exception as e:
            logging.error(f"Erro ao inserir usuário: {e}")
            raise

    def get_user(self, usuario):
        """
        Busca um usuário no banco de dados pelo nome de usuário.

        :param usuario: Nome de usuário a ser buscado.
        :return: Dicionário com os dados do usuário (incluindo a senha) ou None se não encontrado.
        """
        try:
            self.cursor.execute("SELECT id, nome, usuario, senha FROM users WHERE usuario = ?", (usuario,))
            row = self.cursor.fetchone()

            if row:
                return {"id": row[0], "nome": row[1], "usuario": row[2], "senha": row[3]}
            return None  # Retorna None se o usuário não for encontrado
        except Exception as e:
            logging.error(f"❌ Erro ao buscar usuário '{usuario}': {e}")
            return None

    def authenticate_user(self, usuario, senha):
        """
        Autentica um usuário verificando a senha criptografada.

        :param usuario: Nome de usuário.
        :param senha: Senha digitada pelo usuário.
        :return: True se a autenticação for bem-sucedida, False caso contrário.
        """
        try:
            user_data = self.get_user(usuario)  # Obtém o usuário do banco

            if user_data and "senha" in user_data:
                stored_hashed_password = user_data["senha"]
                if bcrypt.checkpw(senha.encode("utf-8"), stored_hashed_password.encode("utf-8")):
                    logging.info(f"✅ Usuário '{usuario}' autenticado com sucesso.")
                    return True
            logging.warning(f"⚠️ Falha na autenticação do usuário '{usuario}'.")
            return False
        except Exception as e:
            logging.error(f"❌ Erro ao autenticar usuário: {e}")
            return False

    def fetch_all_users(self):
        """
        Busca todos os usuários cadastrados no banco de dados.

        :return: Lista de dicionários com os dados dos usuários (exceto a senha).
        """
        try:
            self.cursor.execute('SELECT id, nome, usuario FROM users')
            rows = self.cursor.fetchall()
            users = [{"id": row[0], "nome": row[1], "usuario": row[2]} for row in rows]
            logging.info("Usuários buscados com sucesso.")
            return users
        except Exception as e:
            logging.error(f"Erro ao buscar usuários: {e}")
            raise

    def close_connection(self):
        """
        Fecha a conexão com o banco de dados.
        """
        try:
            self.connection.close()
            logging.info("Conexão com o banco de dados fechada.")
        except Exception as e:
            logging.error(f"Erro ao fechar a conexão com o banco de dados: {e}")
            raise

# Exemplo de uso
if __name__ == "__main__":
    db_user = DatabaseUser()
    try:
        # Criar usuário de teste
        user_id = db_user.insert_user("Luciano Novaes", "Luciano.N", "Novaes2025")
        if user_id:
            print(f"Usuário cadastrado com sucesso! ID: {user_id}")

        # Autenticar usuário
        autenticado = db_user.authenticate_user("Luciano.N", "Novaes2025")
        print("Autenticação bem-sucedida!" if autenticado else "Falha na autenticação.")

        # Buscar todos os usuários
        users = db_user.fetch_all_users()
        print("Usuários cadastrados:", users)

    finally:
        db_user.close_connection()
