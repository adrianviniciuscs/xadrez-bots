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

## Bots Incluídos

O sistema já vem com alguns bots simples prontos para uso:

- **RandomBot**: Faz movimentos aleatórios.
- **AggressiveBot**: Prefere capturar peças do oponente.
- **DefensiveBot**: Tenta evitar perdas e movimentos arriscados.
- **ParanoidBot**: Tenta se afastar das peças do oponente.
- **ChaoticBot**: Movimentos imprevisíveis baseados no tempo atual.

## Exemplo de Execução

Ao executar o programa, você verá um menu como este:

```
=== Torneio de Xadrez entre Bots ===

Bots disponíveis (5):
1. Random Bot (RandomBot)
2. Aggressive Bot (AggressiveBot)
3. Defensive Bot (DefensiveBot)
4. Paranoid Bot (ParanoidBot)
5. Chaotic Bot (ChaoticBot)

Opções:
1. Executar torneio round-robin completo
2. Assistir a uma partida específica
3. Sair
```

### Visualização dos jogos

Quando você escolhe assistir a uma partida, uma página HTML será aberta no seu navegador padrão mostrando o tabuleiro de xadrez e atualizando automaticamente a cada movimento.

## Licença

Este projeto está sob a licença MIT.
