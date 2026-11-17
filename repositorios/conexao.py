import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

# Sempre aumentar este número quando as tabelas mudarem e escrever a migração do número anterior.
VERSAO_DO_ESQUEMA = 3

TABELA_COMENTARIOS = """CREATE TABLE IF NOT EXISTS comentarios (
        id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
        livro_id INTEGER NOT NULL REFERENCES livros(id), texto TEXT NOT NULL,
        data TEXT NOT NULL, UNIQUE (usuario_id, livro_id))"""
TABELA_CURTIDAS = """CREATE TABLE IF NOT EXISTS curtidas (
        comentario_id INTEGER NOT NULL REFERENCES comentarios(id) ON DELETE CASCADE,
        usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
        PRIMARY KEY (comentario_id, usuario_id))"""

TABELAS = [
    "CREATE TABLE IF NOT EXISTS generos (id INTEGER PRIMARY KEY, nome TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS editoras (id INTEGER PRIMARY KEY, nome TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS autores (id INTEGER PRIMARY KEY, nome TEXT NOT NULL)",
    """CREATE TABLE IF NOT EXISTS editora_autor (
        editora_id INTEGER NOT NULL REFERENCES editoras(id),
        autor_id INTEGER NOT NULL REFERENCES autores(id),
        PRIMARY KEY (editora_id, autor_id))""",
    """CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY, nome TEXT NOT NULL, ano INTEGER NOT NULL,
        genero_id INTEGER NOT NULL REFERENCES generos(id), sinopse TEXT NOT NULL,
        edicao TEXT NOT NULL, editora_id INTEGER NOT NULL REFERENCES editoras(id),
        autor_id INTEGER NOT NULL REFERENCES autores(id))""",
    """CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY, nome TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL, admin INTEGER NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS estantes (
        id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
        livro_id INTEGER NOT NULL REFERENCES livros(id), lido INTEGER NOT NULL,
        favorito INTEGER NOT NULL, quer_ler INTEGER NOT NULL, UNIQUE (usuario_id, livro_id))""",
    """CREATE TABLE IF NOT EXISTS avaliacoes (
        id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
        livro_id INTEGER NOT NULL REFERENCES livros(id),
        nota INTEGER NOT NULL CHECK (nota BETWEEN 1 AND 5), data TEXT NOT NULL,
        comentario TEXT NOT NULL, UNIQUE (usuario_id, livro_id))""",
    TABELA_COMENTARIOS,
    TABELA_CURTIDAS,
]

TABELAS_COM_ID = {
    "usuarios", "generos", "editoras", "autores", "livros", "estantes", "avaliacoes", "comentarios",
}


class Conexao:
    """Abre o arquivo SQLite uma vez e entrega a mesma conexão aos repositórios."""

    def __init__(self, caminho):
        if caminho != ":memory:":
            Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        self.__trava = threading.RLock()
        self.__em_transacao = False
        self.__caminho = caminho
        # isolation_level=None: quem abre e fecha as transações sou eu (em transacao())
        self.__conexao = sqlite3.connect(caminho, check_same_thread=False, isolation_level=None)
        self.__conexao.row_factory = sqlite3.Row
        self.__conexao.execute("PRAGMA foreign_keys = ON")
        try:
            self.__preparar_banco()
        except Exception:
            self.__conexao.close()
            raise

    def fechar(self):
        self.__conexao.close()

    @contextmanager
    def transacao(self):
        with self.__trava:
            if self.__em_transacao:
                yield
                return
            self.__conexao.execute("BEGIN IMMEDIATE")
            self.__em_transacao = True
            try:
                yield
                self.__conexao.execute("COMMIT")
            except BaseException:
                self.__conexao.execute("ROLLBACK")
                raise
            finally:
                self.__em_transacao = False

    def consultar(self, sql, parametros=()):
        with self.__trava:
            return self.__conexao.execute(sql, parametros).fetchall()

    def executar(self, sql, parametros=()):
        with self.__trava:
            self.__conexao.execute(sql, parametros)

    def proximo_id(self, tabela):
        if tabela not in TABELAS_COM_ID:
            raise ValueError("tabela desconhecida")
        return self.consultar(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {tabela}")[0][0]

    def gravar(self, tabela, valores):
        """Insere a linha. Se o id já existe, atualiza as outras colunas."""
        colunas = ", ".join(valores)
        marcas = ", ".join("?" for _ in valores)
        atualiza = ", ".join(f"{c} = excluded.{c}" for c in valores if c != "id")
        try:
            with self.transacao():
                self.__conexao.execute(
                    f"INSERT INTO {tabela} ({colunas}) VALUES ({marcas}) "
                    f"ON CONFLICT(id) DO UPDATE SET {atualiza}",
                    list(valores.values()),
                )
        except sqlite3.IntegrityError as erro:
            raise ValueError(f"o banco recusou o dado: {erro}") from erro

    def remover(self, tabela, id_linha):
        with self.transacao():
            self.__conexao.execute(f"DELETE FROM {tabela} WHERE id = ?", (id_linha,))

    def __preparar_banco(self):
        with self.transacao():
            versao = self.consultar("PRAGMA user_version")[0][0]
            if versao == 0:
                for comando in TABELAS:
                    self.__conexao.execute(comando)
                self.__conexao.execute(f"PRAGMA user_version = {VERSAO_DO_ESQUEMA}")
            elif versao == 1:
                self.__migrar_da_versao_1()
                self.__migrar_da_versao_2()
            elif versao == 2:
                self.__migrar_da_versao_2()
            elif versao != VERSAO_DO_ESQUEMA:
                raise RuntimeError(
                    f"O banco {self.__caminho} é de uma versão antiga. "
                    "Apague o arquivo para ele ser recriado (as contas criadas nele se perdem)."
                )

    def __migrar_da_versao_1(self):
        """Versão 1 para 2, sem perder contas: aplica as regras novas aos dados que já existem."""
        executar = self.__conexao.execute
        executar("UPDATE estantes SET quer_ler = 0 WHERE lido = 1 AND quer_ler = 1")
        executar("ALTER TABLE comentarios RENAME TO comentarios_v1")
        executar(TABELA_COMENTARIOS)
        executar(TABELA_CURTIDAS)
        executar("""INSERT INTO comentarios SELECT id, usuario_id, livro_id, texto, data
                    FROM comentarios_v1
                    WHERE id IN (SELECT MAX(id) FROM comentarios_v1 GROUP BY usuario_id, livro_id)""")
        executar("DROP TABLE comentarios_v1")
        executar("PRAGMA user_version = 2")

    def __migrar_da_versao_2(self):
        """Versão 2 para 3: autora vira autor, nome genérico, sem perder o catálogo."""
        executar = self.__conexao.execute
        executar("ALTER TABLE autoras RENAME TO autores")
        executar("ALTER TABLE editora_autora RENAME TO editora_autor")
        executar("ALTER TABLE editora_autor RENAME COLUMN autora_id TO autor_id")
        executar("ALTER TABLE livros RENAME COLUMN autora_id TO autor_id")
        executar(f"PRAGMA user_version = {VERSAO_DO_ESQUEMA}")
