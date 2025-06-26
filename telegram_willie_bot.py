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

# Utilidade para enviar mensagem no Telegram
def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    return httpx.post(url, json=data)

# Enviar imagem (se quiser implementar depois)
def send_photo(chat_id, file_id):
    url = f"{TELEGRAM_API_URL}/sendPhoto"
    data = {"chat_id": chat_id, "photo": file_id}
    return httpx.post(url, json=data)

# Lógica principal: recebe mensagem, envia pro assistente, responde
async def process_message(chat_id, user_text):
    # Criar thread
    thread = await httpx.AsyncClient().post(
        OPENAI_API_URL,
        headers=HEADERS,
        json={"assistant_id": ASSISTANT_ID}
    )
    thread_id = thread.json().get("id")

    # Enviar mensagem para a thread
    await httpx.AsyncClient().post(
        f"{OPENAI_API_URL}/{thread_id}/messages",
        headers=HEADERS,
        json={"role": "user", "content": user_text}
    )

    # Executar assistente
    run_resp = await httpx.AsyncClient().post(
        f"{OPENAI_API_URL}/{thread_id}/runs",
        headers=HEADERS,
        json={"assistant_id": ASSISTANT_ID}
    )
    run_id = run_resp.json().get("id")

    # Esperar execução
    for _ in range(10):
        await asyncio.sleep(2)
        run_check = await httpx.AsyncClient().get(
            f"{OPENAI_API_URL}/{thread_id}/runs/{run_id}", headers=HEADERS
        )
        status = run_check.json().get("status")
        if status == "completed":
            break

    # Obter mensagens
    msg_resp = await httpx.AsyncClient().get(
        f"{OPENAI_API_URL}/{thread_id}/messages",
        headers=HEADERS
    )
    messages = msg_resp.json().get("data", [])
    resposta = messages[-1]['content'][0]['text']['value'] if messages else "Erro ao responder."
    
    send_message(chat_id, resposta)

# Rota que recebe atualizações do Telegram
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    message = data.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"].get("id")
    if "text" in message:
        text = message["text"]
        asyncio.create_task(process_message(chat_id, text))

    return {"ok": True}

# Rota de teste
@app.get("/")
def root():
    return {"message": "Bot Willie Cervantes está no ar."}
