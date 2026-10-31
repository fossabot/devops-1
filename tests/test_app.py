"""Testes da API de tarefas"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import app.api as api
from app.api import APP, criar_sessao

CLIENT = TestClient(APP)


@pytest.fixture(autouse=True)
def preparar(monkeypatch):
    """Usa um banco SQLite em memória novo a cada teste."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def sessao_teste():
        with Session(engine) as s:
            yield s

    APP.dependency_overrides[criar_sessao] = sessao_teste
    monkeypatch.setattr(api, "notificar", lambda mensagem: None)
    yield
    APP.dependency_overrides.clear()


def criar_tarefa_teste():
    """Cria uma tarefa padrão pela API."""
    return CLIENT.post(
        "/tarefas", params={"titulo": "Estudar", "descricao": "Aprender DevOps"}
    )


def test_index():
    """Testa a rota inicial."""
    resposta = CLIENT.get("/")
    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Olá, mundo!"}


def test_autor():
    """Testa a rota do autor."""
    resposta = CLIENT.get("/autor")
    assert resposta.status_code == 200
    assert resposta.json() == {"message": "Leandro Willian Fraccaroli"}


def test_tarefas():
    """Testa a listagem vazia."""
    resposta = CLIENT.get("/tarefas")
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_post_tarefas():
    """Testa a criação de uma tarefa."""
    resposta = criar_tarefa_teste()
    assert resposta.status_code == 200
    assert resposta.json() == {"message": "ok"}

    tarefas = CLIENT.get("/tarefas").json()
    assert len(tarefas) == 1
    assert tarefas[0]["titulo"] == "Estudar"
    assert tarefas[0]["descricao"] == "Aprender DevOps"
    assert tarefas[0]["concluida"] is False


def test_tarefa_especifica():
    """Testa a busca de uma tarefa pelo id."""
    criar_tarefa_teste()

    resposta = CLIENT.get("/tarefas/1")
    assert resposta.status_code == 200
    assert resposta.json()["id"] == 1
    assert resposta.json()["titulo"] == "Estudar"


def test_tarefa_especifica_inexistente():
    """Testa a busca de uma tarefa que não existe."""
    resposta = CLIENT.get("/tarefas/99")
    assert resposta.json() == {"message": "Tarefa não existente"}


def test_concluir_tarefa():
    """Testa a conclusão de uma tarefa."""
    criar_tarefa_teste()

    resposta = CLIENT.put("/tarefas/1")
    assert resposta.status_code == 200
    assert resposta.json()["concluida"] is True
    assert resposta.json()["concluida_em"] is not None


def test_concluir_tarefa_ja_concluida():
    """Testa concluir uma tarefa já concluída."""
    criar_tarefa_teste()
    CLIENT.put("/tarefas/1")

    resposta = CLIENT.put("/tarefas/1")
    assert resposta.json() == {"message": "Atarefa já está concluida"}


def test_concluir_tarefa_inexistente():
    """Testa concluir uma tarefa que não existe."""
    resposta = CLIENT.put("/tarefas/99")
    assert resposta.status_code == 200
    assert resposta.json() == {"message": "Tarefa não existente"}


def test_apagar_tarefa():
    """Testa apagar uma tarefa."""
    criar_tarefa_teste()

    resposta = CLIENT.delete("/tarefas/1")
    assert resposta.status_code == 204

    resposta = CLIENT.get("/tarefas/1")
    assert resposta.json() == {"message": "Tarefa não existente"}


def test_apagar_tarefa_inexistente():
    """Testa apagar uma tarefa que não existe."""
    resposta = CLIENT.delete("/tarefas/99")
    assert resposta.status_code == 200
    assert resposta.json() == {"message": "Tarefa não existente"}
