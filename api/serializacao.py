from datetime import date

def usuario(pessoa):
    return {"id": pessoa.id, "nome": pessoa.nome, "email": pessoa.email, "admin": pessoa.admin}

def livro(item, media=None):
    return {
        "id": item.id,
        "nome": item.nome,
        "ano": item.ano,
        "genero": item.genero.nome,
        "sinopse": item.sinopse,
        "edicao": item.edicao,
        "editora": item.editora.nome,
        "autora": item.autora.nome,
        "media": media,
    }

def estante(registro):
    return {
        "id": registro.id,
        "livro_id": registro.livro.id,
        "livro": registro.livro.nome,
        "genero": registro.livro.genero.nome,
        "autora": registro.livro.autora.nome,
        "lido": registro.lido,
        "favorito": registro.favorito,
        "quer_ler": registro.quer_ler,
    }

def avaliacao(item):
    return {
        "id": item.id,
        "nota": item.nota,
        "comentario": item.comentario,
        "data": item.data.isoformat() if isinstance(item.data, date) else str(item.data),
        "usuario_id": item.usuario.id,
        "usuario": item.usuario.nome,
        "livro_id": item.livro.id,
        "livro": item.livro.nome,
    }

def comentario(item, usuario_id=None):
    return {
        "id": item.id,
        "texto": item.texto,
        "data": item.data.isoformat() if isinstance(item.data, date) else str(item.data),
        "usuario_id": item.usuario.id,
        "usuario": item.usuario.nome,
        "livro_id": item.livro.id,
        "livro": item.livro.nome,
        "curtidas": item.numero_likes,
        "eu_curti": usuario_id in item.curtidas if usuario_id is not None else False,
    }
