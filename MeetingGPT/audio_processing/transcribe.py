import os
import logging
import json
from datetime import datetime
import streamlit as st
import openai
import wave

# Configuração inicial do logger
logging.basicConfig(
    filename='transcribe.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Diretório onde as transcrições serão salvas
TRANSCRIPTS_SAVE_PATH = r'C:\Users\Novaes Engenharia\MeetingGPT\data\transcripts'
os.makedirs(TRANSCRIPTS_SAVE_PATH, exist_ok=True)

class AudioTranscriber:
    def __init__(self):
        """
        Inicializa o transcritor de áudio utilizando a nova API da OpenAI.
        """
        # Verifica se a chave está no session_state
        if "openai_api_key" in st.session_state and st.session_state["openai_api_key"]:
            self.api_key = st.session_state["openai_api_key"]
        elif "OPENAI_API_KEY" in os.environ and os.environ["OPENAI_API_KEY"]:
            self.api_key = os.environ["OPENAI_API_KEY"]
        else:
            logging.error("A chave da API OpenAI não foi encontrada.")
            raise RuntimeError("A chave da API OpenAI é necessária para usar o transcritor.")

        openai.api_key = self.api_key  # Configura a chave da API no OpenAI SDK
        logging.info(f"🔑 Chave da OpenAI carregada corretamente: {self.api_key[:10]}... (ocultado)")

    def transcribe_audio(self, audio_path):
        """
        Transcreve o áudio em texto usando a API Whisper da OpenAI (nova versão).

        :param audio_path: Caminho completo para o arquivo de áudio.
        :return: Dicionário com a transcrição e metadados.
        """
        try:
            # Verifica se o arquivo de áudio existe
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"O arquivo de áudio {audio_path} não foi encontrado.")

            # Verifica se o arquivo está no formato WAV
            if not audio_path.lower().endswith(".wav"):
                raise ValueError("O formato de áudio deve ser .wav")

            # Obtém a duração do áudio para validação
            with wave.open(audio_path, "rb") as wf:
                duration = wf.getnframes() / wf.getframerate()
                if duration < 1:
                    raise ValueError("O arquivo de áudio é muito curto para ser transcrito.")

            logging.info(f"🎤 Iniciando transcrição para o arquivo: {audio_path}")

            # Chamada para a API Whisper (modelo de transcrição da OpenAI) **ATUALIZADA**
            with open(audio_path, "rb") as audio_file:
                response = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="json"
                )

            # LOG da resposta para análise
            logging.info(f"📩 Resposta da API da OpenAI: {response}")

            # Verifica se a resposta contém a transcrição esperada
            if hasattr(response, "text"):  # ✅ Corrigido
                transcription = response.text
            else:
                raise ValueError(f"Resposta inesperada da API da OpenAI: {response}")

            logging.info("✅ Transcrição concluída com sucesso.")
            return {"text": transcription, "duration": duration}

        except Exception as e:
            logging.error(f"❌ Erro ao transcrever o áudio: {e}")
            raise RuntimeError(f"Erro ao transcrever o áudio: {e}")

    def save_transcription(self, transcription_data, filename=None):
        """
        Salva a transcrição em um arquivo JSON no diretório definido.

        :param transcription_data: Dicionário contendo a transcrição e metadados.
        :param filename: Nome do arquivo JSON (opcional).
        :return: Caminho completo do arquivo salvo.
        """
        try:
            if not transcription_data or "text" not in transcription_data:
                raise ValueError("Os dados da transcrição estão vazios.")

            # Gera um nome de arquivo com timestamp, se não fornecido
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"transcription_{timestamp}.json"

            filepath = os.path.join(TRANSCRIPTS_SAVE_PATH, filename)

            # Salva os dados em um arquivo JSON
            with open(filepath, 'w', encoding='utf-8') as json_file:
                json.dump(transcription_data, json_file, ensure_ascii=False, indent=4)

            logging.info(f"📄 Transcrição salva com sucesso: {filepath}")
            return filepath

        except Exception as e:
            logging.error(f"❌ Erro ao salvar a transcrição: {e}")
            raise RuntimeError(f"Erro ao salvar a transcrição: {e}")

# Exemplo de uso
if __name__ == "__main__":
    transcriber = AudioTranscriber()
    audio_file_path = input("Insira o caminho completo do arquivo de áudio para transcrição: ")

    try:
        transcription = transcriber.transcribe_audio(audio_file_path)
        file_path = transcriber.save_transcription(transcription)
        print(f"📄 Transcrição salva em: {file_path}")
    except Exception as e:
        print(f"❌ Erro durante o processo: {e}")
