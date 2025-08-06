import logging
import os
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Carrega as variáveis de ambiente
load_dotenv(dotenv_path=".env", encoding="utf-8")

# Silencia logs de SQLAlchemy
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

class Configuration:
    def __init__(self):
        
        # URL BASE - FRONTEND
        self.base_url_web = os.getenv("BASE_URL_WEB", "http://localhost:3000")
        
        # Configurações do ambiente e banco de dados
        self.environment = os.getenv("ENVIRONMENT", "development").lower()
    