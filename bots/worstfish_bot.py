#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que propositalmente escolhe os piores movimentos possíveis."""

import chess
import random
from bot import ChessBot, BotRegistry

@BotRegistry.register
class WOrstfishBot(ChessBot):
    """Bot que tenta fazer os piores movimentos possíveis."""
    
    @property
    def name(self) -> str:
        return "WOrstfish Bot"
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        moves = list(board.legal_moves)
        
        # Valores das peças (negativo porque queremos minimizar)
        piece_values = {
            chess.PAWN: -1,
            chess.KNIGHT: -3,
            chess.BISHOP: -3,
            chess.ROOK: -5,
            chess.QUEEN: -9,
            chess.KING: -100  # Não queremos perder o rei
        }
        
        # Avaliação do tabuleiro atual
        def evaluate_board(board):
            score = 0
            
            # Pontuação baseada em material
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece:
                    value = piece_values.get(piece.piece_type, 0)
                    if piece.color == board.turn:
                        score += value
                    else:
                        score -= value
            
            # Penaliza desenvolvimento de peças
            if board.turn == chess.WHITE:
                # Penaliza movimentos de cavalos e bispos para longe da posição inicial
                for square in [chess.B1, chess.G1, chess.C1, chess.F1]:
                    if not board.piece_at(square):
                        score -= 0.5
            else:
                for square in [chess.B8, chess.G8, chess.C8, chess.F8]:
                    if not board.piece_at(square):
                        score -= 0.5
            
            # Penaliza controle do centro
            central_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
            for square in central_squares:
                if board.is_attacked_by(board.turn, square):
                    score -= 0.3
                    
            # Penaliza segurança do rei
            king_square = board.king(board.turn)
            if king_square is not None:
                king_attackers = len(board.attackers(not board.turn, king_square))
                score -= king_attackers * 0.5
                
            return score
        
        # Escolhe o movimento com a pior avaliação
        worst_score = float('inf')
        worst_moves = []
        
        for move in moves:
            board.push(move)
            
            # Verifica se é xeque-mate (queremos evitar isso)
            if board.is_checkmate():
                score = 1000  # Pontuação alta para evitar xeque-mate
            else:
                score = evaluate_board(board)
            
            board.pop()
            
            if score < worst_score:
                worst_score = score
                worst_moves = [move]
            elif score == worst_score:
                worst_moves.append(move)
        
        # Escolhe aleatoriamente entre os piores movimentos para não ser completamente previsível
        return random.choice(worst_moves) if worst_moves else random.choice(moves)