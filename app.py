from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, send_from_directory
import requests
import os

app = Flask(__name__)

# Variáveis de ambiente
WHATSAPP_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "fitclub_bot")
TEMPLATE_NAME = os.getenv("TEMPLATE_NAME", "menu_fitclub_bot_v2")

# Caminho para imagens
STATIC_FOLDER = "static"
HORARIO_IMG = "horario.png"

# Rota para servir a imagem
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_FOLDER, filename)

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot WhatsApp do Fitclub está online!"

@app.route("/webhook", methods=["GET"])
def verify():
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    return challenge if token_sent == VERIFY_TOKEN else ("Token de verificação inválido", 403)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Webhook recebido:")
    print(data)

    try:
        value = data["entry"][0]["changes"][0]["value"]
        messages = value.get("messages", [])
        pricing_info = value.get("pricing", {})
        category = pricing_info.get("category", "unknown")
        pricing_type = pricing_info.get("type", "unknown")

        if messages:
            message = messages[0]
            sender = message["from"]

            # Caso o utilizador clique num botão
            if message["type"] == "button":
                button_text = message["button"]["text"].lower()
                print(f"🔘 Botão clicado: {button_text}")

                respostas = {
                    "como são as aulas": "São aulas de grupo de treino funcional de 45 minutos, nas quais usamos vários materiais (barras, halteres, bandas, peso corporal) para desenvolver as diversas capacidades físicas através do treino de padrões motores básicos (agachar, empurrar, puxar, levantar).",
                    "onde é o estúdio": "O Fitclub fica no Pavilhão da ADC de Vila Verde. Fácil acesso e estacionamento gratuito!",
                    "mensalidade": "A mensalidade é de 30€. O pagamento pode ser feito em numerário ou por MBWAY para o número 962854426 com a indicação do nome e mês.",
                    "planos alimentares": "Sim, temos esse serviço por 25€ para quem quer perder peso. Contacta o número +351962854426 para prosseguir.",
                    "o que levar para a aula": "Usa sapatilhas próprias (não usadas na rua). Podes trazer água e toalha (opcional).",
                    "quero inscrever-me já": "Para te inscreveres já, vai a https://fitclubns17.systeme.io/principal e preenche os dados (confirma o SPAM).",
                    "marcar aula experimental": "Marca a tua aula experimental pelo número +351962854426 indicando o horário preferido.",
                    "dificuldades plataforma": "Se tiveres dificuldades técnicas, acede ao grupo de Apoio Técnico - Plataforma, que o técnico entra em contacto contigo."
                }

                if button_text == "horário":
                    image_url = "https://whatsapp-chatgpt-bot-aosj.onrender.com/static/horario.png"
                    send_image_message(sender, image_url, "🕒 Este é o horário das aulas no Fitclub.")
                elif button_text in respostas:
                    send_text_message(sender, respostas[button_text])
                else:
                    send_text_message(sender, "Botão não reconhecido. Tenta novamente.")

            # Se for mensagem normal → enviar template apenas se estiver dentro da janela gratuita
            elif message["type"] == "text":
                if not pricing_info or category == "service" or pricing_type == "free":
                    print("📨 Mensagem de texto recebida → Enviar template com botões")
                    send_template_message(sender)
                else:
                    print("⛔ Fora da janela de 24h → Enviar template para reabrir conversa")
                    send_template_message(sender)

    except Exception as e:
        print("❌ Erro no webhook:", str(e))

    return "Mensagem recebida", 200

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
    print("📤 Enviar texto:", payload)
    response = requests.post(url, headers=headers, json=payload)
    print("📬 Resposta da Meta:", response.status_code, response.text)

def send_image_message(to, image_url, caption):
    url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {
            "link": image_url,
            "caption": caption
        }
    }
    print("🖼️ Enviar imagem:", payload)
    response = requests.post(url, headers=headers, json=payload)
    print("📬 Resposta da Meta (imagem):", response.status_code, response.text)

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
            "language": { "code": "pt_PT" }
        }
    }
    print("📤 Enviar template:", payload)
    response = requests.post(url, headers=headers, json=payload)
    print("📬 Resposta da Meta (template):", response.status_code, response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
