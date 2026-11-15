class Autora:
    #perceba que todos os atributos sao privados, para que ngm altere diretamente, e sim atraves dos metodos da classe. Isso é encapsulamento, um dos pilares da POO
    def __init__(self, id: int, nome: str) -> None: # recebe o id e o nome da autora, e inicializa a lista de editoras como vazia
        self.__id = id # atributo privado para armazenar o id da autora. Privado pois não deve ser alterado após a criação do objeto. Vemos isso pois vem acompanhado de __ que indica que é privado
        self.__nome = self.__validar_nome(nome) # nome privado da autora, validado pelo método __validar_nome (método privado que valida o nome da autora, garantindo que não seja vazio ou apenas espaços em branco)
        self.__editoras: list["Editora"] = [] # lista privada de editoras associadas à autora. Inicializada como uma lista vazia, pois a autora pode não ter editoras associadas no momento da criação do objeto.
        # o comando list é usado para indicar que a variável __editoras é uma lista de objetos do tipo Editora.   
    
#     Pq usar o list["Editora"] = [] ao invés de apenas []?

# ┌───────────────────────────┬─────────────────────────┬────────────────────────┐
# │          Escrita          │         O que é         │        Para quê        │
# ├───────────────────────────┼─────────────────────────┼────────────────────────┤
# │ self.__editoras = []      │ uma lista vazia de      │ cria o valor           │
# │                           │ verdade                 │                        │
# ├───────────────────────────┼─────────────────────────┼────────────────────────┤
# │ self.__editoras:          │ lista vazia mais uma    │ cria o valor e         │
# │ list["Editora"] = []      │ anotação de tipo        │ documenta o que vai    │
# │                           │                         │ dentro                 │
# ├───────────────────────────┼─────────────────────────┼────────────────────────┤
# │ self.__editoras =         │ uma lista que já contém │ cria um valor          │
# │ ["Editora"]               │  a string "Editora"     │ diferente              │
# └───────────────────────────┴─────────────────────────┴────────────────────────┘



    @property # método getter para o id da autora, permitindo acesso ao id sem permitir alteração direta
    def id(self) -> int: # retorna um int, id da autoras
        return self.__id

    @property # metodo getter que retorna o nome
    def nome(self) -> str:
        return self.__nome

    @property # metodo getter que retorna a lista de editoras associadas à autora. 
    def editoras(self) -> list["Editora"]:
        return self.__editoras

    def adicionar_editora(self, editora: "Editora") -> None: # recebe um objeto do tipo Editora e adiciona à lista de editoras da autora; levanta ValueError se já estiver presente
        if editora in self.__editoras: # a própria classe garante que não haja editora repetida
            raise ValueError("editora já vinculada a esta autora")
        self.__editoras.append(editora)

    def remover_editora(self, editora: "Editora") -> None:
        if editora not in self.__editoras:
            raise ValueError("editora não vinculada a esta autora")
        self.__editoras.remove(editora)

    def __validar_nome(self, nome: str) -> str: 
        nome_limpo = nome.strip() # remove espaços em branco no início e no final do nome, garantindo que o nome não seja apenas espaços em branco
        if not nome_limpo:
            raise ValueError("nome da autora é obrigatório")
        return nome_limpo

    def __str__(self) -> str: # método especial que retorna uma representação em string do objeto Autora, incluindo o id e o nome da autora. Para visualizar isso, definimos um objeto autora (objeto = Autora(parametros)),e damos print(objeto)
        return f"[{self.__id}] {self.__nome}"
