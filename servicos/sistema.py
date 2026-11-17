import os
from pathlib import Path

from repositorios.avaliacao_repositorio import AvaliacaoRepositorio
from repositorios.comentario_repositorio import ComentarioRepositorio
from repositorios.conexao import Conexao
from repositorios.estante_repositorio import EstanteRepositorio
from repositorios.livro_repositorio import LivroRepositorio
from repositorios.usuario_repositorio import UsuarioRepositorio
from servicos.avaliacao_service import AvaliacaoService
from servicos.catalogo_service import CatalogoService
from servicos.conta_service import ContaService
from servicos.estante_service import EstanteService

# o arquivo do banco fica em dados/ (fora do git, cada pessoa tem o seu)
CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / "dados" / "estante.db"


class Sistema:
    """Abre o banco e entrega a cada serviço o repositório da sua entidade."""

    def __init__(self, conexao=None):
        if conexao is None:
            conexao = Conexao(os.environ.get("ESTANTE_DB", CAMINHO_PADRAO))
        usuarios = UsuarioRepositorio(conexao)
        livros = LivroRepositorio(conexao)
        avaliacoes = AvaliacaoRepositorio(conexao, usuarios, livros)
        comentarios = ComentarioRepositorio(conexao, usuarios, livros)
        self.conta = ContaService(usuarios)
        self.catalogo = CatalogoService(livros, avaliacoes)
        self.estante = EstanteService(EstanteRepositorio(conexao, livros))
        self.avaliacao = AvaliacaoService(avaliacoes, comentarios)
