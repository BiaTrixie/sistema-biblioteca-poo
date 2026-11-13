# Guia de estudos: Estante

Use este guia para entender o sistema e apresentá-lo. Leia de cima para baixo: primeiro a visão geral, depois as pastas, depois um caminho completo, depois arquivo por arquivo.

┌──────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│    Passo     │                                                     Resultado                                                     │
├──────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│              │ Autora estava copiada de Editora e quebrava o main.py. Corrigi isso, tirei lido de Livro (agora fica em Estante), │
│ 1. Modelos   │  corrigi o bug dos likes e fiz Avaliacao e Comentario guardarem usuário e livro. A nota fora de 1 a 5 agora é     │
│              │ recusada.                                                                                                         │
├──────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2.           │ Listas em memória, com a semente dos 6 livros do protótipo. A estante da Ana dá 6 total, 2 favoritos e 3 quero    │
│ Repositório  │ ler, como na tela.                                                                                                │
├──────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Serviços  │ Conta, catálogo, estante e avaliação, mais o padrão Strategy em servicos/filtros.py.                              │
├──────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. Terminal  │ python3 main.py percorre o roteiro completo.                                                                      │
├──────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. Flask     │ As 6 telas, no formato do professor (app/, view/, static/).                                                       │
├──────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 6. UML       │ docs/uml/diagrama_de_classes.md, em Mermaid.                                                                      │
├──────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 7. Guia      │ guia_de_estudos.md, no formato que você elogiou, com as 10 perguntas da revisão respondidas com o nosso código.   │
└──────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


## 1. O que é o sistema

O Estante é um diário de livros. Cada pessoa tem uma conta, marca livros como lido, favorito ou quero ler, dá nota de 1 a 5 e comenta.

Pense numa biblioteca de bairro. O acervo é da biblioteca: o livro existe para todo mundo. Mas "já li" e "quero ler" são de cada leitor. Por isso o sistema separa duas coisas: o `Livro` (do acervo) e a `Estante` (a ficha de uma pessoa sobre um livro).

Dois jeitos de usar, com as mesmas regras por baixo:

| Jeito | Comando | Para que serve |
|---|---|---|
| Terminal | `python3 main.py` | Roteiro completo em menu |
| Web (Flask) | `python3 mainFlask.py` e abrir `http://127.0.0.1:5000` | As 6 telas do protótipo |

Login de teste: `ana@email.com`, senha `123456`. Testes: `python3 -m unittest discover tests`.

## 2. Mapa das pastas

```
modelos/        as classes do domínio (Livro, Usuario, Estante...)
repositorios/   onde os dados ficam guardados (listas em memória) e a semente
servicos/       as regras do sistema (avaliar, buscar, marcar status...)
  filtros.py      o padrão Strategy
menus/          o terminal (só pergunta e mostra)
app/            o Flask: rotas.py (controller), view/ (HTML), static/ (CSS)
tests/          um arquivo de teste por serviço
docs/uml/       os diagramas de classes
```

Por que dividir assim: cada pasta responde a uma pergunta só. "O que é um livro?" está em `modelos`. "Onde guardo?" está em `repositorios`. "Qual a regra?" está em `servicos`. "Como mostro?" está em `menus` e `app`. Se a regra de nota mudar, você mexe em um lugar só. Isso é o princípio de responsabilidade única (SRP) que o professor cobra.

## 3. Um caminho completo: a Ana avalia O Hobbit

Siga uma ação do clique até o objeto. É a melhor forma de entender como as pastas se conversam.

| Passo | Onde | O que acontece |
|---|---|---|
| 1 | `app/view/avaliar.html` | A Ana escolhe 5 estrelas, escreve e clica em "Publicar avaliação". O formulário envia um POST |
| 2 | `app/rotas.py`, função `avaliar` | Lê `nota` e `texto` do formulário e chama o serviço. Não decide nada |
| 3 | `servicos/avaliacao_service.py`, `avaliar` | Procura se a Ana já avaliou esse livro. Se sim, atualiza; se não, cria |
| 4 | `modelos/avaliacao.py` | O `Avaliacao` valida que a nota é de 1 a 5. Se não for, lança `ValueError` |
| 5 | `repositorios/repositorio_memoria.py` | A avaliação nova entra na lista `avaliacoes` |
| 6 | de volta na rota | Sem erro, redireciona para a página do livro. Com erro, mostra a mensagem na tela (`flash`) |

O terminal faz o mesmo caminho a partir do passo 3. O passo 3 em diante é idêntico nos dois, e é por isso que `menus/` e `app/` não têm regra de negócio.

## 4. Arquivo por arquivo

### modelos/ (o domínio)

| Arquivo | O que é | Detalhe importante |
|---|---|---|
| `usuario.py` | Pessoa com conta | Valida e-mail e senha no construtor. Guarda a senha em texto puro (ver limitações) |
| `livro.py` | Um livro do acervo | Tem gênero, editora e autora. Não sabe se foi lido: isso é da `Estante` |
| `genero.py`, `editora.py`, `autora.py` | Dados do livro | `Editora` e `Autora` se conhecem (agregação) |
| `estante.py` | A ficha de uma pessoa sobre um livro | Guarda `lido`, `favorito` e `quer_ler`. Uma ficha por par usuário e livro |
| `avaliacao.py` | Nota de 1 a 5 de uma pessoa sobre um livro | Valida a nota no construtor e no setter |
| `comentario.py` | Texto de uma pessoa sobre um livro | Tem `curtir()` que soma 1 |

Todas usam atributos privados (`self.__nome`) e `@property`. É o encapsulamento: de fora ninguém mexe direto no dado, só pelo caminho que a classe oferece e valida.

### repositorios/

| Arquivo | O que faz |
|---|---|
| `repositorio_memoria.py` | Tem uma lista para cada tipo de objeto e o método `proximo_id`. Os dados somem ao fechar |
| `semente.py` | Cria o conteúdo inicial: os 6 livros do protótipo, 3 usuários, a estante da Ana e as avaliações |

Por que existe: os serviços não sabem onde os dados ficam. Se um dia for um arquivo ou um banco, troca-se só esta pasta. Esse é o papel do DAO que o professor ensinou, numa versão mínima.

### servicos/ (as regras)

| Arquivo | Regras que cuida |
|---|---|
| `conta_service.py` | Cadastro (e-mail único) e login |
| `catalogo_service.py` | Listar, buscar, média das notas, populares |
| `estante_service.py` | Marcar e desmarcar status, listar por filtro, contadores |
| `avaliacao_service.py` | Avaliar (uma por pessoa), comentar, curtir, diário recente |
| `filtros.py` | O padrão Strategy (próxima seção) |
| `sistema.py` | Monta repositório e serviços uma vez. Terminal e Flask usam esta classe |

### menus/ e app/ (a fronteira com a pessoa)

| Arquivo | O que faz |
|---|---|
| `menus/menu_principal.py` | Menu de terminal: pergunta, chama o serviço, imprime |
| `app/__init__.py` | Cria o `app` Flask. `template_folder="view"` é como no exemplo do professor |
| `app/rotas.py` | Uma função por tela ou ação. Lê o formulário, chama o serviço, escolhe a página |
| `app/view/*.html` | As telas. `base.html` é o esqueleto (topo e mensagens); as outras o estendem |
| `app/static/css/style.css` | Tema escuro e verde do protótipo |
| `mainFlask.py` | Duas linhas que sobem o servidor |

A rota `exigir_login` (em `rotas.py`) manda qualquer pessoa sem sessão para o login, menos as telas de entrada e cadastro.

## 5. O padrão de projeto: Strategy

**O problema.** Buscar livros tem várias regras: por texto, por gênero, por editora. A estante também: todos, lidos, favoritos, quero ler. Sem padrão, o serviço viraria uma pilha de `if/elif`.

**A solução.** Cada regra vira uma classe pequena com o mesmo método, `passa(item)`, que responde sim ou não. O serviço monta uma lista de filtros e o `aplicar` deixa passar só quem passa em todos.

```python
class Filtro(ABC):
    @abstractmethod
    def passa(self, item) -> bool: ...

class FiltroGenero(Filtro):
    def passa(self, livro):
        return livro.genero.nome.lower() == self.__nome
```

**Por que escolhemos este.** Ele aparece em duas telas do protótipo (estante e busca), e acrescentar um filtro novo é criar uma classe, sem mexer no serviço. Observer e Singleton caberiam, mas seriam forçados.

| Parte do Strategy | No nosso código |
|---|---|
| Interface da estratégia | `Filtro` (classe abstrata) |
| Estratégias concretas | `FiltroTexto`, `FiltroGenero`, `FiltroEditora`, `FiltroTodos`, `FiltroLido`, `FiltroFavorito`, `FiltroQueroLer` |
| Quem usa | `CatalogoService.buscar` e `EstanteService.listar` |

Detalhe honesto: nos filtros do catálogo o item é um `Livro`; nos da estante é um registro `Estante`. A ideia é a mesma, só muda o tipo do item.

## 6. UML

Os diagramas estão em `docs/uml/diagrama_de_classes.md`: classes do domínio, o Strategy e as camadas. Lá há uma tabela de leitura das setas.

## 7. Perguntas que o professor pode fazer (com a resposta do nosso código)

| Pergunta da revisão | Resposta usando o Estante |
|---|---|
| Encapsulamento | `Avaliacao`: o atributo `__nota` é privado; só se muda pelo setter, que valida de 1 a 5 |
| Interface x classe abstrata | `Filtro` é abstrata: só diz "o que sabe fazer" (`passa`) |
| SRP e camadas | Modelo guarda dado, serviço aplica regra, rota só liga formulário e serviço |
| Composição x herança | Herança: filtros herdam de `Filtro`. Composição: o serviço usa filtros, não herda deles |
| Classe x objeto | `Livro` é a classe; "O Hobbit" é um objeto dela |
| Agregação x composição | `Editora` tem `Autora` (agregação): apagar a editora não apaga a autora |
| Navegabilidade | `Estante` conhece `Usuario` e `Livro`, mas o `Livro` não conhece a `Estante` |
| Polimorfismo | `aplicar` chama `f.passa(item)` sem saber qual filtro é; cada um responde do seu jeito |
| Tipos de associação | Estante, Avaliação e Comentário ligam Usuário e Livro (muitos para um) |
| Acoplamento e coesão | O terminal e o Flask só dependem de `Sistema`; cada serviço cuida de um assunto |

## 8. Limitações conhecidas

- Os dados ficam só em memória: ao reiniciar, volta tudo para a semente.
- A senha fica em texto puro dentro de `Usuario`. Num sistema real usaria hash.
- A chave da sessão do Flask está escrita no código. Aceitável num trabalho acadêmico.
- No protótipo, a busca "fantasia" mostra Circe (Mitologia), mas a busca real só devolve os 2 livros de fantasia. O desenho tinha essa inconsistência.
- Os modelos dos colegas foram alterados (Autora restaurada, `lido` movido para `Estante`, bug dos likes, usuário e livro nas avaliações e comentários). Combinar com o grupo antes de subir.
