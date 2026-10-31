"""Modelos da aplicação de tarefa"""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Tarefa(SQLModel, table=True):
    """Representa uma tarefa."""
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    descricao: Optional[str] = None
    concluida: bool = False
    criado_em: datetime
    concluida_em: Optional[datetime] = None

    def finalizar(self):
        """Finaliza a tarefa."""
        self.concluida = True
        self.concluida_em = datetime.now(timezone.utc)