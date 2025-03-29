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
    print("📦 Dados recebidos no webhook:")
    print(data)

    if "messages" in data and len(data["messages"]) > 0:
        message = data["messages"][0]
        user_message = message["text"]["body"]
        sender = message["from"]

        print(f"📩 Mensagem recebida: {user_message}")
        print(f"📞 Número de destino: {sender}")

        # Gerar resposta com OpenAI
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}]
            )
            bot_reply = response.choices[0].message["content"]
            print(f"🧠 Resposta gerada: {bot_reply}")
        except Exception as e:
            print("❌ Erro ao gerar resposta com OpenAI:", str(e))
            bot_reply = "Houve um erro ao tentar gerar a resposta. Tenta novamente mais tarde."

        # Enviar resposta para o WhatsApp
        url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": sender,
            "type": "text",
            "text": {"body": bot_reply}
        }

        print("="*30)
        print("➡️ A enviar para a Meta:")
        print("URL:", url)
        print("Headers:", headers)
        print("Payload:", payload)

        try:
            response_whatsapp = requests.post(url, headers=headers, json=payload)
            print("📨 Resposta da Meta:", response_whatsapp.status_code, response_whatsapp.text)
        except Exception as e:
            print("❌ Erro ao enviar mensagem para o WhatsApp:", str(e))

    return "Mensagem recebida", 200

# Iniciar o servidor
@app.route("/", methods=["GET"])
def home():
    return "✅ O bot está online e a funcionar! 👋"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
