from pathlib import Path

from flask import Flask

from servicos.sistema import Sistema

PASTA_APP = Path(__file__).resolve().parent.parent / "app"
app = Flask(
    __name__,
    template_folder=str(PASTA_APP / "view"),
    static_folder=str(PASTA_APP / "static"),
)
sistema = Sistema()

from api.rotas import api  
from app.paginas import paginas  

app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(paginas)
