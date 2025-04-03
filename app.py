from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request
import requests
import openai
import os
from datetime import datetime

# Variáveis de ambiente
WHATSAPP_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "fitclub_bot")
TEMPLATE_NAME = os.getenv("TEMPLATE_NAME", "reabrir_conversa")

# Configurar chave da OpenAI
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
LOG_FILE = "conversas_log.txt"

def registar_conversa(entrada, resposta):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - Pergunta: {entrada}\\nResposta: {resposta}\\n{'-'*40}\\n")

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
            sender = message.get("from")

            if message.get("type") == "text" and message.get("text", {}).get("body"):
                user_message = message["text"]["body"]
                pergunta_normalizada = user_message.lower().strip()

                respostas_frequentes = {
                    "o que é o fitclub": "O Fitclub é um estúdio de fitness que ajuda mulheres ocupadas a sentirem-se mais confiantes através do treino, mesmo que nunca tenham treinado antes!",
                    "como funcionam as aulas": "As sessões são aulas de grupo de treino funcional de 45 minutos no Pavilhão da ADC de Vila Verde. Temos aulas às 9:15 e 18:15.",
                    "como posso inscrever-me": "É simples! Vai a https://fitclubns17.systeme.io/principal , preenche os dados e recebe tudo por e-mail (confirma o spam).",
                    "qual é o preço": "A mensalidade é de 30€. A primeira inclui taxa de inscrição de 15€.",
                    "fazem avaliação": "Sim! Todos os meses há avaliação da composição corporal e avaliação física.",
                    "posso ir experimentar": "Sim! Marca a tua aula experimental pelo número +351 962 854 426 indicando o horário preferido.",
                    "qual é a plataforma de treinos": "A nossa plataforma é https://fitclubns17.pt/",
                    "preciso de ajuda com a plataforma": "Pede apoio no grupo de Apoio Técnico - Plataforma.",
                    "como posso pagar a mensalidade": "Podes pagar em numerário ou por MBWAY para o número 962854426 com a indicação do nome e mês.",
                    "o que preciso de levar para a aula": "É obrigatório usar sapatilhas próprias (não usadas na rua) no estúdio. Também podes levar água e toalha (opcional).",
                    "fazem planos alimentares": "Sim, temos esse serviço extra para alunos com objetivo de perda de peso. Custa 25€."
                }

                resposta = respostas_frequentes.get(pergunta_normalizada)
                billable = pricing_info.get("billable", False)
                category = pricing_info.get("category", "unknown")
                pricing_type = pricing_info.get("type", "unknown")
                conversation_id = conversation.get("id", "N/A")

                print(f"💰 Tipo de mensagem: {pricing_type}")
                print(f"🧾 Categoria: {category}")
                print(f"💵 Faturável: {'Sim' if billable else 'Não'}")
                print(f"🆔 Conversa ID: {conversation_id}")
                print(f"📨 Mensagem de: {sender} → {user_message}")

                if category == "service" or pricing_type == "free":
                    if resposta:
                        bot_reply = resposta
                    else:
                        try:
                            completion = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[{"role": "user", "content": user_message}]
                            )
                            bot_reply = completion.choices[0].message["content"]
                        except Exception as e:
                            print("❌ Erro na OpenAI:", str(e))
                            bot_reply = "Desculpa, não consegui responder agora. Tenta mais tarde."

                    send_text_message(sender, bot_reply)
                    registar_conversa(user_message, bot_reply)
                else:
                    print("⚠️ Mensagem fora da janela gratuita.")
                    print("📨 A enviar mensagem template para reabrir a conversa...")
                    send_template_message(sender)

    except Exception as e:
        print("❌ Erro geral no webhook:", str(e))

    return "Mensagem processada", 200

def send_text_message(to, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    print("➡️ Enviar resposta para Meta (texto):")
    print("Payload:", payload)
    response = requests.post(url, headers=headers, json=payload)
    print("📬 Resposta Meta:", response.status_code, response.text)

def send_template_message(to):
    url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": TEMPLATE_NAME,
            "language": {"code": "pt_PT"}
        }
    }
    print("➡️ Enviar mensagem template para reabrir conversa:")
    print("Payload:", payload)
    response = requests.post(url, headers=headers, json=payload)
    print("📬 Resposta da Meta (template):", response.status_code, response.text)

@app.route("/", methods=["GET"])
def home():
    return "✅ O bot está online e funcional! 👋"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
