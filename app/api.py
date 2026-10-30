"""Aplicação para o módulo de extensão DevOps"""

from datetime import datetime

from fastapi import FastAPI, Response, status
from requests import request

from app.modelo import Tarefa

APP = FastAPI()
TAREFAS: list[Tarefa] = []


def criar_tarefa(titulo, descricao: str | None = None) -> Tarefa:
    """Cria uma tarefa com os dados informados."""
    return Tarefa(id=len(TAREFAS),
                  titulo=titulo,
                  descricao=descricao,
                  concluida=False,
                  criado_em=datetime.now())


def encontrar_tarefa(tarefa_id: int) -> Tarefa | None:
    """Retorna a tarefa com o id informado, ou None se não existir."""
    for tarefa in TAREFAS:
        if tarefa_id == tarefa.id:
            return tarefa
    return None


def notificar(mensagem: str):
    """Envia uma notificação para o serviço de mensagens."""
    resp = request(
        "POST",
        "http://localhost:8000/enviar",
        params={"mensagem": mensagem},
        timeout=5,
    )
    print("Mensagem enviada com sucesso: " + resp.text)


@APP.get("/")
async def index():
    """Rota inicial da API."""
    return {"mensagem": "Olá, mundo!"}


@APP.get("/autor")
async def autor():
    """Nome do autor do projeto"""
    return {"message": "Leandro Willian Fraccaroli"}


@APP.get("/tarefas")
async def tarefas():
    """Lista todas as tarefas."""
    return TAREFAS


@APP.post("/tarefas")
async def post_tarefas(titulo: str, descricao: str):
    """Cria uma nova tarefa."""
    tarefa_nova = criar_tarefa(titulo, descricao)
    TAREFAS.append(tarefa_nova)

    notificar(f"Tarefa {tarefa_nova.id} criada com sucesso")
    return {"message": "ok"}


@APP.get("/tarefas/{tarefa_id}")
async def tarefa_especifica(tarefa_id: int):
    """Retorna uma tarefa específica."""
    tarefa = encontrar_tarefa(tarefa_id)

    if not tarefa:
        return {"message": "Tarefa não existente"}

    return tarefa


@APP.put("/tarefas/{tarefa_id}")
async def concluir_tarefa(tarefa_id: int):
    """Marca uma tarefa como concluída."""
    tarefa = encontrar_tarefa(tarefa_id)

    if not tarefa:
        return {"message": "Tarefa não existente"}
    if tarefa.concluida:
        return {"message": "Atarefa já está concluida"}

    tarefa.finalizar()
    notificar(f"Tarefa {tarefa.id} concluida com sucesso")
    return tarefa


@APP.delete("/tarefas/{tarefa_id}")
async def apagar_tarefa(tarefa_id: int):
    """Apaga uma tarefa."""
    tarefa = encontrar_tarefa(tarefa_id)

    if not tarefa:
        return {"message": "Tarefa não existente"}

    TAREFAS.remove(tarefa)
    notificar(f"Tarefa {tarefa.id} apagada com sucesso")
    return Response(status_code=status.HTTP_204_NO_CONTENT)