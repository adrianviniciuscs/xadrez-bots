#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que só move peças para casas da mesma cor que começaram."""

import chess
import random
from bot import ChessBot, BotRegistry

@BotRegistry.register
class DiagonalBot(ChessBot):
    """
    Bot que só move peças para casas da mesma cor.
    Se uma peça está em casa branca, só pode se mover para outras casas brancas.
    Peões só avançam 2 casas se isso mantiver a cor.
    """
    
    @property
    def name(self) -> str:
        return "Diagonal Bot"
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        moves = list(board.legal_moves)
        if not moves:
            return None
            
        # Filtra movimentos que mantêm a cor da casa
        same_color_moves = []
        for move in moves:
            from_square = move.from_square
            to_square = move.to_square
            
            # Verifica se as casas de origem e destino têm a mesma cor
            from_square_color = self._is_white_square(from_square)
            to_square_color = self._is_white_square(to_square)
            
            # Se as cores são iguais, adiciona à lista de movimentos válidos
            if from_square_color == to_square_color:
                same_color_moves.append(move)
        
        # Se temos movimentos que mantêm a cor, usamos esses
        if same_color_moves:
            # Prioriza capturas que mantêm a cor
            capture_moves = [move for move in same_color_moves if board.is_capture(move)]
            if capture_moves:
                return random.choice(capture_moves)
            
            # Caso contrário, move para mesma cor aleatoriamente
            return random.choice(same_color_moves)
        
        # Se não há movimentos que mantêm a cor, usamos movimentos normais
        # (isso deve ser raro, mas é necessário para não ficar preso)
        print("Diagonal Bot teve que quebrar sua regra de cor!")
        
        # Pelo menos tenta evitar perder peças importantes
        best_moves = []
        for move in moves:
            piece = board.piece_at(move.from_square)
            if not piece:
                continue
                
            # Pontuação alta para peças valiosas (para não sacrificá-las)
            score = 0
            if piece.piece_type == chess.PAWN:
                score = 1
            elif piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                score = 3
            elif piece.piece_type == chess.ROOK:
                score = 5
            elif piece.piece_type == chess.QUEEN:
                score = 9
            elif piece.piece_type == chess.KING:
                score = 100
                
            # Evita mover peças valiosas para casas atacadas
            if board.is_attacked_by(not board.turn, move.to_square):
                score -= 5
                
            best_moves.append((move, score))
            
        if best_moves:
            # Ordena pela pontuação (menor para maior) e pega os 3 melhores
            best_moves.sort(key=lambda x: x[1], reverse=True)
            return best_moves[0][0]
        
        # Fallback para movimento aleatório
        return random.choice(moves)
    
    def _is_white_square(self, square):
        """
        Determina se uma casa é branca ou preta.
        No tabuleiro de xadrez, uma casa é branca se a soma do número da coluna e linha for par.
        """
        file = chess.square_file(square)  # 0-7 (a-h)
        rank = chess.square_rank(square)  # 0-7 (1-8)
        
        # Se a soma é par, a casa é branca; se ímpar, a casa é preta
        return (file + rank) % 2 == 0