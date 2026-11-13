from repositorios.repositorio_memoria import RepositorioMemoria
from repositorios.repositorio_sqlite import RepositorioSQLite
from repositorios.semente import criar_repositorio


def repo_memoria():
    return criar_repositorio(RepositorioMemoria())


def repo_sqlite():
    return criar_repositorio(RepositorioSQLite(":memory:"))
