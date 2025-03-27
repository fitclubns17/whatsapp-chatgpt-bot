from flask import Flask, request
import requests
import openai
import os

# Configurar as chaves de API com variáveis de ambiente
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Rota para validação do Webhook (necessário para Meta)
VERIFY_TOKEN = "fitclub_bot"

@app.route("/webhook", methods=["GET"])
def verify():
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token_sent == VERIFY_TOKEN:
        return challenge
    return "Invalid verification token", 403

# Rota para processar mensagens recebidas
@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    data = request.get_json()

    if "messages" in data and len(data["messages"]) > 0:
        message = data["messages"][0]
        user_message = message["text"]["body"]
        sender = message["from"]

        # Resposta com OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        bot_reply =_
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
