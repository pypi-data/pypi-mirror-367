from sqlmodel import Session
from src.configuration.settings import Configuration

# Carregar configuração global
configuration = Configuration()

def populate_database(session: Session):
    """Inicializa o banco de dados e popula com dados iniciais."""
    pass


