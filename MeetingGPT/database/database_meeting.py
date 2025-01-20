import sqlite3
import os
import logging

# Configuração inicial do logger
logging.basicConfig(
    filename='database_meeting.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class DatabaseMeeting:
    def __init__(self):
        """
        Inicializa a conexão com o banco de dados SQLite e cria/verifica tabelas.
        """
        try:
            # Conexão com SQLite
            self.connection = sqlite3.connect(DATABASE_PATH)
            self.connection.row_factory = sqlite3.Row  # Retorna dicionários em vez de tuplas
            self.cursor = self.connection.cursor()
            logging.info("🔗 Conexão com o banco de dados estabelecida.")

            # Verifica e cria tabelas se necessário
            self.create_tables()
            self.check_and_update_schema()  # Verifica se a coluna user_id existe

        except Exception as e:
            logging.error(f"❌ Erro ao conectar ao banco de dados: {e}")
            raise

    def create_tables(self):
        """
        Cria a tabela de reuniões/diários se ainda não existir.
        """
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,  -- Tipo: 'meeting' ou 'diary'
                    title TEXT,
                    participants TEXT,
                    date TEXT NOT NULL,
                    start_time TEXT,
                    end_time TEXT,
                    transcript TEXT,
                    insights TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            self.connection.commit()
            logging.info("✅ Tabela 'meetings' criada/verificada com sucesso.")
        except Exception as e:
            logging.error(f"❌ Erro ao criar a tabela 'meetings': {e}")
            raise

    def check_and_update_schema(self):
        """
        Verifica se a coluna 'user_id' está na tabela 'meetings' e adiciona se necessário.
        """
        try:
            # Obtém os nomes das colunas na tabela
            self.cursor.execute("PRAGMA table_info(meetings)")
            columns = [row["name"] for row in self.cursor.fetchall()]

            # Se 'user_id' não estiver na tabela, adiciona a coluna
            if "user_id" not in columns:
                self.cursor.execute("ALTER TABLE meetings ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")
                self.connection.commit()
                logging.info("✅ Coluna 'user_id' adicionada com sucesso na tabela 'meetings'.")
            else:
                logging.info("ℹ️ Coluna 'user_id' já existe na tabela 'meetings'. Nenhuma alteração necessária.")
        except Exception as e:
            logging.error(f"❌ Erro ao verificar/adicionar coluna 'user_id': {e}")
            raise

    def insert_record(self, record):
        """
        Insere um registro no banco de dados.

        :param record: Dicionário contendo os dados do registro.
        :return: ID do registro inserido.
        """
        try:
            self.cursor.execute('''
                INSERT INTO meetings (user_id, type, title, participants, date, start_time, end_time, transcript, insights)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record["user_id"],
                record["type"],
                record["title"],
                record["participants"],
                record["date"],
                record["start_time"],
                record["end_time"],
                record["transcript"],
                record["insights"]
            ))
            self.connection.commit()
            record_id = self.cursor.lastrowid
            logging.info(f"📌 Registro inserido com sucesso. ID: {record_id}")
            return record_id
        except Exception as e:
            logging.error(f"❌ Erro ao inserir registro: {e}")
            raise

    def fetch_all_records(self):
        """
        Busca todos os registros no banco de dados.

        :return: Lista de dicionários com os registros.
        """
        try:
            self.cursor.execute("SELECT * FROM meetings")
            rows = self.cursor.fetchall()

            records = [dict(row) for row in rows]
            logging.info("📄 Registros buscados com sucesso.")
            return records
        except Exception as e:
            logging.error(f"❌ Erro ao buscar registros: {e}")
            raise

    def fetch_records_by_user(self, user_id):
        """
        Busca todas as reuniões e diários vinculados ao usuário logado.

        :param user_id: ID do usuário logado.
        :return: Lista de reuniões e diários do usuário.
        """
        try:
            self.cursor.execute("SELECT * FROM meetings WHERE user_id = ?", (user_id,))
            rows = self.cursor.fetchall()

            records = [dict(row) for row in rows]
            logging.info(f"📄 Registros do usuário {user_id} buscados com sucesso.")
            return records
        except Exception as e:
            logging.error(f"❌ Erro ao buscar registros do usuário {user_id}: {e}")
            raise

    def close_connection(self):
        """
        Fecha a conexão com o banco de dados.
        """
        try:
            self.connection.close()
            logging.info("🔌 Conexão com o banco de dados fechada.")
        except Exception as e:
            logging.error(f"❌ Erro ao fechar a conexão com o banco de dados: {e}")
            raise

# Exemplo de uso
if __name__ == "__main__":
    db = DatabaseMeeting()
    try:
        # 🔹 Exemplo de inserção de uma reunião vinculada a um usuário
        record_id = db.insert_record({
            "user_id": 1,  # Simulação do usuário logado
            "type": "meeting",
            "title": "Reunião de Alinhamento",
            "participants": "João, Maria, Carlos",
            "date": "2025-01-15",
            "start_time": "10:00",
            "end_time": "11:00",
            "transcript": "Texto da transcrição aqui.",
            "insights": "Insights gerados aqui."
        })
        print(f"📌 Registro inserido com ID: {record_id}")

        # 🔹 Busca todas as reuniões e diários do usuário 1
        user_records = db.fetch_records_by_user(1)
        print("📄 Registros do usuário logado:", user_records)
    finally:
        db.close_connection()
