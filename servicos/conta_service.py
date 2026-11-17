from modelos.usuario import Usuario


class ContaService:
    def __init__(self, usuarios):
        self.__usuarios = usuarios

    def cadastrar(self, nome, email, senha):
        if self.__usuarios.buscar_por_email(email) is not None:
            raise ValueError("e-mail já cadastrado")
        usuario = Usuario(self.__usuarios.proximo_id(), nome, email, senha)
        self.__usuarios.salvar(usuario)
        return usuario

    def entrar(self, email, senha):
        usuario = self.__usuarios.buscar_por_email(email)
        if usuario is None or not usuario.verificar_senha(senha):
            raise ValueError("e-mail ou senha incorretos")
        return usuario

    def buscar_por_id(self, id_usuario):
        return self.__usuarios.buscar(id_usuario)
