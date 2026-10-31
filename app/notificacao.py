"""Serviço de notificações"""

from fastapi import FastAPI

APP_NOTFICACAO = FastAPI()


@APP_NOTFICACAO.post("/enviar")
async def enviar(mensagem: str):
    """Recebe uma mensagem e a exibe no console."""
    print(mensagem)
    return {"mensagem": "ok"}