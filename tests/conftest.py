"""Configuração compartilhada dos testes"""

import os

os.environ.setdefault("DATABASE_USERNAME", "teste")
os.environ.setdefault("DATABASE_PASSWORD", "teste")
os.environ.setdefault("DATABASE_ADDRESS", "localhost")
os.environ.setdefault("DATABASE", "teste")
