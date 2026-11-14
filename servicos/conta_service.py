from modelos.usuario import Usuario


class ContaService:
    def __init__(self, repo):
        self.__repo = repo

    def cadastrar(self, nome, email, senha):
        if self.__repo.buscar_usuario_por_email(email) is not None:
            raise ValueError("e-mail já cadastrado")
        novo_id = self.__repo.proximo_id("usuarios")
        usuario = Usuario(novo_id, nome, email, senha)  # a classe valida os campos
        self.__repo.salvar(usuario)
        return usuario

    def entrar(self, email, senha):
        usuario = self.__repo.buscar_usuario_por_email(email)
        if usuario is None or not usuario.verificar_senha(senha):
            raise ValueError("e-mail ou senha incorretos")
        return usuario

    def buscar_por_id(self, id_usuario):
        return self.__repo.buscar_usuario(id_usuario)
