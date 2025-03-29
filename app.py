from flask import Flask, request
import requests
import openai
import os

# Variáveis de ambiente
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "fitclub_bot")

# Configurar chave da OpenAI
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

@app.route("/webhook", methods=["GET"])
def verify():
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    return challenge if token_sent == VERIFY_TOKEN else ("Invalid verification token", 403)

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    data = request.get_json()
    print("📦 Webhook recebido:")
    print(data)

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        pricing_info = value.get("pricing", {})
        conversation = value.get("conversation", {})

        if messages:
            message = messages[0]
            user_message = message.get("text", {}).get("body")
            sender = message.get("from")

            print(f"📨 Mensagem de: {sender} → {user_message}")

            # INFO: Pricing e tipo de conversa
            billable = pricing_info.get("billable", False)
            category = pricing_info.get("category", "unknown")
            pricing_type = pricing_info.get("type", "unknown")
            conversation_id = conversation.get("id", "N/A")

            print(f"💰 Tipo de mensagem: {pricing_type}")
            print(f"🧾 Categoria: {category}")
            print(f"💵 Faturável: {'Sim' if billable else 'Não'}")
            print(f"🆔 Conversa ID: {conversation_id}")

            # Gerar resposta (dentro da janela de 24h = grátis)
            if category == "service" or pricing_type == "free_customer_service":
                try:
                    completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": user_message}]
                    )
                    bot_reply = completion.choices[0].message["content"]
                except Exception as e:
                    print("❌ Erro na OpenAI:", str(e))
                    bot_reply = "Desculpa, não consegui responder agora. Tenta mais tarde."

                # Enviar para WhatsApp
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

                print("➡️ Enviar resposta para Meta:")
                print("Payload:", payload)
                response = requests.post(url, headers=headers, json=payload)
                print("📬 Resposta Meta:", response.status_code, response.text)

            else:
                print("⚠️ Mensagem recebida fora da janela gratuita.")
                print("🚫 Resposta não enviada (evitar custos).")
                # Podes aqui futuramente usar uma mensagem template aprovada pela Meta

    except Exception as e:
        print("❌ Erro geral no webhook:", str(e))

    return "Mensagem processada", 200

@app.route("/", methods=["GET"])
def home():
    return "✅ O bot está online e funcional! 👋"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
