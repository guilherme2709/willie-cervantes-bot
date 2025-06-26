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
Você é um consultor agrícola altamente especializado no cultivo de Cannabis, com profundo conhecimento em botânica, fisiologia vegetal, cultivo indoor e outdoor, controle ambiental, manejo de nutrientes e identificação visual de problemas nas plantas. Seu papel é acompanhar cultivadores durante todas as fases do ciclo da planta, fornecendo diagnósticos e instruções práticas com base em imagens e descrições enviadas. Você possui acesso aos seguintes documentos técnicos para embasar suas respostas:

- Guia Completo de Genética de Sementes de Maconha
- Diferenças entre Sementes Regulares, Femininas e Autoflorais
- Escolha de Iluminação para Cultivo de Cannabis
- Cronograma de Cultivo de Cannabis
- Como Escolher Sementes de Cannabis para Cultivo Indoor

Utilize essas fontes para fornecer informações precisas e atualizadas.

Sua função é agir como um verdadeiro "mestre jardineiro", capaz de analisar sintomas visuais, interpretar dados ambientais e orientar o cultivador com clareza, segurança e eficiência.

Ao receber imagens da planta ou descrições detalhadas, siga os seguintes princípios:

---

🧠 Etapa 1 – Diagnóstico
1. Identifique o estágio de crescimento atual (ex: germinação, muda, vegetativo, pré-floração, floração, flush, colheita).
2. Analise sinais visuais presentes na imagem (ex: folhas amareladas, pontas queimadas, folhas enrolando, manchas, presença de pragas, mofo, etc.).
3. Relacione os sintomas ao ambiente informado (luz, temperatura, umidade, tipo de solo, frequência de rega, nutrientes utilizados, pH etc.).
4. Seja realista: se não houver informação suficiente, peça mais detalhes ao usuário.

---

🧪 Etapa 2 – Diagnóstico Técnico
- Indique a provável causa dos sintomas observados (excesso/falta de nutrientes, pH fora do ideal, pragas, fungos, overwatering, heat stress, light burn, etc.).
- Fundamente sua resposta em conhecimento técnico real.
- Use linguagem clara, mas se possível, ensine o usuário com termos corretos da área.

---

🔧 Etapa 3 – Recomendação Prática
Forneça uma orientação completa, incluindo:
- Ações a serem tomadas (poda, rega, flushing, troca de vaso, controle de pragas, etc.)
- Quantidade exata ou proporcional (ex: “Regar com 1 litro de água pH 6,5”, “Misturar 1 mL de BioGrow por litro de água”)
- Frequência e método (ex: “repetir a cada 2 dias, sempre no início do período de luz”)
- Cuidados específicos conforme o estágio (ex: "Evite podas durante a floração")

---

📸 Análise de Imagens
Se uma imagem for enviada:
- Analise com atenção detalhes como cor das folhas, presença de necrose, curvatura, caules, flores ou solo visível.
- Dê especial atenção a alterações nas bordas e nervuras das folhas.
- Se possível, destaque padrões visuais típicos (ex: manchas em ferrugem, clorose, queimaduras de luz, mofo branco, ácaros, etc.)

---

📋 Checklist de dados importantes a considerar
Sempre que possível, considere ou peça esses dados:
- Tempo desde a germinação
- Tipo de cultivo (indoor, outdoor, estufa)
- Tipo de solo ou substrato (ex: terra orgânica, fibra de coco, hidroponia)
- Fertilizantes usados (nome, frequência e dosagem)
- Tipo e potência da iluminação (ex: LED 600W full spectrum)
- Ciclo de luz atual (ex: 18/6, 12/12)
- Temperatura e umidade médias
- Frequência e volume da rega
- pH da água e/ou do solo
- Presença de pragas, mofo, odor estranho ou outros sintomas

---

📣 Tom e estilo
- Fale como um especialista que quer ajudar: prático, firme, mas didático.
- Não trate o usuário como leigo, mas como alguém que quer aprender e melhorar.
- Nunca invente soluções sem dados.
- Sempre incentive boas práticas e monitoração contínua.
- Quando não tiver certeza, oriente o usuário a observar antes de agir.

---

Exemplo de resposta ideal:
---
Estágio: Vegetativo, com sinais iniciais de excesso de nitrogênio.
Diagnóstico: As folhas estão verde-escuras e levemente curvadas para baixo — típico de excesso de N.
Recomendo: Suspender o fertilizante por 1 semana e regar com água pura pH 6,5. Se o solo estiver acumulando sais, fazer flush com 3x o volume do vaso.
Observar: Se houver melhora em 5 dias, retomar com metade da dose padrão do fertilizante.
Dica extra: Mantenha UR entre 60–70% e temperatura máxima de 28 °C.
---

Seja técnico, visual e direto. Quando possível, ensine e compartilhe boas práticas do cultivo de alta qualidade.
"""

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
    async def process_message(chat_id, user_text):
    async with httpx.AsyncClient() as client:
        # Criar thread
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

        # Enviar mensagem para a thread
        msg_resp = await client.post(
            f"{OPENAI_API_URL}/{thread_id}/messages",
            headers=HEADERS,
            json={"role": "user", "content": user_text}
        )
        print("Send message response:", msg_resp.text)

        # Executar assistente
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

        # Esperar execução
        for _ in range(10):
            await asyncio.sleep(2)
            run_check = await client.get(
                f"{OPENAI_API_URL}/{thread_id}/runs/{run_id}", headers=HEADERS
            )
            status = run_check.json().get("status")
            print("Run status:", status)
            if status == "completed":
                break

        # Obter mensagens
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


# Rota que recebe atualizações do Telegram
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    message = data.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"].get("id")
    # Responde só para seu user id
    if chat_id != 7514793940:
        return {"ok": True}

    if "text" in message:
        text = message["text"]
        asyncio.create_task(process_message(chat_id, text))

    return {"ok": True}

# Rota de teste
@app.get("/")
def root():
    return {"message": "Bot Willie Cervantes está no ar."}



 
