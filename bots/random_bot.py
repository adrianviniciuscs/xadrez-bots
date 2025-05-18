#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que realiza movimentos aleatórios."""

import random
import chess
from bot import ChessBot, BotRegistry

@BotRegistry.register
class RandomBot(ChessBot):
    """Bot que escolhe movimentos aleatórios."""
    
    @property
    def name(self) -> str:
        return "Random Bot"
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        moves = list(board.legal_moves)
        return random.choice(moves)