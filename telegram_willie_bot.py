from fastapi import FastAPI, Request
import httpx
import os
import asyncio

app = FastAPI()

# ---- CONFIGS ----
TELEGRAM_TOKEN = "7514793940:AAE1pZJlnSUJoh2Y3IU9b49U9qUg9Yt58LE"
ASSISTANT_ID = "asst_eO8HkcgdpaEOjx5hddytJMe3"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Defina no Render como secret

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
OPENAI_API_URL = "https://api.openai.com/v1/threads"
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "OpenAI-Beta": "assistants=v2",
    "Content-Type": "application/json"
}

# Prompt especialista para o assistente (cultivo de cannabis)
EXPERT_PROMPT = """
Você é um consultor agrícola altamente especializado no cultivo de Cannabis, com profundo conhecimento em botânica, fisiologia vegetal, cultivo indoor e outdoor, controle ambiental, manejo de nutrientes e identificação visual de problemas nas plantas. Seu papel é acompanhar cultivadores durante todas as fases do ciclo da planta, fornecendo diagnósticos e instruções práticas com base em imagens e descrições en


 
