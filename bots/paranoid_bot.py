#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que tenta se manter longe das peças do oponente."""

import chess
from bot import ChessBot, BotRegistry

@BotRegistry.register
class ParanoidBot(ChessBot):
    """Bot que tenta se mover para longe das peças do oponente."""
    
    @property
    def name(self) -> str:
        return "Paranoid Bot"
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        moves = list(board.legal_moves)
        
        # Função para calcular a "segurança" de uma posição após um movimento
        def safety_score(move):
            board.push(move)
            score = 0
            
            # Para cada peça própria, soma a distância para a peça mais próxima do oponente
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece and piece.color == board.turn:
                    min_distance = 8  # Valor máximo no tabuleiro
                    for opp_square in chess.SQUARES:
                        opp_piece = board.piece_at(opp_square)
                        if opp_piece and opp_piece.color != board.turn:
                            file_dist = abs((square % 8) - (opp_square % 8))
                            rank_dist = abs((square // 8) - (opp_square // 8))
                            distance = max(file_dist, rank_dist)
                            min_distance = min(min_distance, distance)
                    score += min_distance
            
            board.pop()
            return score
        
        # Escolhe o movimento que maximize a segurança
        if moves:
            return max(moves, key=safety_score)
        
        # Fallback, caso não haja movimentos válidos
        import random
        return random.choice(moves) if moves else None