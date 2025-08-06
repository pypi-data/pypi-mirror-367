import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.configuration.settings import Configuration
from fastapi.middleware.cors import CORSMiddleware

from src.routes.home import HomeRouter

configuration = Configuration()

def create_app():
    """
    Cria e configura a aplicação FastAPI, incluindo middlewares e rotas.
    """
    app = FastAPI()

    logging.info("Inicializando o banco de dados...")

    if configuration.environment == "production":
        origins = ["https://url_production.com", "https://url_production2.com"]
    else:
        origins = ["http://localhost:3000", "http://localhost:3001"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Configure a montagem dos arquivos estáticos AQUI
    app.mount("/static", StaticFiles(directory="assets"), name="static")
    logging.info("SISTEMA >>> Rota /static montada para servir arquivos estáticos de assets")
        
    app.include_router(HomeRouter())

    return app