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
TEMPLATE_NAME = os.getenv("TEMPLATE_NAME", "menu_fitclub_bot")

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
        messages = data["entry"][0]["changes"][0]["value"].get("messages", [])
        if messages:
            message = messages[0]
            sender = message["from"]

            if message["type"] == "button":
                button_text = message["button"]["text"].lower()
                print(f"🔘 Botão clicado: {button_text}")

                respostas = {
                    "como são as aulas": "As aulas são de treino funcional em grupo com duração de 45 minutos, usando barras, halteres, bandas e peso corporal.",
                    "mensalidade": "A mensalidade é de 30€. O pagamento pode ser feito em numerário ou por MBWAY para o número 962854426 com a indicação do nome e mês.",
                    "planos alimentares": "Sim, temos esse serviço por 25€ para quem quer perder peso.",
                    "o que levar para a aula": "Usa sapatilhas próprias (não usadas na rua). Podes trazer água e toalha (opcional).",
                    "quero inscrever-me já": "Para te inscreveres já, vai a https://fitclubns17.systeme.io/principal e preenche os dados (confirma o SPAM).",
                    "marcar aula experimental": "Marca a tua aula experimental pelo número +351 962 854 426 indicando o horário preferido.",
                    "dificuldades plataforma": "Se tiveres dificuldades técnicas, acede ao grupo de Apoio Técnico - Plataforma."
                }

                if button_text == "horário":
                    image_url = "https://whatsapp-chatgpt-bot-aosj.onrender.com/static/horario.png"
                    send_image_message(sender, image_url, "Este é o horário das aulas no Fitclub.")
                elif button_text in respostas:
                    send_text_message(sender, respostas[button_text])
                else:
                    send_text_message(sender, "Botão não reconhecido. Tenta novamente.")

    except Exception as e:
        print("❌ Erro:", str(e))

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

# Enviar imagem com link público
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
    print("📬 Resposta da Meta:", response.status_code, response.text)

# 👇 ESTA PARTE DEVE ESTAR NO FIM DO FICHEIRO
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
