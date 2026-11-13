from flask import Flask

from servicos.sistema import Sistema

# template_folder='view': as páginas HTML ficam em app/view (como no exemplo do professor)
app = Flask(__name__, template_folder="view")
app.secret_key = "estante-trabalho-poo"  # só para a sessão; trabalho acadêmico

sistema = Sistema()

from app import rotas  # noqa: E402  (as rotas precisam do app e do sistema acima)
