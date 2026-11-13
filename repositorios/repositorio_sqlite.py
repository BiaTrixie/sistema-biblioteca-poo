import sqlite3
import threading
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from modelos.autora import Autora
from modelos.avaliacao import Avaliacao
from modelos.comentario import Comentario
from modelos.editora import Editora
from modelos.estante import Estante
from modelos.genero import Genero
from modelos.livro import Livro
from modelos.usuario import Usuario
from repositorios.repositorio import COLECAO_DE, Repositorio

# Suba este número quando as tabelas mudarem; um arquivo antigo é recusado com um aviso.
VERSAO_DO_ESQUEMA = 1

TABELAS = [
    "CREATE TABLE IF NOT EXISTS generos (id INTEGER PRIMARY KEY, nome TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS editoras (id INTEGER PRIMARY KEY, nome TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS autoras (id INTEGER PRIMARY KEY, nome TEXT NOT NULL)",
    """CREATE TABLE IF NOT EXISTS editora_autora (
        editora_id INTEGER NOT NULL REFERENCES editoras(id),
        autora_id INTEGER NOT NULL REFERENCES autoras(id),
        PRIMARY KEY (editora_id, autora_id))""",
    """CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY, nome TEXT NOT NULL, ano INTEGER NOT NULL,
        genero_id INTEGER NOT NULL REFERENCES generos(id), sinopse TEXT NOT NULL,
        edicao TEXT NOT NULL, editora_id INTEGER NOT NULL REFERENCES editoras(id),
        autora_id INTEGER NOT NULL REFERENCES autoras(id))""",
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
    """CREATE TABLE IF NOT EXISTS comentarios (
        id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
        livro_id INTEGER NOT NULL REFERENCES livros(id), texto TEXT NOT NULL,
        data TEXT NOT NULL, numero_likes INTEGER NOT NULL)""",
]

# como cada objeto vira uma linha da tabela (colunas e valores)
PARA_LINHA = {
    Usuario: lambda u: {"id": u.id, "nome": u.nome, "email": u.email,
                        "senha": u.senha_protegida, "admin": int(u.admin)},
    Genero: lambda g: {"id": g.id, "nome": g.nome},
    Editora: lambda e: {"id": e.id, "nome": e.nome},
    Autora: lambda a: {"id": a.id, "nome": a.nome},
    Livro: lambda l: {"id": l.id, "nome": l.nome, "ano": l.ano, "genero_id": l.genero.id,
                      "sinopse": l.sinopse, "edicao": l.edicao,
                      "editora_id": l.editora.id, "autora_id": l.autora.id},
    Estante: lambda e: {"id": e.id, "usuario_id": e.usuario.id, "livro_id": e.livro.id,
                        "lido": int(e.lido), "favorito": int(e.favorito), "quer_ler": int(e.quer_ler)},
    Avaliacao: lambda a: {"id": a.id, "usuario_id": a.usuario.id, "livro_id": a.livro.id,
                          "nota": a.nota, "data": a.data.isoformat(), "comentario": a.comentario},
    Comentario: lambda c: {"id": c.id, "usuario_id": c.usuario.id, "livro_id": c.livro.id,
                           "texto": c.texto, "data": c.data.isoformat(), "numero_likes": c.numero_likes},
}

CATALOGO = (Genero, Editora, Autora, Livro)  # nunca mudam com o programa rodando


class RepositorioSQLite(Repositorio):
    """Guarda tudo num arquivo SQLite, então os dados sobrevivem ao fechar o programa.

    O catálogo (livros, gêneros, editoras, autoras) é lido uma vez e fica em memória.
    Usuários, estantes, avaliações e comentários são lidos do banco a cada consulta,
    para o terminal e o Flask sempre enxergarem os dados mais novos um do outro."""

    def __init__(self, caminho):
        if caminho != ":memory:":
            Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        self.__trava = threading.RLock()  # o Flask atende em várias threads
        self.__em_transacao = False
        self.__catalogo = None
        # isolation_level=None: quem abre e fecha as transações sou eu (em transacao())
        self.__conexao = sqlite3.connect(caminho, check_same_thread=False, isolation_level=None)
        self.__conexao.row_factory = sqlite3.Row
        self.__conexao.execute("PRAGMA foreign_keys = ON")
        try:
            self.__preparar_banco(caminho)
        except Exception:
            self.__conexao.close()  # não deixa a conexão aberta se o arquivo for recusado
            raise

    def fechar(self):
        self.__conexao.close()

    # --- infraestrutura ---

    @contextmanager
    def transacao(self):
        with self.__trava:
            if self.__em_transacao:  # já estamos dentro de uma: só deixa passar
                yield
                return
            self.__conexao.execute("BEGIN IMMEDIATE")  # reserva a escrita já no início
            self.__em_transacao = True
            try:
                yield
                self.__conexao.execute("COMMIT")
            except BaseException:
                self.__conexao.execute("ROLLBACK")
                raise
            finally:
                self.__em_transacao = False

    def __consultar(self, sql, parametros=()):
        with self.__trava:
            return self.__conexao.execute(sql, parametros).fetchall()

    def __preparar_banco(self, caminho):
        with self.transacao():
            versao = self.__consultar("PRAGMA user_version")[0][0]
            if versao == 0:  # arquivo novo
                for comando in TABELAS:
                    self.__conexao.execute(comando)
                self.__conexao.execute(f"PRAGMA user_version = {VERSAO_DO_ESQUEMA}")
            elif versao != VERSAO_DO_ESQUEMA:
                raise RuntimeError(
                    f"O banco {caminho} é de uma versão antiga. "
                    "Apague o arquivo para ele ser recriado (as contas criadas nele se perdem)."
                )

    # --- escrita ---

    def proximo_id(self, colecao):
        if colecao not in COLECAO_DE.values():
            raise ValueError("coleção desconhecida")
        return self.__consultar(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {colecao}")[0][0]

    def salvar(self, objeto):
        tabela = COLECAO_DE[type(objeto)]
        valores = PARA_LINHA[type(objeto)](objeto)
        colunas = ", ".join(valores)
        marcas = ", ".join("?" for _ in valores)
        atualiza = ", ".join(f"{c} = excluded.{c}" for c in valores if c != "id")
        try:
            with self.transacao():
                # insere se o id é novo; se já existe, atualiza as colunas
                self.__conexao.execute(
                    f"INSERT INTO {tabela} ({colunas}) VALUES ({marcas}) "
                    f"ON CONFLICT(id) DO UPDATE SET {atualiza}",
                    list(valores.values()),
                )
                if isinstance(objeto, Editora):  # a ligação editora-autora tem tabela própria
                    for autora in objeto.autores:
                        self.__conexao.execute(
                            "INSERT OR IGNORE INTO editora_autora VALUES (?, ?)", (objeto.id, autora.id)
                        )
        except sqlite3.IntegrityError as erro:
            raise ValueError(f"o banco recusou o dado: {erro}") from erro
        if isinstance(objeto, CATALOGO):
            self.__catalogo = None  # o catálogo mudou: relê na próxima consulta

    def remover(self, objeto):
        with self.transacao():
            self.__conexao.execute(f"DELETE FROM {COLECAO_DE[type(objeto)]} WHERE id = ?", (objeto.id,))

    def esta_vazio(self):
        return self.__consultar("SELECT COUNT(*) FROM livros")[0][0] == 0

    # --- catálogo (em memória depois da primeira leitura) ---

    def __ler_catalogo(self):
        if self.__catalogo is None:
            generos = {r["id"]: Genero(r["id"], r["nome"])
                       for r in self.__consultar("SELECT * FROM generos ORDER BY id")}
            editoras = {r["id"]: Editora(r["id"], r["nome"])
                        for r in self.__consultar("SELECT * FROM editoras ORDER BY id")}
            autoras = {r["id"]: Autora(r["id"], r["nome"])
                       for r in self.__consultar("SELECT * FROM autoras ORDER BY id")}
            for r in self.__consultar("SELECT * FROM editora_autora"):
                editoras[r["editora_id"]].adicionar_autora(autoras[r["autora_id"]])
                autoras[r["autora_id"]].adicionar_editora(editoras[r["editora_id"]])
            livros = {
                r["id"]: Livro(r["id"], r["nome"], r["ano"], generos[r["genero_id"]], r["sinopse"],
                               r["edicao"], editoras[r["editora_id"]], autoras[r["autora_id"]])
                for r in self.__consultar("SELECT * FROM livros ORDER BY id")
            }
            self.__catalogo = {"generos": generos, "editoras": editoras, "livros": livros}
        return self.__catalogo

    def listar_livros(self):
        return list(self.__ler_catalogo()["livros"].values())

    def buscar_livro(self, id_livro):
        return self.__ler_catalogo()["livros"].get(id_livro)

    def listar_generos(self):
        return list(self.__ler_catalogo()["generos"].values())

    def listar_editoras(self):
        return list(self.__ler_catalogo()["editoras"].values())

    # --- usuários ---

    def __para_usuario(self, linha):
        # protegida=True: a senha da linha já é um hash
        return Usuario(linha["id"], linha["nome"], linha["email"], linha["senha"],
                       bool(linha["admin"]), protegida=True)

    def __usuarios_por_id(self):
        return {r["id"]: self.__para_usuario(r) for r in self.__consultar("SELECT * FROM usuarios")}

    def buscar_usuario(self, id_usuario):
        linhas = self.__consultar("SELECT * FROM usuarios WHERE id = ?", (id_usuario,))
        return self.__para_usuario(linhas[0]) if linhas else None

    def buscar_usuario_por_email(self, email):
        email = str(email).strip().lower()
        linhas = self.__consultar("SELECT * FROM usuarios WHERE email = ?", (email,))
        return self.__para_usuario(linhas[0]) if linhas else None

    # --- estante ---

    def __para_registro(self, linha, usuario):
        livro = self.__ler_catalogo()["livros"][linha["livro_id"]]
        return Estante(linha["id"], usuario, livro, favorito=bool(linha["favorito"]),
                       quer_ler=bool(linha["quer_ler"]), lido=bool(linha["lido"]))

    def buscar_registro(self, usuario, livro):
        linhas = self.__consultar(
            "SELECT * FROM estantes WHERE usuario_id = ? AND livro_id = ?", (usuario.id, livro.id)
        )
        return self.__para_registro(linhas[0], usuario) if linhas else None

    def listar_registros(self, usuario):
        linhas = self.__consultar("SELECT * FROM estantes WHERE usuario_id = ? ORDER BY id", (usuario.id,))
        return [self.__para_registro(linha, usuario) for linha in linhas]

    # --- avaliações e comentários ---

    def __filtrar_por_livro(self, tabela, livro):
        if livro is None:
            return self.__consultar(f"SELECT * FROM {tabela} ORDER BY id")
        return self.__consultar(f"SELECT * FROM {tabela} WHERE livro_id = ? ORDER BY id", (livro.id,))

    def __para_avaliacao(self, linha, usuario, livro):
        return Avaliacao(linha["id"], linha["nota"], date.fromisoformat(linha["data"]),
                         usuario, livro, linha["comentario"])

    def __para_comentario(self, linha, usuario, livro):
        return Comentario(linha["id"], linha["texto"], date.fromisoformat(linha["data"]),
                          usuario, livro, linha["numero_likes"])

    def buscar_avaliacao(self, usuario, livro):
        linhas = self.__consultar(
            "SELECT * FROM avaliacoes WHERE usuario_id = ? AND livro_id = ?", (usuario.id, livro.id)
        )
        return self.__para_avaliacao(linhas[0], usuario, livro) if linhas else None

    def listar_avaliacoes(self, livro=None):
        usuarios, livros = self.__usuarios_por_id(), self.__ler_catalogo()["livros"]
        return [self.__para_avaliacao(r, usuarios[r["usuario_id"]], livros[r["livro_id"]])
                for r in self.__filtrar_por_livro("avaliacoes", livro)]

    def buscar_comentario(self, id_comentario):
        linhas = self.__consultar("SELECT * FROM comentarios WHERE id = ?", (id_comentario,))
        if not linhas:
            return None
        usuario = self.buscar_usuario(linhas[0]["usuario_id"])
        return self.__para_comentario(linhas[0], usuario, self.buscar_livro(linhas[0]["livro_id"]))

    def listar_comentarios(self, livro=None):
        usuarios, livros = self.__usuarios_por_id(), self.__ler_catalogo()["livros"]
        return [self.__para_comentario(r, usuarios[r["usuario_id"]], livros[r["livro_id"]])
                for r in self.__filtrar_por_livro("comentarios", livro)]
