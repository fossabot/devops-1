import pytest
from fastapi.testclient import TestClient

import app
from app import APP

CLIENT = TestClient(APP)


@pytest.fixture(autouse=True)
def preparar(monkeypatch):
    # Limpa as tarefas antes de cada teste
    app.TAREFAS.clear()
    # Substitui o notificar por uma função que não faz nada
    monkeypatch.setattr(app, "notificar", lambda mensagem: None)


def criar_tarefa_teste():
    return CLIENT.post("/tarefas", params={"titulo": "Estudar", "descricao": "Aprender FastAPI"})


def test_index():
    resposta = CLIENT.get("/")
    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Olá, mundo!"}


def test_autor():
    resposta = CLIENT.get("/autor")
    assert resposta.status_code == 200
    assert resposta.json() == {"message": "Leandro Willian Fraccaroli"}


def test_tarefas():
    resposta = CLIENT.get("/tarefas")
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_post_tarefas():
    resposta = criar_tarefa_teste()
    assert resposta.status_code == 200
    assert resposta.json() == {"message": "ok"}

    tarefas = CLIENT.get("/tarefas").json()
    assert len(tarefas) == 1
    assert tarefas[0]["titulo"] == "Estudar"
    assert tarefas[0]["descricao"] == "Aprender FastAPI"
    assert tarefas[0]["concluida"] is False


def test_tarefa_especifica():
    criar_tarefa_teste()

    resposta = CLIENT.get("/tarefas/0")
    assert resposta.status_code == 200
    assert resposta.json()["id"] == 0
    assert resposta.json()["titulo"] == "Estudar"


def test_tarefa_especifica_inexistente():
    resposta = CLIENT.get("/tarefas/99")
    assert resposta.json() == {"message": "Tarefa não existente"}


def test_concluir_tarefa():
    criar_tarefa_teste()

    resposta = CLIENT.put("/tarefas/0")
    assert resposta.status_code == 200
    assert resposta.json()["concluida"] is True
    assert resposta.json()["concluida_em"] is not None


def test_concluir_tarefa_ja_concluida():
    criar_tarefa_teste()
    CLIENT.put("/tarefas/0")

    resposta = CLIENT.put("/tarefas/0")
    assert resposta.json() == {"message": "Atarefa já está concluida"}

def test_concluir_tarefa_inexistente():
    resposta = CLIENT.put("/tarefas/99")
    assert resposta.status_code == 200
    assert resposta.json() == {"message": "Tarefa não existente"}


def test_apagar_tarefa():
    criar_tarefa_teste()

    resposta = CLIENT.delete("/tarefas/0")
    assert resposta.status_code == 204

    resposta = CLIENT.get("/tarefas/0")
    assert resposta.json() == {"message": "Tarefa não existente"}

def test_apagar_tarefa_inexistente():
    resposta = CLIENT.delete("/tarefas/99")
    assert resposta.status_code == 200
    assert resposta.json() == {"message": "Tarefa não existente"}