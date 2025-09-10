from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import datetime
import openai
import os
import tempfile
import requests
import json

app = Flask(__name__)

# ======================
# CONFIGURAÇÕES
# ======================

# Twilio
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP = "whatsapp:+14155238886"  # sandbox
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Controle de janela 24h
ultima_conversa = {}

# ======================
# FUNÇÕES AUXILIARES
# ======================

def transcrever_audio(url_arquivo):
    r = requests.get(url_arquivo)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
    tmp.write(r.content)
    tmp.close()
    with open(tmp.name, "rb") as f:
        transcript = openai.Audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    os.unlink(tmp.name)
    return transcript.text

def gerar_resposta_gpt(texto_usuario):
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role":"system", "content":"Você é um assistente financeiro amigável que organiza gastos."},
            {"role":"user", "content": texto_usuario}
        ],
        temperature=0.5
    )
    return completion.choices[0].message.content

def gerar_tts(texto, nome_arquivo):
    audio_resp = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=texto
    )
    caminho = os.path.join(tempfile.gettempdir(), nome_arquivo)
    with open(caminho, "wb") as f:
        f.write(audio_resp.audio)
    return caminho

# ======================
# ROTAS FLASK
# ======================

@app.route("/webhook", methods=["POST"])
def webhook():
    global ultima_conversa
    from_number = request.form.get("From")
    incoming_msg = request.form.get("Body")
    media_url = request.form.get("MediaUrl0")  # se tiver áudio

    resp = MessagingResponse()
    msg = resp.message()

    # Atualiza janela 24h
    ultima_conversa[from_number] = datetime.datetime.now()

    # 1️⃣ Se veio áudio, transcreve
    if media_url:
        try:
            texto_usuario = transcrever_audio(media_url)
        except Exception as e:
            msg.body(f"Erro ao processar áudio: {str(e)}")
            return str(resp)
    else:
        texto_usuario = incoming_msg

    # 2️⃣ Gera resposta GPT
    resposta_texto = gerar_resposta_gpt(texto_usuario)

    # 3️⃣ Gera TTS
    nome_audio = f"{from_number.replace('+','')}.mp3"
    caminho_audio = gerar_tts(resposta_texto, nome_audio)

    # 4️⃣ Envia resposta texto (sem upload de áudio)
    msg.body(resposta_texto)

    # Opcional: enviar áudio como mídia se Twilio permitir enviar arquivo local
    # Caso contrário, comente as linhas abaixo
    # with open(caminho_audio, "rb") as audio_file:
    #     msg.media(f"data:audio/mp3;base64,{base64.b64encode(audio_file.read()).decode()}")

    # Remove arquivo local
    os.remove(caminho_audio)

    return str(resp)
