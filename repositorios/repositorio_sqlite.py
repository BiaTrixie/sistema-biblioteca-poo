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

# Suba este número quando as tabelas mudarem e escreva a migração do número anterior.
VERSAO_DO_ESQUEMA = 2

# --------------- Nessa primeira etapa, temos a criação das tabelas do banco. É o shcema do banco, escrito em DDL -----------------------------------------------------

# um comentário por pessoa e livro; quem curtiu fica numa tabela própria (uma linha por pessoa)

# POR QUE estas duas tabelas ficam fora da lista TABELAS (mais abaixo)?
# Porque o mesmo SQL é usado em DOIS lugares, e uma variável com nome evita copiar e colar o texto:
#   1) em TABELAS, quando o banco é novo (__preparar_banco, versão 0);
#   2) em __migrar_da_versao_1, que recria "comentarios" e "curtidas" no formato novo
#      depois de renomear a tabela antiga para comentarios_v1.
# Se o SQL ficasse só dentro da lista, a migração teria de repetir o texto, e uma mudança
# numa cópia esqueceria a outra. As demais tabelas só são criadas no caso 1, então ficam direto na lista.
#
# O QUE SÃO as aspas triplas (""" ... """)?
# São uma string de várias linhas. Com aspas simples ("...") o texto precisa caber em uma linha;
# com """ ... """ o texto pode ocupar várias linhas, e as quebras e os espaços ficam como foram escritos.
# Aqui serve para escrever o comando SQL CREATE TABLE legível, uma coluna por linha, e passá-lo
# inteiro ao banco (self.__conexao.execute). O mesmo recurso é usado dentro de TABELAS.

TABELA_COMENTARIOS = """CREATE TABLE IF NOT EXISTS comentarios ( 
        id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
        livro_id INTEGER NOT NULL REFERENCES livros(id), texto TEXT NOT NULL,
        data TEXT NOT NULL, UNIQUE (usuario_id, livro_id))"""
TABELA_CURTIDAS = """CREATE TABLE IF NOT EXISTS curtidas (
        comentario_id INTEGER NOT NULL REFERENCES comentarios(id) ON DELETE CASCADE,
        usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
        PRIMARY KEY (comentario_id, usuario_id))"""

# O SQL que cria cada tabela. Pontos para entender:
# - REFERENCES = chave estrangeira (livros.genero_id aponta para generos.id);
# - UNIQUE (usuario_id, livro_id) = a mesma pessoa não repete registro para o mesmo livro;
# - editora_autora é uma tabela só de ligação (relação muitos-para-muitos);
# - CHECK (nota BETWEEN 1 AND 5) = o próprio banco recusa nota inválida.
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
    TABELA_COMENTARIOS,
    TABELA_CURTIDAS,
]

# como cada objeto vira uma linha da tabela (colunas e valores)
PARA_LINHA = {
    Usuario: lambda u: {"id": u.id, "nome": u.nome, "email": u.email, # u é o objeto da classe Usuario, e a função lambda retorna um dicionário com as chaves correspondentes aos nomes das colunas da tabela usuarios e os valores correspondentes aos atributos do objeto u. A senha é protegida (hash) e não é armazenada em texto puro, por isso o atributo senha_protegida é usado para obter o hash da senha.
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
                           "texto": c.texto, "data": c.data.isoformat()},
}

CATALOGO = (Genero, Editora, Autora, Livro)  # essas classes são lidas do banco uma vez e ficam em memória, para não precisar ficar consultando o banco toda hora. Já que essas informações não mudam com frequência e principalmente não enquanto o programa roda.


# ---------------------------------------- Aqui temos a classe RepositorioSQLite, que é filha da classe Repositorio e implementa o contrato guardando os dados em um arquivo SQLite. O serviço chama os mesmos métodos que chamaria na versão em memória (polimorfismo). ----------------------------------------

# Filha de Repositorio: implementa o contrato guardando num arquivo SQLite.
# O serviço chama os mesmos métodos que chamaria na versão em memória (polimorfismo).
class RepositorioSQLite(Repositorio):
    """Guarda tudo num arquivo SQLite, então os dados sobrevivem ao fechar o programa.

    O catálogo (livros, gêneros, editoras, autoras) é lido uma vez e fica em memória.
    Usuários, estantes, avaliações e comentários são lidos do banco a cada consulta,
    para o terminal e o Flask sempre enxergarem os dados mais novos um do outro."""



# ----------------------------- Nessa primeira parte, ainda nao temos a implementação dos métodos de repositorio.py, apenas as definições do banco sqlite -------------------------------------------
    # Abre (ou cria) o arquivo do banco e deixa as tabelas prontas. ":memory:" cria um banco
    # temporário só na memória, usado nos testes.
    def __init__(self, caminho):
        if caminho != ":memory:":
            Path(caminho).parent.mkdir(parents=True, exist_ok=True)

        self.__trava = threading.RLock()  # o Flask atende em várias threads. Threads são como "mini-programas" que rodam ao mesmo tempo dentro do mesmo programa. O RLock impede duas threads de gravarem ao mesmo tempo, evitando que o banco fique corrompido.
        self.__em_transacao = False # transação se refere a um grupo de operações de gravação no banco de dados que devem ser tratadas como uma única unidade. Se uma operação falhar, todas as operações dentro da transação são revertidas, garantindo a consistência dos dados. A variável __em_transacao indica se o repositório está atualmente dentro de uma transação. Se for True, significa que uma transação foi iniciada e ainda não foi concluída (comitada ou revertida). Se for False, significa que não há transação em andamento.
        self.__catalogo = None
        # isolation_level=None: quem abre e fecha as transações sou eu (em transacao())
        self.__conexao = sqlite3.connect(caminho, check_same_thread=False, isolation_level=None) # cria a conexão com o banco.
        self.__conexao.row_factory = sqlite3.Row
        self.__conexao.execute("PRAGMA foreign_keys = ON") # habilita as chaves estrangeiras no SQLite, garantindo que as restrições de integridade referencial sejam aplicadas. Isso significa que, por exemplo, não será possível inserir um registro em uma tabela que faça referência a um registro inexistente em outra tabela. O PRAGMA foreign_keys = ON é necessário porque, por padrão, o SQLite não aplica essas restrições.
        try:
            self.__preparar_banco(caminho)
        except Exception:
            self.__conexao.close()  # não deixa a conexão aberta se o arquivo for recusado
            raise

    # Fecha a conexão com o arquivo.
    def fechar(self):
        self.__conexao.close()

    # Parte técnica, que os serviços nunca chamam direto: transação, consulta e preparação do banco.
    # --- infraestrutura ---

    # Transação = grupo de gravações em que ou entram todas ou nenhuma. Gravações em um banco de dados.
    # BEGIN abre, COMMIT confirma, ROLLBACK desfaz tudo se der erro no meio.
    # Se já estamos dentro de uma transação (ex.: `salvar` chamado dentro da semente), só deixa passar.
    # O RLock impede duas threads do Flask de gravarem ao mesmo tempo.
    @contextmanager # contextmanager é um decorador que transforma uma função em um gerenciador de contexto, permitindo que seja usada com a instrução with. Ele simplifica o gerenciamento de recursos, como arquivos ou conexões de banco de dados, garantindo que sejam corretamente abertos e fechados, mesmo em caso de erros.

    def transacao(self): #função transacao é um gerenciador de contexto que permite agrupar várias operações de gravação em uma única transação. Quando usada com a instrução with, ela inicia uma transação no banco de dados SQLite, permitindo que todas as operações dentro do bloco with sejam tratadas como uma única unidade. Se todas as operações forem bem-sucedidas, a transação é confirmada (COMMIT). Se ocorrer algum erro durante as operações, a transação é revertida (ROLLBACK), garantindo que nenhuma alteração parcial seja aplicada ao banco de dados.
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

    # Roda um SELECT e devolve todas as linhas. Os "?" do SQL são preenchidos por `parametros`,
    # o que evita SQL injection (nunca se monta o SQL juntando o texto do usuário).
    def __consultar(self, sql, parametros=()):
        with self.__trava:
            return self.__conexao.execute(sql, parametros).fetchall()

    # PRAGMA user_version guarda a versão do esquema dentro do próprio arquivo:
    # 0 = arquivo novo (cria as tabelas); 1 = versão antiga (migra); igual à atual = não faz nada;
    # qualquer outra = erro, pedindo para apagar o arquivo.
    
    def __preparar_banco(self, caminho):
        with self.transacao():
            versao = self.__consultar("PRAGMA user_version")[0][0]
            if versao == 0:  # arquivo novo
                for comando in TABELAS:
                    self.__conexao.execute(comando)
                self.__conexao.execute(f"PRAGMA user_version = {VERSAO_DO_ESQUEMA}")
            elif versao == 1:
                self.__migrar_da_versao_1()
            elif versao != VERSAO_DO_ESQUEMA:
                raise RuntimeError(
                    f"O banco {caminho} é de uma versão antiga. "
                    "Apague o arquivo para ele ser recriado (as contas criadas nele se perdem)."
                )

    # MIGRAÇÃO = levar um banco criado numa versão antiga do esquema para a versão atual,
    # SEM perder os dados que já estão nele (contas, estantes, avaliações...).
    # Esta função cobre um único salto: versão 1 -> versão 2. Ela só é chamada por
    # __preparar_banco, quando o PRAGMA user_version do arquivo vale 1.
    #
    # O que mudou da versão 1 para a 2 (duas regras de negócio novas):
    #   a) na estante, "lido" e "quero ler" não podem valer ao mesmo tempo;
    #   b) cada pessoa tem UM comentário por livro, e as curtidas passam a guardar QUEM curtiu.
    #
    # Atomicidade: __preparar_banco chama esta função dentro de "with self.transacao()".
    # Se qualquer comando abaixo falhar, o ROLLBACK desfaz TUDO e o arquivo continua na versão 1,
    # intacto. Por isso não há tratamento de erro aqui dentro.
    #
    # Importante: o corpo desta função NÃO deve ser editado depois de publicada. Quem ainda
    # está na versão 1 precisa do mesmo comportamento. Uma mudança futura vira uma migração nova.
    def __migrar_da_versao_1(self):
        """Versão 1 para 2, sem perder contas: aplica as regras novas aos dados que já existem."""
        # atalho: "executar(sql)" é o mesmo que "self.__conexao.execute(sql)"
        executar = self.__conexao.execute

        # --- Passo 1: regra (a), na tabela "estantes" -------------------------------------
        # Linhas antigas podem ter lido = 1 e quer_ler = 1 ao mesmo tempo, o que agora é
        # inválido (Estante lança ValueError ao carregar). Quem já leu não "quer ler",
        # então zeramos quer_ler só nessas linhas e preservamos o lido.
        executar("UPDATE estantes SET quer_ler = 0 WHERE lido = 1 AND quer_ler = 1")

        # --- Passo 2: regra (b), na tabela "comentarios" ----------------------------------
        # O formato da tabela mudou (colunas e restrição UNIQUE), e SQLite não altera isso
        # com facilidade. A técnica é "renomear, recriar, copiar, descartar":
        #
        # 2.1) Renomeia a tabela velha, para o nome "comentarios" ficar livre.
        executar("ALTER TABLE comentarios RENAME TO comentarios_v1")
        # 2.2) Cria as tabelas no formato NOVO. Reaproveita as mesmas constantes usadas ao criar
        #      um banco do zero (é por isso que elas ficam fora da lista TABELAS), então o banco
        #      migrado e o banco novo ficam idênticos. A "curtidas" também é nova: na versão 1
        #      as curtidas eram só um número dentro de "comentarios".
        executar(TABELA_COMENTARIOS)
        executar(TABELA_CURTIDAS)
        # 2.3) Copia os dados aproveitáveis. A tabela nova tem UNIQUE (usuario_id, livro_id),
        #      mas a velha podia ter vários comentários da mesma pessoa no mesmo livro.
        #      O subSELECT agrupa por (usuario_id, livro_id) e pega o MAIOR id de cada grupo.
        #      Como o id cresce com o tempo, o maior id é o comentário mais novo, o que fica.
        #      As curtidas antigas se perdem: eram só um número, sem dizer de quem, e a
        #      tabela nova precisa de uma linha por pessoa.
        executar("""INSERT INTO comentarios SELECT id, usuario_id, livro_id, texto, data
                    FROM comentarios_v1
                    WHERE id IN (SELECT MAX(id) FROM comentarios_v1 GROUP BY usuario_id, livro_id)""")
        # 2.4) A cópia velha já cumpriu o papel: remove.
        executar("DROP TABLE comentarios_v1")

        # --- Passo 3: carimbar a versão ---------------------------------------------------
        # Sem isso, na próxima abertura o programa acharia que o arquivo ainda é da versão 1
        # e tentaria migrar de novo (e quebraria). user_version fica gravado dentro do arquivo.
        executar(f"PRAGMA user_version = {VERSAO_DO_ESQUEMA}")





    # Aqui começam os métodos do contrato Repositorio (explicados em repositorio.py).
    # --- escrita ---

    # O nome da tabela vai direto no SQL (tabela não aceita "?"), por isso antes se confere
    # que ele é um dos nomes conhecidos. COALESCE(MAX(id), 0) + 1 = maior id + 1, ou 1 se a tabela está vazia.
    def proximo_id(self, colecao):
        if colecao not in COLECAO_DE.values():
            raise ValueError("coleção desconhecida")
        return self.__consultar(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {colecao}")[0][0]

    # 1) PARA_LINHA[tipo] converte o objeto em {coluna: valor}.
    # 2) INSERT ... ON CONFLICT(id) DO UPDATE = "upsert": insere se o id é novo, atualiza se já existe.
    # 3) Comentário e Editora têm tabelas extras (curtidas, editora_autora), gravadas na mesma transação.
    # 4) IntegrityError (ex.: UNIQUE violado) vira ValueError, que o resto do sistema já sabe tratar.
    # 5) Se o catálogo mudou, descarta o cache para reler do banco na próxima consulta.
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
                if isinstance(objeto, Comentario):  # quem curtiu: apaga e regrava a lista
                    self.__conexao.execute("DELETE FROM curtidas WHERE comentario_id = ?", (objeto.id,))
                    for id_usuario in objeto.curtidas:
                        self.__conexao.execute("INSERT INTO curtidas VALUES (?, ?)", (objeto.id, id_usuario))
                if isinstance(objeto, Editora):  # a ligação editora-autora tem tabela própria
                    for autora in objeto.autores:
                        self.__conexao.execute(
                            "INSERT OR IGNORE INTO editora_autora VALUES (?, ?)", (objeto.id, autora.id)
                        )
        except sqlite3.IntegrityError as erro:
            raise ValueError(f"o banco recusou o dado: {erro}") from erro
        if isinstance(objeto, CATALOGO):
            self.__catalogo = None  # o catálogo mudou: relê na próxima consulta

    # DELETE pela chave primária. As curtidas somem junto por causa do ON DELETE CASCADE.
    def remover(self, objeto):
        with self.transacao():
            self.__conexao.execute(f"DELETE FROM {COLECAO_DE[type(objeto)]} WHERE id = ?", (objeto.id,))

    def esta_vazio(self):
        return self.__consultar("SELECT COUNT(*) FROM livros")[0][0] == 0




    # --- catálogo (em memória depois da primeira leitura) ---

    # Lê gêneros, editoras, autoras e livros UMA vez e guarda em memória (self.__catalogo).
    # Usa dicionários {id: objeto} para montar o Livro já apontando para os objetos certos.
    # O catálogo não muda com o programa rodando, então não precisa reler a cada consulta.
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

    # Os métodos do catálogo só olham o cache montado por __ler_catalogo.
    def listar_livros(self):
        return list(self.__ler_catalogo()["livros"].values())

    def buscar_livro(self, id_livro):
        return self.__ler_catalogo()["livros"].get(id_livro)

    def listar_generos(self):
        return list(self.__ler_catalogo()["generos"].values())

    def listar_editoras(self):
        return list(self.__ler_catalogo()["editoras"].values())

    # --- usuários ---

    # "__para_*" fazem o caminho inverso de PARA_LINHA: transformam uma linha do banco em objeto.
    def __para_usuario(self, linha):
        # senha_protegida=True: a senha da linha já é um hash
        return Usuario(linha["id"], linha["nome"], linha["email"], linha["senha"],
                       bool(linha["admin"]), senha_protegida=True)

    # Todos os usuários num dicionário {id: Usuario}, para consulta rápida ao montar listas.
    def __usuarios_por_id(self):
        return {r["id"]: self.__para_usuario(r) for r in self.__consultar("SELECT * FROM usuarios")}

    # Se a consulta não achou linha nenhuma, devolve None.
    def buscar_usuario(self, id_usuario):
        linhas = self.__consultar("SELECT * FROM usuarios WHERE id = ?", (id_usuario,))
        return self.__para_usuario(linhas[0]) if linhas else None

    def buscar_usuario_por_email(self, email):
        email = str(email).strip().lower()
        linhas = self.__consultar("SELECT * FROM usuarios WHERE email = ?", (email,))
        return self.__para_usuario(linhas[0]) if linhas else None

    # --- estante ---

    # A linha só guarda o livro_id: o objeto Livro vem do catálogo em memória.
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

    # Sem livro (None) traz a tabela inteira; com livro, só as linhas desse livro.
    def __filtrar_por_livro(self, tabela, livro):
        if livro is None:
            return self.__consultar(f"SELECT * FROM {tabela} ORDER BY id")
        return self.__consultar(f"SELECT * FROM {tabela} WHERE livro_id = ? ORDER BY id", (livro.id,))

    def __para_avaliacao(self, linha, usuario, livro):
        return Avaliacao(linha["id"], linha["nota"], date.fromisoformat(linha["data"]),
                         usuario, livro, linha["comentario"])

    # Monta {id_do_comentario: {ids de quem curtiu}} lendo a tabela curtidas uma vez.
    def __curtidas_por_comentario(self):
        curtidas = {}
        for r in self.__consultar("SELECT comentario_id, usuario_id FROM curtidas"):
            curtidas.setdefault(r["comentario_id"], set()).add(r["usuario_id"])
        return curtidas

    def __para_comentario(self, linha, usuario, livro, curtidas):
        return Comentario(linha["id"], linha["texto"], date.fromisoformat(linha["data"]),
                          usuario, livro, curtidas.get(linha["id"], ()))

    # Nos buscar_* de avaliação e comentário, o resultado é um objeto ou None.
    def buscar_avaliacao(self, usuario, livro):
        linhas = self.__consultar(
            "SELECT * FROM avaliacoes WHERE usuario_id = ? AND livro_id = ?", (usuario.id, livro.id)
        )
        return self.__para_avaliacao(linhas[0], usuario, livro) if linhas else None

    # Carrega usuários e livros uma vez e reaproveita ao montar cada Avaliacao (evita uma consulta por linha).
    def listar_avaliacoes(self, livro=None):
        usuarios, livros = self.__usuarios_por_id(), self.__ler_catalogo()["livros"]
        return [self.__para_avaliacao(r, usuarios[r["usuario_id"]], livros[r["livro_id"]])
                for r in self.__filtrar_por_livro("avaliacoes", livro)]

    def buscar_comentario(self, id_comentario):
        linhas = self.__consultar("SELECT * FROM comentarios WHERE id = ?", (id_comentario,))
        if not linhas:
            return None
        usuario = self.buscar_usuario(linhas[0]["usuario_id"])
        return self.__para_comentario(linhas[0], usuario, self.buscar_livro(linhas[0]["livro_id"]),
                                      self.__curtidas_por_comentario())

    def buscar_comentario_de(self, usuario, livro):
        linhas = self.__consultar(
            "SELECT * FROM comentarios WHERE usuario_id = ? AND livro_id = ?", (usuario.id, livro.id)
        )
        return (self.__para_comentario(linhas[0], usuario, livro, self.__curtidas_por_comentario())
                if linhas else None)

    def listar_comentarios(self, livro=None):
        usuarios, livros = self.__usuarios_por_id(), self.__ler_catalogo()["livros"]
        curtidas = self.__curtidas_por_comentario()
        return [self.__para_comentario(r, usuarios[r["usuario_id"]], livros[r["livro_id"]], curtidas)
                for r in self.__filtrar_por_livro("comentarios", livro)]
