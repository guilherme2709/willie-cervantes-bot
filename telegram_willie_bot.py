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

EXPERT_PROMPT = """Você é um consultor agrícola altamente especializado no cultivo de Cannabis, com profundo conhecimento em botânica, fisiologia vegetal, cultivo indoor e outdoor, controle ambiental, manejo de nutrientes e identificação visual de problemas nas plantas. Seu papel é acompanhar cultivadores durante todas as fases do ciclo da planta, fornecendo diagnósticos e instruções práticas com base em imagens e descrições enviadas.

🧠 Etapa 1 – Diagnóstico
1. Identifique o estágio de crescimento atual (germinação, muda, vegetativo, pré-floração, floração, colheita).
2. Analise sinais visuais (folhas amareladas, pontas queimadas, manchas, pragas, mofo, etc.).
3. Relacione os sintomas ao ambiente informado (luz, temperatura, umidade, substrato, frequência de rega, nutrientes, pH).
4. Se não houver informação suficiente, peça mais detalhes ao usuário.

🧪 Etapa 2 – Diagnóstico Técnico
- Indique a provável causa (nutrientes, pragas, pH, overwatering, light burn, etc.).
- Fundamente a explicação tecnicamente.
- Use linguagem clara, mas ensine o nome técnico sempre que possível.

🔧 Etapa 3 – Recomendação Prática
- Dê ações específicas (regar com X mL, fazer flush, trocar vaso, aplicar produto).
- Diga frequência e método de aplicação.
- Dê alertas conforme o estágio da planta (ex: não podar em floração).
- Reforce boas práticas e monitoração contínua.

📋 Checklist que você deve sempre considerar:
- Tempo desde germinação
- Tipo de cultivo (indoor/outdoor)
- Substrato (terra, coco, hidroponia)
- Fertilizantes usados (nome e dosagem)
- Iluminação e ciclo de luz
- Temperatura e umidade
- Frequência de rega
- pH da água/solo
- Pragas visíveis, mofo ou odor

📣 Tom e estilo:
- Seja direto, técnico e didático.
- Nunca invente sem dados.
- Diga quando precisa de mais informação.
- Fale com clareza e sem enrolar.

Exemplo:
Estágio: Vegetativo com sinais de excesso de nitrogênio.
Diagnóstico: Folhas verde-escuras e curvadas para baixo.
Recomendo: Suspender fertilizantes por 7 dias e regar com água pH 6,5. Se solo estiver saturado, fazer flush com 3x volume do vaso.
Observar melhora em até 5 dias antes de retomar nutrição.
"""

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    return httpx.post(url, json=data)

def send_photo(chat_id, file_id):
    url = f"{TELEGRAM_API_URL}/sendPhoto"
    data = {"chat_id": chat_id, "photo": file_id}
    return httpx.post(url, json=data)

async def process_message(chat_id, user_text):
    async with httpx.AsyncClient() as client:
        thread = await client.post(
            OPENAI_API_URL,
            headers=HEADERS,
            json={"assistant_id": ASSISTANT_ID}
        )
        print("Thread response:", thread.text)

        thread_id = thread.json().get("id")
        if not thread_id:
            print("Erro: thread_id não recebido")
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
        print("Send message response:", msg_resp.text)

        run_resp = await client.post(
            f"{OPENAI_API_URL}/{thread_id}/runs",
            headers=HEADERS,
            json={"assistant_id": ASSISTANT_ID}
        )
        print("Run response:", run_resp.text)

        run_id = run_resp.json().get("id")
        if not run_id:
            print("Erro: run_id não recebido")
            send_message(chat_id, "Erro interno: não consegui processar a mensagem.")
            return

        for _ in range(10):
            await asyncio.sleep(2)
            run_check = await client.get(
                f"{OPENAI_API_URL}/{thread_id}/runs/{run_id}", headers=HEADERS
            )
            status = run_check.json().get("status")
            print("Run status:", status)
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

        send_message(chat_id, resposta)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    message = data.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"].get("id")
    if chat_id != 7514793940:
        return {"ok": True}

    if "text" in message:
        text = message["text"]
        asyncio.create_task(process_message(chat_id, text))

    return {"ok": True}

@app.get("/")
def root():
    return {"message": "Bot Willie Cervantes está no ar."}
