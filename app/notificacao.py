from fastapi import FastAPI, Response, status
from datetime import datetime

APP_NOTFICACAO = FastAPI()

@APP_NOTFICACAO.post("/enviar")
async def enviar(mensagem):
    print(mensagem)
    return {"mensagem": "ok"}