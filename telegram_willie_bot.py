from fastapi import FastAPI, Request
import httpx
import os
import asyncio

app = FastAPI()

# ---- CONFIGS ----
TELEGRAM_TOKEN = "7514793940:AAE1pZJlnSUJoh2Y3IU9b49U9qUg9Yt58LE"
ASSISTANT_ID = "asst_eO8HkcgdpaEOjx5hddytJMe3"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("🔐 OPENAI_API_KEY:", OPENAI_API_KEY)  # DEBUG

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
OPENAI_API_URL = "https://api.openai.com/v1/threads"
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "OpenAI-Beta": "assistants=v2",
    "Content-Type": "application/json"
}

EXPERT_PROMPT = """Você é um consultor agrícola altamente especializado no cultivo de Cannabis...
(continua igual, sem alterações)
"""

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    print("📤 Enviando mensagem para o Telegram:", data)  # DEBUG
    return httpx.post(url, json=data)

def send_photo(chat_id, file_id):
    url = f"{TELEGRAM_API_URL}/sendPhoto"
    data = {"chat_id": chat_id, "photo": file_id}
    return httpx.post(url, json=data)

async def process_message(chat_id, user_text):
    print("✅ Entrou na função process_message")  # DEBUG
    async with httpx.AsyncClient() as client:
        thread = await client.post(
            OPENAI_API_URL,
            headers=HEADERS,
            json={"assistant_id": ASSISTANT_ID}
        )
        print("🧵 Thread response:", thread.text)

        thread_id = thread.json().get("id")
        if not thread_id:
            print("❌ Erro: thread_id não recebido")
            send_message(chat_id, "Erro interno: não consegui iniciar a conversa.")
            return

        await client.post(
            f"{OPENAI_API_URL}/{thread_id}/messages",
            headers=HEADERS,
            json={"role": "system", "content": EXPERT_PROMPT}
        )

        msg_resp = await client.post(
            f"{OPENAI_API_URL}/{thread_id}/messages",
            headers=HEADERS,
            json={"role": "user", "content": user_text}
        )
        print("📩 Mensagem enviada à IA:", msg_resp.text)

        run_resp = await client.post(
            f"{OPENAI_API_URL}/{thread_id}/runs",
            headers=HEADERS,
            json={"assistant_id": ASSISTANT_ID}
        )
        print("🏃 Run response:", run_resp.text)

        run_id = run_resp.json().get("id")
        if not run_id:
            print("❌ Erro: run_id não recebido")
            send_message(chat_id, "Erro interno: não consegui processar a mensagem.")
            return

        for i in range(10):
            await asyncio.sleep(2)
            run_check = await client.get(
                f"{OPENAI_API_URL}/{thread_id}/runs/{run_id}", headers=HEADERS
            )
            status = run_check.json().get("status")
            print(f"⏳ Tentativa {i+1} – Run status:", status)
            if status == "completed":
                break

        msg_resp = await client.get(
            f"{OPENAI_API_URL}/{thread_id}/messages",
            headers=HEADERS
        )
        messages = msg_resp.json().get("data", [])
        resposta = "Erro ao responder."
        if messages:
            try:
                resposta = messages[-1]['content'][0]['text']['value']
            except Exception:
                resposta = messages[-1].get('content', 'Erro ao interpretar resposta.')

        print("🧠 Resposta final da IA:", resposta)  # DEBUG
        send_message(chat_id, resposta)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    print("📥 Dados recebidos do Telegram:", data)  # DEBUG

    message = data.get("message")
    if not message:
        print("⚠️ Nenhuma chave 'message' encontrada.")
        return {"ok": True}

    chat_id = message["chat"].get("id")
    if chat_id != 7514793940:
        print("🔒 Mensagem ignorada de outro usuário:", chat_id)
        return {"ok": True}

    if "text" in message:
        text = message["text"]
        print("📨 Texto recebido:", text)  # DEBUG
        asyncio.create_task(process_message(chat_id, text))

    return {"ok": True}

@app.get("/")
def root():
    return {"message": "Bot Willie Cervantes está no ar."}
