from repositorios.semente import criar_repositorio
from servicos.avaliacao_service import AvaliacaoService
from servicos.catalogo_service import CatalogoService
from servicos.conta_service import ContaService
from servicos.estante_service import EstanteService


class Sistema:
    """Junta o repositório e os serviços. Terminal e Flask usam esta mesma classe."""

    def __init__(self):
        repo = criar_repositorio()
        self.conta = ContaService(repo)
        self.catalogo = CatalogoService(repo)
        self.estante = EstanteService(repo)
        self.avaliacao = AvaliacaoService(repo)
