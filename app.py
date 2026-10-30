from fastapi import FastAPI, Response, status
from datetime import datetime
from requests import request

APP = FastAPI()

@APP.get("/")
async def index():
    return {"mensagem": "Olá, mundo!"}


#ESTRUTURA DA TAREFA
"""
{
    "id"            -> int,
    "titulo"        -> str,
    "descricao"     -> "str",
    "concluida"     -> bool,
    "criado_em"     -> datetime
    "concluida_em"  -> datetime | None
}
"""
TAREFAS = []


def criar_tarefa(titulo, descricao):
    return {
        "id": len(TAREFAS),
        "titulo": titulo,
        "descricao": descricao,
        "concluida": False,
        "criado_em": datetime.now()
    }

def encontrar_tarefa(id: int) -> dict | None:
    global TAREFAS
    for tarefa in TAREFAS:
        if id == int(tarefa["id"]):
            return tarefa


def notificar(mensagem: str):
    resp = request("POST", f"http://localhost:8000/enviar?mensagem={mensagem}")
    print("Mensagem enviada com sucesso: " + resp.text)


@APP.get("/tarefas")
async def tarefas():
    return TAREFAS


@APP.post("/tarefas")
async def post_tarefas(titulo: str, descricao: str):
    tarefa_nova = criar_tarefa(titulo, descricao)
    TAREFAS.append(tarefa_nova)

    notificar(f"Taarefa {tarefa_nova["id"]} criada com sucesso")
    return {"message": "ok"}


@APP.get("/tarefas/{id}")
async def tarefa_especifica(id: int):
    tarefa = encontrar_tarefa(id)

    if not tarefa:
        return {"message": "Tarefa não existente"}

    return tarefa


@APP.put("/tarefas/{id}")
async def concluir_tarefa(id: int):
    tarefa = encontrar_tarefa(id)

    if not tarefa:
        return {"message": "Tarefa não existente"}
    elif tarefa["concluida"] == True:
        return {"message": "Atarefa já está concluida"}

    tarefa["concluida"] = True
    tarefa["concluida_em"] = datetime.now()
    notificar(f"Tarefa {tarefa["id"]} concluida com sucesso")
    return tarefa


@APP.delete("/tarefas/{id}")
async def apagar_tarefa(id: int):
    tarefa = encontrar_tarefa(id)

    if not tarefa:
        return {"message": "Tarefa não existente"}

    TAREFAS.remove(tarefa)
    notificar(f"Taarefa {tarefa["id"]} apagada com sucesso")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
