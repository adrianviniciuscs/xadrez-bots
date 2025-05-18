#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez cujo rei tem tendências suicidas e procura o perigo."""

import chess
import random
from bot import ChessBot, BotRegistry

@BotRegistry.register
class SuicidalKingBot(ChessBot):
    """Bot que tenta mover o rei para casas atacadas pelo oponente."""
    
    @property
    def name(self) -> str:
        return "Suicidal King Bot"
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        moves = list(board.legal_moves)
        if not moves:
            return None
        
        # Encontra o rei
        king_square = board.king(board.turn)
        if king_square is None:
            # Se não encontrarmos o rei (o que não deveria acontecer), move aleatoriamente
            return random.choice(moves)
        
        # Movimentos apenas do rei
        king_moves = [move for move in moves if move.from_square == king_square]
        
        # Se o rei não pode se mover, tentamos bloquear nossos próprios ataques
        if not king_moves:
            # Se há xeque, temos que bloqueá-lo (o Python-Chess não permite ignorar xeque)
            if board.is_check():
                return random.choice(moves)  # Move qualquer coisa para tentar sair do xeque
            
            # Tenta achar movimentos que bloqueiam nossos próprios ataques
            blocking_moves = []
            for move in moves:
                board.push(move)
                
                # Verifica se esse movimento bloqueia nossos próprios ataques
                if not board.is_check():
                    blocking_moves.append(move)
                
                board.pop()
            
            if blocking_moves:
                return random.choice(blocking_moves)
            return random.choice(moves)
        
        # Lista de casas atacadas pelo oponente
        attacked_squares = [sq for sq in chess.SQUARES if board.is_attacked_by(not board.turn, sq)]
        
        # Movimentos do rei para casas atacadas (suicidas)
        suicidal_moves = [move for move in king_moves if move.to_square in attacked_squares]
        
        # Se existem movimentos suicidas, priorize-os
        if suicidal_moves:
            # Calcula o "perigo" de cada casa (número de peças que atacam)
            danger_scores = {}
            for move in suicidal_moves:
                to_square = move.to_square
                danger = 0
                for sq in chess.SQUARES:
                    piece = board.piece_at(sq)
                    if piece and piece.color != board.turn:
                        if to_square in board.attacks(sq):
                            danger += 1
                danger_scores[move] = danger
            
            # Escolhe o movimento para a casa mais perigosa
            most_dangerous_move = max(suicidal_moves, key=lambda move: danger_scores.get(move, 0))
            return most_dangerous_move
        
        # Se não existem movimentos suicidas disponíveis, move o rei aleatoriamente
        if king_moves:
            return random.choice(king_moves)
        
        # Se tudo falhar, faz um movimento aleatório
        return random.choice(moves)