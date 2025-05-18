#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que prioriza capturar peças do oponente."""

import random
import chess
from bot import ChessBot, BotRegistry

@BotRegistry.register
class AggressiveBot(ChessBot):
    """Bot que prefere capturar peças do oponente."""
    
    @property
    def name(self) -> str:
        return "Aggressive Bot"
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        # Primeiro, procura movimentos de captura
        capture_moves = []
        for move in board.legal_moves:
            if board.is_capture(move):
                capture_moves.append(move)
        
        # Se houver movimentos de captura, escolhe um aleatoriamente
        if capture_moves:
            return random.choice(capture_moves)
        
        # Caso contrário, escolhe um movimento aleatório
        moves = list(board.legal_moves)
        return random.choice(moves)