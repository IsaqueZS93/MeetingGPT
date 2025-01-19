import os
import logging
import json
from datetime import datetime
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage  # Importação para tratar o retorno
from langchain.prompts import ChatPromptTemplate

# Configuração inicial do logger
logging.basicConfig(
    filename='insights_generator.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Diretório onde os insights serão salvos
INSIGHTS_SAVE_PATH = r'C:\Users\Novaes Engenharia\MeetingGPT\data\data_insights'
os.makedirs(INSIGHTS_SAVE_PATH, exist_ok=True)

class InsightsGenerator:
    def __init__(self):
        """
        Inicializa o gerador de insights utilizando LangChain OpenAI.
        """
        if "openai_api_key" in st.session_state and st.session_state["openai_api_key"]:
            self.api_key = st.session_state["openai_api_key"]
        elif "OPENAI_API_KEY" in os.environ and os.environ["OPENAI_API_KEY"]:
            self.api_key = os.environ["OPENAI_API_KEY"]
        else:
            logging.error("🔑 A chave da API OpenAI não foi encontrada.")
            raise RuntimeError("A chave da API OpenAI é necessária para gerar insights.")

        # Inicializa o modelo da OpenAI via LangChain
        self.llm = ChatOpenAI(openai_api_key=self.api_key, model="gpt-4o-mini")
        logging.info(f"🔑 Chave da OpenAI carregada corretamente: {self.api_key[:10]}... (ocultado)")

    def generate_insights(self, text):
        """
        Gera insights a partir do texto fornecido usando LangChain com a API da OpenAI.

        :param text: Texto de entrada para análise.
        :return: Dicionário com os insights gerados.
        """
        try:
            if not text.strip():
                raise ValueError("O texto de entrada está vazio.")

            logging.info("🧠 Iniciando a geração de insights...")

            # Criando prompt para insights
            prompt = ChatPromptTemplate.from_template(
                "1 - Não precisa fazer uma introdução. Analise e gere insights organizados sobre o seguinte texto: {texto}" +
                "2 - Faça um resumo da reunião ou diario mental com até 300 caracteres. Isso deve vir em primeiro lugar." +
                "3 - Quando o texto vier de uma reunião, organize os topicos principais com um titulo 'Topicos abordados:'." +
                "4 - Quando o texto vier de um diario mental organize o texto em topicos com um titulo 'Diario mental:'." +
                "5 - Os insights devem ser apresentados em bullet points, verifique o contexto geral da reunião ou diario mental."
            )

            # Chamada para a API via LangChain
            response = self.llm.invoke(prompt.format(texto=text))

            # ✅ Extraindo apenas o texto do AIMessage para evitar erros ao salvar no banco
            insights_text = response.content if isinstance(response, AIMessage) else str(response)

            if not insights_text.strip():
                raise ValueError("❌ Resposta inesperada da API da OpenAI. Nenhum insight gerado.")

            logging.info("✅ Insights gerados com sucesso.")
            return {
                "original_text": text,
                "insights": insights_text,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logging.error(f"❌ Erro ao gerar insights: {e}")
            raise RuntimeError(f"Erro ao gerar insights: {e}")

    def save_insights(self, insights_data, filename=None):
        """
        Salva os insights gerados em um arquivo JSON no diretório especificado.

        :param insights_data: Dicionário contendo os insights e metadados.
        :param filename: Nome do arquivo JSON (opcional).
        :return: Caminho completo do arquivo salvo.
        """
        try:
            if not insights_data or "insights" not in insights_data:
                raise ValueError("Os dados de insights estão vazios.")

            # Gera um nome de arquivo com timestamp, se não fornecido
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"insights_{timestamp}.json"

            filepath = os.path.join(INSIGHTS_SAVE_PATH, filename)

            # Salva os dados em um arquivo JSON
            with open(filepath, 'w', encoding='utf-8') as json_file:
                json.dump(insights_data, json_file, ensure_ascii=False, indent=4)

            logging.info(f"📄 Insights salvos com sucesso: {filepath}")
            return filepath

        except Exception as e:
            logging.error(f"❌ Erro ao salvar os insights: {e}")
            raise RuntimeError(f"Erro ao salvar os insights: {e}")

# Exemplo de uso
if __name__ == "__main__":
    generator = InsightsGenerator()
    input_text = input("Insira o texto para análise: ")

    try:
        insights = generator.generate_insights(input_text)
        file_path = generator.save_insights(insights)
        print(f"📄 Insights salvos em: {file_path}")
    except Exception as e:
        print(f"❌ Erro durante o processo: {e}")
