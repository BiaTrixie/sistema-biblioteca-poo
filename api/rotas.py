import secrets
from datetime import date

from flask import Blueprint, g, jsonify, request

from api import sistema
from api.serializacao import avaliacao, comentario, estante, livro, usuario

api = Blueprint("api", __name__)
TOKENS = {}

PUBLICAS = {
    "api.entrar",
    "api.cadastrar",
    "api.listar_livros",
    "api.obter_livro",
    "api.populares",
    "api.livro_do_dia",
    "api.generos",
    "api.editoras",
    "api.avaliacoes_do_livro",
    "api.comentarios_do_livro",
    "api.diario",
}

@api.before_request
def exigir_login():
    g.usuario = _usuario_do_token()
    if request.endpoint in PUBLICAS:
        return None
    if g.usuario is None:
        return jsonify({"erro": "faça login"}), 401
    return None

@api.post("/contas")
def cadastrar():
    dados = _json()
    if dados is None:
        return _erro("envie um JSON")
    try:
        pessoa = sistema.conta.cadastrar(dados.get("nome", ""), dados.get("email", ""), dados.get("senha", ""))
    except ValueError as erro:
        return _erro(str(erro))
    return jsonify(usuario(pessoa)), 201

@api.post("/login")
def entrar():
    dados = _json()
    if dados is None:
        return _erro("envie um JSON")
    try:
        pessoa = sistema.conta.entrar(dados.get("email", ""), dados.get("senha", ""))
    except ValueError as erro:
        return _erro(str(erro), 401)
    token = secrets.token_urlsafe(32)
    TOKENS[token] = pessoa.id
    return jsonify({"token": token, "usuario": usuario(pessoa)})

@api.post("/sair")
def sair():
    token = _token()
    TOKENS.pop(token, None)
    return "", 204

@api.get("/perfil")
def perfil():
    pessoa = g.usuario
    avaliacoes, comentarios = sistema.avaliacao.do_usuario(pessoa)
    return jsonify({
        "usuario": usuario(pessoa),
        "resumo": sistema.estante.resumo(pessoa),
        "avaliacoes": len(avaliacoes),
        "comentarios": len(comentarios),
    })

@api.get("/livros")
def listar_livros():
    texto = request.args.get("q", "")
    genero = request.args.get("genero", "")
    editora = request.args.get("editora", "")
    itens = sistema.catalogo.buscar(texto, genero, editora)
    return jsonify([livro(item, sistema.catalogo.media(item)) for item in itens])

@api.get("/livros/populares")
def populares():
    itens = sistema.catalogo.populares()
    return jsonify([livro(item, sistema.catalogo.media(item)) for item in itens])

@api.get("/livros/do-dia")
def livro_do_dia():
    if not sistema.catalogo.listar():
        return _erro("não há livros", 404)
    item = sistema.catalogo.livro_do_dia(date.today())
    return jsonify(livro(item, sistema.catalogo.media(item)))

@api.get("/livros/<int:id_livro>")
def obter_livro(id_livro):
    item = _livro(id_livro)
    if item is None:
        return _erro("livro não encontrado", 404)
    return jsonify(livro(item, sistema.catalogo.media(item)))

@api.get("/generos")
def generos():
    return jsonify(sistema.catalogo.generos())

@api.get("/editoras")
def editoras():
    return jsonify(sistema.catalogo.editoras())

@api.get("/estante")
def listar_estante():
    filtro = request.args.get("filtro", "todos")
    try:
        registros = sistema.estante.listar(g.usuario, filtro)
    except ValueError as erro:
        return _erro(str(erro))
    return jsonify([estante(registro) for registro in registros])

@api.get("/estante/resumo")
def resumo_estante():
    return jsonify(sistema.estante.resumo(g.usuario))

@api.patch("/estante/<int:id_livro>")
def mudar_estante(id_livro):
    item = _livro(id_livro)
    if item is None:
        return _erro("livro não encontrado", 404)
    dados = _json()
    if dados is None or "status" not in dados:
        return _erro("envie o status: lido, favorito ou quer_ler")
    try:
        registro = sistema.estante.alternar(g.usuario, item, dados["status"])
    except ValueError as erro:
        return _erro(str(erro))
    return jsonify(estante(registro))

@api.get("/livros/<int:id_livro>/avaliacoes")
def avaliacoes_do_livro(id_livro):
    item = _livro(id_livro)
    if item is None:
        return _erro("livro não encontrado", 404)
    avaliacoes, _ = sistema.avaliacao.do_livro(item)
    return jsonify([avaliacao(item_avaliacao) for item_avaliacao in avaliacoes])

@api.post("/livros/<int:id_livro>/avaliacoes")
def avaliar(id_livro):
    item = _livro(id_livro)
    if item is None:
        return _erro("livro não encontrado", 404)
    dados = _json()
    if dados is None or "nota" not in dados:
        return _erro("envie a nota")
    try:
        nota = int(dados["nota"])
    except (TypeError, ValueError):
        return _erro("a nota vai de 1 a 5")
    ja_existia = sistema.avaliacao.avaliacao_de(g.usuario, item) is not None
    try:
        criada = sistema.avaliacao.avaliar(g.usuario, item, nota, dados.get("texto", ""))
    except ValueError as erro:
        return _erro(str(erro))
    return jsonify(avaliacao(criada)), 200 if ja_existia else 201

@api.get("/livros/<int:id_livro>/comentarios")
def comentarios_do_livro(id_livro):
    item = _livro(id_livro)
    if item is None:
        return _erro("livro não encontrado", 404)
    _, comentarios = sistema.avaliacao.do_livro(item)
    return jsonify([_comentario(item_comentario) for item_comentario in comentarios])

@api.post("/livros/<int:id_livro>/comentarios")
def comentar(id_livro):
    item = _livro(id_livro)
    if item is None:
        return _erro("livro não encontrado", 404)
    dados = _json()
    if dados is None or "texto" not in dados:
        return _erro("envie o texto")
    ja_existia = sistema.avaliacao.comentario_de(g.usuario, item) is not None
    try:
        criado = sistema.avaliacao.comentar(g.usuario, item, dados["texto"])
    except ValueError as erro:
        return _erro(str(erro))
    return jsonify(_comentario(criado)), 200 if ja_existia else 201

@api.patch("/comentarios/<int:id_comentario>")
def curtir(id_comentario):
    try:
        atualizado = sistema.avaliacao.curtir(id_comentario, g.usuario)
    except ValueError as erro:
        return _erro(str(erro), 404)
    return jsonify(_comentario(atualizado))

@api.get("/diario")
def diario():
    eventos = []
    for tipo, item in sistema.avaliacao.diario_recente():
        corpo = avaliacao(item) if tipo == "avaliou" else _comentario(item)
        eventos.append({"tipo": tipo, **corpo})
    return jsonify(eventos)

def _usuario_do_token():
    token = _token()
    if token is None:
        return None
    return sistema.conta.buscar_por_id(TOKENS.get(token))

def _token():
    cabecalho = request.headers.get("Authorization", "")
    if not cabecalho.startswith("Bearer "):
        return None
    return cabecalho.removeprefix("Bearer ").strip() or None

def _livro(id_livro):
    return sistema.catalogo.obter(id_livro)

def _json():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return None
    return dados

def _comentario(item):
    pessoa = getattr(g, "usuario", None)
    return comentario(item, pessoa.id if pessoa else None)


def _erro(mensagem, status=400):
    return jsonify({"erro": mensagem}), status
