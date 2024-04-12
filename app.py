import os
import requests
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

app = Flask(__name__)

load_dotenv()

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

@app.route("/")
def index():
    return "Oi Thi<3"


@app.route("/telegram", methods=["POST"])
def telegram_update():
    update = request.json
    url_envio_mensagem = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    chat_id = update["message"]["chat"]["id"]
    mensagem = {"chat_id": chat_id, "text": "mensagem <b>recebida</b>!", "parse_mode": "HTML"}
    requests.post(url_envio_mensagem, data=mensagem)
    return "ok"
