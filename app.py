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

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
LOG_FILE = "conversas_log.txt"

def registar_conversa(entrada, resposta):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - Pergunta: {entrada}\nResposta: {resposta}\n{'-'*40}\n")

# Perguntas frequentes com keywords
respostas_frequentes = [
    {
        "keywords": ["o que é", "fitclub"],
        "resposta": "O Fitclub é um estúdio de fitness que ajuda mulheres ocupadas a sentirem-se mais confiantes através do treino, mesmo que nunca tenham treinado antes!"
    },
    {
        "keywords": ["como funciona", "aulas"],
        "resposta": "As sessões são aulas de grupo de treino funcional de 45 minutos no Pavilhão da ADC de Vila Verde. Temos aulas às 9:15 e 18:15."
    },
    {
        "keywords": ["inscrever", "inscrição"],
        "resposta": "É simples! Vai a https://fitclubns17.systeme.io/principal , preenche os dados e recebe tudo por e-mail (confirma o spam)."
    },
    {
        "keywords": ["preço", "mensalidade", "quanto"],
        "resposta": "A mensalidade é de 30€. A primeira inclui taxa de inscrição de 15€."
    },
    {
        "keywords": ["avaliação", "mensal"],
        "resposta": "Sim! Todos os meses há avaliação da composição corporal e avaliação física."
    },
    {
        "keywords": ["experimentar", "teste", "aula"],
        "resposta": "Sim! Marca a tua aula experimental pelo número +351 962 854 426 indicando o horário preferido."
    },
    {
        "keywords": ["plataforma", "treino", "online"],
        "resposta": "A nossa plataforma é https://fitclubns17.pt/"
    },
    {
        "keywords": ["ajuda", "aceder", "técnico"],
        "resposta": "Pede apoio no grupo de Apoio Técnico - Plataforma."
    },
    {
        "keywords": ["pagar", "mensalidade", "mbway"],
        "resposta": "Podes pagar em numerário ou por MBWAY para o número 962854426 com a indicação do nome e mês."
    },
    {
        "keywords": ["levar", "trazer", "equipamento", "sapatilhas"],
        "resposta": "É obrigatório usar sapatilhas próprias (não usadas na rua) no estúdio. Também podes levar água e toalha (opcional)."
    },
    {
        "keywords": ["plano alimentar", "nutrição", "alimentação"],
        "resposta": "Sim, temos esse serviço extra para alunos com objetivo de perda de peso. Custa 25€."
    }
]

def encontrar_resposta(pergunta):
    pergunta = pergunta.lower()
    for item in respostas_frequentes:
        if any(palavra in pergunta for palavra in item["keywords"]):
            return item["resposta"]
    return None
