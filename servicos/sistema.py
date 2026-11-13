import os
from pathlib import Path

from repositorios.repositorio_sqlite import RepositorioSQLite
from repositorios.semente import criar_repositorio
from servicos.avaliacao_service import AvaliacaoService
from servicos.catalogo_service import CatalogoService
from servicos.conta_service import ContaService
from servicos.estante_service import EstanteService

# o arquivo do banco fica em dados/ (fora do git, cada pessoa tem o seu)
CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / "dados" / "estante.db"


class Sistema:
    """Junta o repositório e os serviços. Terminal e Flask usam esta mesma classe."""

    def __init__(self, repo=None):
        if repo is None:
            repo = RepositorioSQLite(os.environ.get("ESTANTE_DB", CAMINHO_PADRAO))
        repo = criar_repositorio(repo)  # no primeiro uso, enche o banco com a semente
        self.conta = ContaService(repo)
        self.catalogo = CatalogoService(repo)
        self.estante = EstanteService(repo)
        self.avaliacao = AvaliacaoService(repo)
