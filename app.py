import os
from flask import Flask, request
import openai
from youtube_transcript_api import YouTubeTranscriptApi
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import time
import re
import requests
from datetime import datetime
import time
from dotenv import load_dotenv
from requests.exceptions import Timeout 

app = Flask(__name__)



load_dotenv()

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

arquivo_credenciais = "fresh-electron-418019-797333eb9d13.json"  #nome do arquivo do token. é preciso subir ele antes nos arquivos do colab
conta = ServiceAccountCredentials.from_json_keyfile_name(arquivo_credenciais)
api = gspread.authorize(conta)
planilha = api.open_by_key ("1nQYNS9BXqDLY9Zykm02OI-KJ5YDv15wy7SkjPsX172Y")
sheet = planilha.worksheet("Updates")



import re
def extrair_id_video(link):
    # Expressão regular para encontrar o identificador do vídeo
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, link)
    if match:
        return match.group(1)
    else:
        return None

@app.route('/', methods=['GET', 'HEAD'])
def index():
    if request.method == 'HEAD':
        return '', 200  # Retorna uma resposta vazia para solicitações HEAD
    else:
        # Lógica normal para solicitações GET
        return render_template('index.html')

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    
    update = request.json

    ultimo_id_processado = update["update_id"]
    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"]
    first_name = update["message"]["from"]["first_name"]
            
    if text == "/start":
        resposta = "BOAS VINDAS AO: ISSO NÃO É UM BOT, ISSO É UMA MÃE! Sabemos que é um desafio monitorar tudo que nossos filhos assistem, então estou aqui para te ajudar a entender se o conteúdo assistido por seu filho é adequado. Escolha o comando INSTRUÇÕES no Menu"
        
    elif "instruções" in text or "INSTRUÇÕES" in text or "Intruções" in text:
        resposta = "Para saber se um vídeo assistido por seu filho é adequado, cole aqui a URL do vídeo que deseja analisar. IMPORTANTE: Eu análiso vídeos que têm LEGENDA EM PORTUGUÊS no youtube, então se retornar algum erro pode ser isso. Como o que avaliado é a transcrição, há uma limitação quanto as imagens que aparecem nos vídeos. Se algo der errado e você quiser deixar um feedback escreva a palavra FEEDBACK + o que precisa ser melhorado (na mesma mensagem)"
        
    elif text == "/command1":
        resposta = "Que legal que você quer saber sobre funcionamento \o/. Esse bot foi criado por uma mãe, que na locura de volta a rotina pós-filho decidiu estudar algo novo. A base desse bot está em Python, toda vez que você manda uma mensagem, meu código lê o seu comando e te responde. Quando essa mensagem contem um link de vídeo no youtube, o meu código chama uma API de transcrição para acessar o conteúdo do vídeo e depois analisa com base em parâmetros que passei, pela API da OPENAI."

    elif text == "/command2":
        resposta = "Para saber se um vídeo assistido por seu filho é adequado, cole aqui a URL do vídeo que deseja analisar. IMPORTANTE: Eu análiso vídeos que têm LEGENDA EM PORTUGUÊS no youtube, então se retornar algum erro pode ser isso. Como o que avaliado é a transcrição, há uma limitação quanto as imagens que aparecem nos vídeos. Se algo der errado e você quiser deixar um feedback escreva a palavra FEEDBACK + o que precisa ser melhorado (na mesma mensagem)"
    
    elif "youtube.com" in text or "youtu.be" in text:
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
                                api_key=OPENAI_API_KEY
                                timeout=35
                            )
                            resposta = chat.choices[0].message.content.strip()
                        else:
                            resposta = "Desculpe, este vídeo é muito longo e ultrapassa meus limites de análise."
            except Exception as e:
                print("Erro ao analisar o vídeo:", e)
                resposta = "Ocorreu um erro ao analisar o vídeo. Certifique-se que o vídeo tem LEGENDAS em PORTUGUES."
        else:
            resposta = "Não foi possível extrair o ID do vídeo. Por favor, verifique o formato da URL."
    
    elif text == "/command3":
        resposta = "Obrigada e volte sempre <3"
    elif "FEEDBACK" in text or "Feedback" in text or "feedback" in text or "melhoria" in text:
        resposta = "Poxa, nem sempre conseguirei ajudar, sabe como é a sobrecarga materna né. Mas obrigada pela pontuação, buscarei melhorar."
    else:
        resposta = "Não entendi! Nem sempre consigo pensar em tudo, como uma mãe faria. Então, use os comandos disponíveis no chat para que eu funcione melhor."

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    mensagem = {"chat_id": chat_id, "text": resposta}
    resultado = requests.post(url, data=mensagem)
    print("Resposta enviada", resultado.json())

    # Guarda o ID do último update processado, para que possamos ignorar os já
    # processados no `if` acima
    ultimo_id_update = update["update_id"]            
    nome = update["message"]["from"]["first_name"]            
    mensagem = update["message"]["text"]            
    momento_atual = datetime.now()            
    momento_atual_formatado = momento_atual.strftime("%Y-%m-%d %H:%M:%S")            
    sheet.append_row([ultimo_id_update, nome, mensagem, resposta, momento_atual_formatado])

    print("Atualizações concluídas")

    return "ok" 


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True, timeout=120)
