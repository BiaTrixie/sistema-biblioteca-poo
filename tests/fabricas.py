import unittest

from repositorios.repositorio_memoria import RepositorioMemoria
from repositorios.repositorio_sqlite import RepositorioSQLite
from repositorios.semente import criar_repositorio


def repo_memoria():
    return criar_repositorio(RepositorioMemoria())


def repo_sqlite():
    repo = RepositorioSQLite(":memory:")
    unittest.addModuleCleanup(repo.fechar)  # fecha a conexão quando o arquivo de testes terminar
    return criar_repositorio(repo)
