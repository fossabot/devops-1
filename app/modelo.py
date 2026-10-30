"""Modelos da  aplicação de tarefa"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class Tarefa(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    concluida: bool  
    criado_em:  datetime
    concluida_em: Optional[datetime] = None

    def finalizar(self):
        """Finaliza a tarefa"""
        self.concluida = True
        self.concluida_em = datetime.now()