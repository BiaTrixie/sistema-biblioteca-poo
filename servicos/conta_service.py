from modelos.usuario import Usuario


class ContaService:
    def __init__(self, repo):
        self.__repo = repo

    def cadastrar(self, nome, email, senha):
        if self.__buscar_por_email(email) is not None:
            raise ValueError("e-mail já cadastrado")
        novo_id = self.__repo.proximo_id(self.__repo.usuarios)
        usuario = Usuario(novo_id, nome, email, senha)  # a classe valida os campos
        self.__repo.usuarios.append(usuario)
        return usuario

    def entrar(self, email, senha):
        usuario = self.__buscar_por_email(email)
        if usuario is None or not usuario.verificar_senha(senha):
            raise ValueError("e-mail ou senha incorretos")
        return usuario

    def buscar_por_id(self, id_usuario):
        return next((u for u in self.__repo.usuarios if u.id == id_usuario), None)

    def __buscar_por_email(self, email):
        email = str(email).strip().lower()
        return next((u for u in self.__repo.usuarios if u.email == email), None)
