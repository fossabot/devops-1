"""Aplicação para o módulo de extensão DevOps"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated, List

from fastapi import Depends, FastAPI, Response, status
from requests import RequestException, request
from sqlmodel import Session, SQLModel, create_engine, select

from app.modelo import Tarefa


ENGINE = create_engine("mysql+pymysql://root:root@localhost:3306/devops")


def criar_sessao():
    """Abre uma sessão com o banco para cada requisição."""
    with Session(ENGINE) as s:
        yield s


SESSAO = Annotated[Session, Depends(criar_sessao)]


@asynccontextmanager
async def inicializacao(_api: FastAPI):
    """Cria as tabelas ao iniciar a aplicação."""
    SQLModel.metadata.create_all(ENGINE)
    yield


APP = FastAPI(lifespan=inicializacao)


def criar_tarefa(titulo, descricao: str | None = None) -> Tarefa:
    """Cria uma tarefa com os dados informados."""
    return Tarefa(titulo=titulo,
                  descricao=descricao,
                  concluida=False,
                  criado_em=datetime.now(timezone.utc))


def encontrar_tarefa(sessao: Session, tarefa_id: int) -> Tarefa | None:
    """Retorna a tarefa com o id informado, ou None se não existir."""
    return sessao.get(Tarefa, tarefa_id)


def notificar(mensagem: str):
    """Envia uma notificação para o serviço de mensagens."""
    try:
        resp = request(
            "POST",
            "http://localhost:8001/enviar",
            params={"mensagem": mensagem},
            timeout=5,
        )
        print("Mensagem enviada com sucesso: " + resp.text)
    except RequestException as erro:
        print(f"Falha ao notificar: {erro}")


@APP.get("/")
async def index():
    """Rota inicial da API."""
    return {"mensagem": "Olá, mundo!"}


@APP.get("/autor")
async def autor():
    """Nome do autor do projeto"""
    return {"message": "Leandro Willian Fraccaroli"}


@APP.get("/tarefas")
async def tarefas(sessao: SESSAO) -> List[Tarefa]:
    """Lista todas as tarefas."""
    return sessao.exec(select(Tarefa)).all()


@APP.post("/tarefas")
async def post_tarefas(sessao: SESSAO, titulo: str, descricao: str):
    """Cria uma nova tarefa."""
    tarefa_nova = criar_tarefa(titulo, descricao)

    sessao.add(tarefa_nova)
    sessao.commit()
    sessao.refresh(tarefa_nova)

    notificar(f"Tarefa {tarefa_nova.id} criada com sucesso")
    return {"message": "ok"}


@APP.get("/tarefas/{tarefa_id}")
async def tarefa_especifica(sessao: SESSAO, tarefa_id: int):
    """Retorna uma tarefa específica."""
    tarefa = encontrar_tarefa(sessao, tarefa_id)

    if not tarefa:
        return {"message": "Tarefa não existente"}

    return tarefa


@APP.put("/tarefas/{tarefa_id}")
async def concluir_tarefa(sessao: SESSAO, tarefa_id: int):
    """Marca uma tarefa como concluída."""
    tarefa = encontrar_tarefa(sessao, tarefa_id)

    if not tarefa:
        return {"message": "Tarefa não existente"}
    if tarefa.concluida:
        return {"message": "Atarefa já está concluida"}

    tarefa.finalizar()
    sessao.add(tarefa)
    sessao.commit()
    sessao.refresh(tarefa)

    notificar(f"Tarefa {tarefa.id} concluida com sucesso")
    return tarefa


@APP.delete("/tarefas/{tarefa_id}")
async def apagar_tarefa(sessao: SESSAO, tarefa_id: int):
    """Apaga uma tarefa."""
    tarefa = encontrar_tarefa(sessao, tarefa_id)

    if not tarefa:
        return {"message": "Tarefa não existente"}

    tarefa_id_apagada = tarefa.id
    sessao.delete(tarefa)
    sessao.commit()

    notificar(f"Tarefa {tarefa_id_apagada} apagada com sucesso")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
