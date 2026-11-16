import os
from pathlib import Path

from repositorios.repositorio_sqlite import RepositorioSQLite
from repositorios.semente import criar_repositorio
from servicos.avaliacao_service import AvaliacaoService
from servicos.catalogo_service import CatalogoService
from servicos.conta_service import ContaService
from servicos.estante_service import EstanteService

# o arquivo do banco fica em dados/ (fora do git, cada pessoa tem o seu)
CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / "dados" / "estante.db" # caminho para o banco de dados SQLite, que é um arquivo chamado estante.db localizado na pasta dados, que está no mesmo nível da pasta servicos. O método resolve() retorna o caminho absoluto do arquivo atual (__file__), parent.parent sobe dois níveis na hierarquia de pastas (de servicos para o diretório raiz do projeto), e o operador / é usado para construir o caminho completo para o arquivo estante.db.


class Sistema:
    """Junta o repositório e os serviços. Terminal e Flask usam esta mesma classe."""

    # Sem argumento usa o SQLite (arquivo definido pela variável ESTANTE_DB ou o caminho padrão).
    # Os testes passam um repositório próprio no lugar (injeção de dependência). Injeção de dependência é um padrão de design que permite que uma classe receba suas dependências (como repositórios, serviços, etc.) de fora, em vez de criá-las internamente. Isso facilita a testabilidade e a flexibilidade do código, permitindo que diferentes implementações sejam usadas conforme necessário.
    def __init__(self, repo=None):
        if repo is None:
            repo = RepositorioSQLite(os.environ.get("ESTANTE_DB", CAMINHO_PADRAO))
        repo = criar_repositorio(repo)  # no primeiro uso, enche o banco com a semente
        # Os quatro serviços recebem o MESMO repositório, então enxergam os mesmos dados.
        # Terminal e Flask só precisam de `Sistema()` e usam sistema.conta, .catalogo, .estante, .avaliacao.
        self.conta = ContaService(repo) # 
        self.catalogo = CatalogoService(repo)
        self.estante = EstanteService(repo)
        self.avaliacao = AvaliacaoService(repo)
