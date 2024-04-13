import os
import logging
import re
from flask import Flask, request
import requests
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Inicializa o app Flask
app = Flask(__name__)

# Define as variáveis de ambiente
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
arquivo_credenciais = "fresh-electron-418019-797333eb9d13.json"

# Configura o cliente do Google Sheets
conta = ServiceAccountCredentials.from_json_keyfile_name(arquivo_credenciais)
api = gspread.authorize(conta)
planilha = api.open_by_key("1nQYNS9BXqDLY9Zykm02OI-KJ5YDv15wy7SkjPsX172Y")
sheet = planilha.worksheet("Updates")


def extrair_id_video(link):
    # Expressão regular para encontrar o identificador do vídeo
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, link)
    if match:
        return match.group(1)
    else:
        return None

updates_processados = set()

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    
    update = request.json
    ultimo_id_processado = int(update["update_id"])
    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"]
    first_name = update["message"]["from"]["first_name"]

    try:
        # Busca o último ID processado no Google Sheets
        ultimo_id_update_registrado = int(sheet.cell(sheet.row_count, 1).value) if sheet.cell(sheet.row_count, 1).value else 0

        # Se o ID da mensagem atual for menor ou igual ao último ID processado, ignore-a
        if ultimo_id_processado <= ultimo_id_update_registrado:
            logging.info(f"Mensagem duplicada recebida e ignorada. ID: {ultimo_id_processado}")
            return "ok", 200
        updates_processados.add(ultimo_id_processado)
        
        if text == "/start":
            resposta = "BOAS VINDAS AO: ISSO NÃO É UM BOT, ISSO É UMA MÃE! Sabemos que é um desafio monitorar tudo que nossos filhos assistem, então estou aqui para te ajudar a entender se o conteúdo assistido por seu filho é adequado. Escolha o comando INSTRUÇÕES no Menu"
        
        elif "instruções" in text or "INSTRUÇÕES" in text or "Intruções" in text:
            resposta = "Para saber se um vídeo assistido por seu filho é adequado, cole aqui a URL do vídeo que deseja analisar. IMPORTANTE: Eu análiso vídeos que têm LEGENDA EM PORTUGUÊS no youtube, então se retornar algum erro pode ser isso. Como o que avaliado é a transcrição, há uma limitação quanto as imagens que aparecem nos vídeos. Se algo der errado e você quiser deixar um feedback escreva a palavra FEEDBACK + o que precisa ser melhorado (na mesma mensagem)"
        
        elif text == "/command1":
            resposta = "Que legal que você quer saber sobre funcionamento \o/. Esse bot foi criado por uma mãe, que na locura de volta a rotina pós-filho decidiu estudar algo novo. A base desse bot está em Python, toda vez que você manda uma mensagem, meu código lê o seu comando e te responde. Quando essa mensagem contem um link de vídeo no youtube, o meu código chama uma API de transcrição para acessar o conteúdo do vídeo e depois analisa com base em parâmetros que passei, pela API da OPENAI."

        elif text == "/command2":
            resposta = "Para saber se um vídeo assistido por seu filho é adequado, cole aqui a URL do vídeo que deseja analisar. IMPORTANTE: Eu análiso vídeos que têm LEGENDA EM PORTUGUÊS no youtube, então se retornar algum erro pode ser isso. Como o que avaliado é a transcrição, há uma limitação quanto as imagens que aparecem nos vídeos. Se algo der errado e você quiser deixar um feedback escreva a palavra FEEDBACK + o que precisa ser melhorado (na mesma mensagem)"
    
        elif "youtube.com" in text or "youtu.be" in text:
            if processing_youtube_link:
                logging.info("Link do YouTube já está sendo processado. Ignorando novo link.")
                resposta = "Desculpe, estou processando um link do YouTube agora. Por favor, aguarde."

            else:
                processing_youtube_link = True  # Define a flag para True
                id_video = extrair_id_video(text)
                if id_video:
                    try:
                        transcricoes = YouTubeTranscriptApi.get_transcript(id_video, languages=['pt'])
                        texto = ""
                        for transcricao in transcricoes:
                            if 'text' in transcricao:
                                texto += transcricao['text'] + " "  # Adiciona o texto do trecho atual ao texto completo
                                numero_caracteres = len(texto)
                        
                                if numero_caracteres < 45000:
                                    pergunta = f"Considere a seguinte transcrição de vídeo: {texto}\n\nMe diga sobre o que é o vídeo numa frase curta, e Considerando as classificações indicativas de conteúdo (DJCTQ Brasil), que avaliam os conteúdos como incluem L, 10, 12, 14, 16 e 18, classifique esse conteúdo, e justifique.Além da classificação DJCTQ, você pode adicionar, por favor, se o conteúdo é adequado para crianças? ALÉM DA CLASSIFICAÇÃO DJCTQ, entenda que mesmo conteúdos L (livre) podem ser desinteressantes para crianças. Então, quero que você também faça essa reflexão se o conteúdo é se algo que pode ser do interesse de crianças, se o conteúdo é infantil, e/ou de compreensão de uma criança."
                                    chat = openai.ChatCompletion.create(
                                        messages=[
                                        {"role": "user", "content": pergunta}
                                        ],
                                        model="gpt-3.5-turbo",  # Modelo da OpenAI
                                        api_key=OPENAI_API_KEY,
                                    )
                                    resposta = chat.choices[0].message.content.strip()
                                else:
                                    resposta = "Desculpe, este vídeo é muito longo e ultrapassa meus limites de análise."
                    except Exception as e:
                        print("Erro ao analisar o vídeo:", e)
                        resposta = "Ocorreu um erro ao analisar o vídeo. Certifique-se que o vídeo tem LEGENDAS em PORTUGUES."
                else:
                    resposta = "Não foi possível extrair o ID do vídeo. Por favor, verifique o formato da URL."
                processing_youtube_link = False 
                
        elif text == "/command3":
            resposta = "Obrigada e volte sempre <3"
        elif "FEEDBACK" in text or "Feedback" in text or "feedback" in text or "melhoria" in text:
            resposta = "Poxa, nem sempre conseguirei ajudar, sabe como é a sobrecarga materna né. Mas obrigada pela pontuação, buscarei melhorar."
        else:
            resposta = "Não entendi! Nem sempre consigo pensar em tudo, como uma mãe faria. Então, use os comandos disponíveis no chat para que eu funcione melhor."

    
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        mensagem = {"chat_id": chat_id, "text": resposta}
        requests.post(url, json=mensagem)


        # Guarda o ID do último update processado, para que possamos ignorar os já
        # processados no `if` acima
        ultimo_id_update = update["update_id"]            
        nome = update["message"]["from"]["first_name"]            
        mensagem = update["message"]["text"]            
        momento_atual = datetime.now()            
        momento_atual_formatado = momento_atual.strftime("%Y-%m-%d %H:%M:%S")            
        sheet.append_row([ultimo_id_update, nome, mensagem, resposta, momento_atual_formatado])

        logging.info(f"Resposta enviada: {resposta}")
        return "ok", 200

    except Exception as e:
        logging.error(f"Erro ao processar a mensagem: {str(e)}")
        return "ok", 200

# Inicia o servidor Flask se estiver no escopo principal
if __name__ == "__main__":
    app.run()
