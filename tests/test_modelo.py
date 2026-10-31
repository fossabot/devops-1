"""Teste dos modelos"""

from datetime import datetime, timezone

from app.modelo import Tarefa


def criar_tarefa_mock(agora: datetime | None):
    """Cria uma tarefa padrão para os testes."""
    return Tarefa(id=0,
                  titulo="Tarefa Teste",
                  concluida=False,
                  criado_em=agora or datetime.now(timezone.utc))


def test_nova_tarefa():
    """Cria uma tarefa e verifica os campos."""
    agora = datetime.now(timezone.utc)
    t = criar_tarefa_mock(agora)
    assert t.id == 0
    assert t.titulo == "Tarefa Teste"
    assert t.descricao is None
    assert t.concluida is False
    assert t.criado_em == agora
    assert t.concluida_em is None


def test_finalizada():
    """Testa se a tarefa foi finalizada."""
    t = criar_tarefa_mock(None)

    t.finalizar()

    assert t.concluida is True
    assert isinstance(t.concluida_em, datetime)
    assert t.concluida_em >= t.criado_em
