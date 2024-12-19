from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import requests

app = FastAPI()


class ChatwootEvent(BaseModel):
    event: str
    data: dict


@app.post("/chatwoot/webhook")
async def chatwoot_webhook(media_url: str):
    try:
        response = requests.get(media_url)
        if response.status_code == 200:
            # Faça o processamento desejado com o conteúdo da imagem
            image_data = response.content
            # Salve ou redirecione para EvolutionAPI, conforme necessário
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Erro ao acessar a mídia")

    return {"status": "success"}


@app.get("/webhook/chatwoot")
async def webhook_health_check():
    return {"status": "Webhook is active"}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("teste:app", host="0.0.0.0", port=8001,
                log_level='info', reload=True)
