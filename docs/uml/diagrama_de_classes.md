# Diagrama de classes

Abra no GitHub, no VS Code com a extensão Mermaid ou em mermaid.live.

```mermaid
classDiagram
    direction LR

    class Usuario {
        -int id
        -str nome
        -str email
        -str senha
        -bool admin
        +verificar_senha(senha) bool
        +alterar_senha(atual, nova)
    }
    class Livro {
        -int id
        -str nome
        -int ano
        -str sinopse
        -str edicao
    }
    class Genero {
        -int id
        -str nome
    }
    class Autora {
        -int id
        -str nome
    }
    class Editora {
        -int id
        -str nome
    }
    class Estante {
        -int id
        -bool lido
        -bool favorito
        -bool quer_ler
        +definir_lido(valor)
        +definir_favorito(valor)
        +definir_quer_ler(valor)
    }
    class Avaliacao {
        -int id
        -int nota
        -date data
        -str comentario
    }
    class Comentario {
        -int id
        -str texto
        -date data
        -set curtidas
        +alternar_curtida(usuario)
        +curtido_por(usuario) bool
        +substituir(texto, data)
    }

    Livro "*" --> "1" Genero
    Livro "*" --> "1" Autora
    Livro "*" --> "1" Editora
    Editora "*" o-- "*" Autora : publica
    Estante "*" --> "1" Usuario
    Estante "*" --> "1" Livro
    Avaliacao "*" --> "1" Usuario
    Avaliacao "*" --> "1" Livro
    Comentario "*" --> "1" Usuario
    Comentario "*" --> "1" Livro
    Comentario "*" --> "*" Usuario : curtido por
```

Leitura rápida das setas:

| Seta | Significa | Exemplo daqui |
|---|---|---|
| `-->` associação, com navegabilidade | A classe da ponta sem seta guarda a outra | `Estante` guarda o `Usuario` e o `Livro` |
| `o--` agregação | Tem um, e a parte sobrevive sem o todo | `Editora` tem `Autora`; apagar a editora não apaga a autora |
| `*` e `1` | Multiplicidade | Muitos livros para um gênero |

`Estante` é a classe que resolve "lido, favorito e quero ler são de cada pessoa": uma linha por par usuário e livro.

# Padrão Strategy (filtros)

```mermaid
classDiagram
    direction TB
    class Filtro {
        <<abstract>>
        +passa(item) bool
    }
    class FiltroTexto
    class FiltroGenero
    class FiltroEditora
    class FiltroTodos
    class FiltroLido
    class FiltroFavorito
    class FiltroQueroLer
    class CatalogoService {
        +buscar(texto, genero, editora)
    }
    class EstanteService {
        +listar(usuario, filtro)
    }

    Filtro <|-- FiltroTexto
    Filtro <|-- FiltroGenero
    Filtro <|-- FiltroEditora
    Filtro <|-- FiltroTodos
    Filtro <|-- FiltroLido
    Filtro <|-- FiltroFavorito
    Filtro <|-- FiltroQueroLer
    CatalogoService ..> Filtro : usa
    EstanteService ..> Filtro : usa
```

`<|--` é herança (aqui, realização de uma classe abstrata) e `..>` é dependência: o serviço só usa o filtro durante a chamada, não o guarda.

# DAO (repositórios)

```mermaid
classDiagram
    direction TB
    class Repositorio {
        <<interface>>
        +salvar(objeto)
        +remover(objeto)
        +proximo_id(colecao) int
        +transacao()
        +buscar_usuario(id) Usuario
        +listar_livros() list
        +buscar_registro(usuario, livro) Estante
        +listar_avaliacoes(livro) list
        +buscar_comentario_de(usuario, livro) Comentario
    }
    class RepositorioMemoria {
        -dados
    }
    class RepositorioSQLite {
        -conexao
        +fechar()
    }
    class ContaService
    class CatalogoService
    class EstanteService
    class AvaliacaoService
    class Sistema

    Repositorio <|.. RepositorioMemoria
    Repositorio <|.. RepositorioSQLite
    ContaService ..> Repositorio : usa
    CatalogoService ..> Repositorio : usa
    EstanteService ..> Repositorio : usa
    AvaliacaoService ..> Repositorio : usa
    Sistema ..> RepositorioSQLite : cria
```

`<|..` é realização: a classe cumpre o contrato da interface. Os serviços dependem só de `Repositorio`, então trocar a implementação não muda os serviços. Os testes usam as duas implementações.

# Camadas

```mermaid
flowchart LR
    V[view: HTML] --> C[controller: rotas Flask ou menu do terminal]
    C --> S[servicos: regras]
    S --> R[repositorios: interface Repositorio]
    R --> M[modelos: classes do domínio]
    R --> B[(dados/estante.db)]
```
