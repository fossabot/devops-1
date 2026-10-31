"""Modelos da  aplicação de tarefa"""

from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class Tarefa(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    descricao: Optional[str] = None
    concluida: bool  
    criado_em:  datetime
    concluida_em: Optional[datetime] = None

    def finalizar(self):
        """Finaliza a tarefa"""
        self.concluida = True
        self.concluida_em = datetime.now(timezone.utc)