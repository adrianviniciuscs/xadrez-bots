#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que prioriza movimentos defensivos."""

import random
import chess
from bot import ChessBot, BotRegistry

@BotRegistry.register
class DefensiveBot(ChessBot):
    """Bot que tenta evitar perdas e prefere movimentos que não resultam em capturas imediatas."""
    
    @property
    def name(self) -> str:
        return "Defensive Bot"
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        safe_moves = []
        risky_moves = []
        
        for move in board.legal_moves:
            # Faz o movimento
            board.push(move)
            
            # Verifica se o oponente pode capturar alguma peça
            is_risky = False
            for counter_move in board.legal_moves:
                if board.is_capture(counter_move):
                    is_risky = True
                    break
            
            # Desfaz o movimento
            board.pop()
            
            if is_risky:
                risky_moves.append(move)
            else:
                safe_moves.append(move)
        
        # Prefere movimentos seguros
        if safe_moves:
            return random.choice(safe_moves)
        
        # Se não houver movimentos seguros, escolhe qualquer um
        moves = list(board.legal_moves)
        return random.choice(moves)