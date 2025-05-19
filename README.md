# Torneio Automatizado de Xadrez entre Bots 🏆♟️

Um sistema em Python para executar torneios automatizados de xadrez entre bots simples (e intencionalmente ruins).

## Características

- ✅ Registro automático de bots com sistema de decoradores
- ✅ Torneio Round Robin totalmente automatizado
- ✅ Visualização do tabuleiro durante as partidas
- ✅ Interface de linha de comando para executar torneios completos ou partidas específicas
- ✅ Geração de estatísticas e gráficos com os resultados

## Requisitos

Este projeto requer as seguintes bibliotecas Python:

```
python-chess
matplotlib
numpy
```

Você pode instalá-las com o pip:

```
pip install python-chess matplotlib numpy
```

## Como Usar

### Executar o torneio

```
python xadrez.py
```

Isso iniciará a interface de linha de comando que permite escolher entre executar um torneio completo ou assistir a uma partida específica.

### Implementar um novo Bot

Para criar um novo bot, você só precisa:

1. Criar uma nova classe derivada de `ChessBot`
2. Implementar os métodos `name` e `choose_move`
3. Decorar a classe com `@BotRegistry.register`

Exemplo:

```python
@BotRegistry.register
class MeuNovoBot(ChessBot):
    @property
    def name(self) -> str:
        return "Meu Bot Incrível"
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        # Sua lógica para escolher um movimento
        moves = list(board.legal_moves)
        return random.choice(moves)  # Exemplo simples
```
## Licença

Este projeto está sob a licença MIT.
