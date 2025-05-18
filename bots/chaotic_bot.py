#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que faz movimentos imprevisíveis baseados no tempo."""

import chess
import time
import random
import datetime
from bot import ChessBot, BotRegistry

@BotRegistry.register
class ChaoticBot(ChessBot):
    """Bot que escolhe movimentos com base no tempo atual, sendo imprevisível."""
    
    @property
    def name(self) -> str:
        return "Chaotic Bot"
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        moves = list(board.legal_moves)
        
        # Usa o timestamp atual como parte do processo de seleção
        timestamp = int(time.time())
        random.seed(timestamp % 100)
        
        # Escolhe um movimento com base no segundo atual
        second = datetime.datetime.now().second
        index = second % len(moves) if moves else 0
        
        return moves[index]