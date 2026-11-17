from modelos.usuario import Usuario


class UsuarioRepositorio:
    def __init__(self, conexao):
        self.__conexao = conexao

    def proximo_id(self):
        return self.__conexao.proximo_id("usuarios")

    def salvar(self, usuario):
        self.__conexao.gravar("usuarios", {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "senha": usuario.senha_protegida,
            "admin": int(usuario.admin),
        })

    def buscar(self, id_usuario):
        linhas = self.__conexao.consultar("SELECT * FROM usuarios WHERE id = ?", (id_usuario,))
        return self.__para_usuario(linhas[0]) if linhas else None

    def buscar_por_email(self, email):
        email = str(email).strip().lower()
        linhas = self.__conexao.consultar("SELECT * FROM usuarios WHERE email = ?", (email,))
        return self.__para_usuario(linhas[0]) if linhas else None

    def por_id(self):
        return {linha["id"]: self.__para_usuario(linha)
                for linha in self.__conexao.consultar("SELECT * FROM usuarios")}

    def __para_usuario(self, linha):
        # protegida=True: a senha da linha já é um hash
        return Usuario(linha["id"], linha["nome"], linha["email"], linha["senha"],
                       bool(linha["admin"]), protegida=True)
