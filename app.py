from flask import Flask, request
import requests
import openai
import os

# Carregar variáveis de ambiente
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "fitclub_bot")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Rota de verificação do webhook
@app.route("/webhook", methods=["GET"])
def verify():
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token_sent == VERIFY_TOKEN:
        return challenge
    return "Invalid verification token", 403

# Rota para processar mensagens recebidas do WhatsApp
@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    data = request.get_json()
    print("📦 Dados recebidos no webhook:")
    print(data)

    messages = data.get("messages", [])
    if messages:
        message = messages[0]
        user_message = message.get("text", {}).get("body")
        sender = message.get("from")

        print(f"📨 Mensagem recebida: {user_message}")
        print(f"📞 Número: {sender}")

        if user_message and sender:
            # Gerar resposta com OpenAI
            try:
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_message}]
                )
                bot_reply = completion.choices[0].message["content"]
            except Exception as e:
                print("❌ Erro na OpenAI:", e)
                bot_reply = "Ocorreu um erro ao gerar a resposta."

            # Enviar resposta via WhatsApp
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

            print("➡️ Enviar para a Meta:")
            print("URL:", url)
            print("Payload:", payload)

            response = requests.post(url, headers=headers, json=payload)
            print("📬 Resposta Meta:", response.status_code, response.text)

    return "Mensagem recebida", 200

# Página inicial
@app.route("/", methods=["GET"])
def home():
    return "✅ O bot está online e a funcionar! 👋"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
