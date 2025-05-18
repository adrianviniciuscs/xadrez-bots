#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que fica cada vez mais azarado a cada peça perdida."""

import chess
import random
from bot import ChessBot, BotRegistry

@BotRegistry.register
class RevengeLuckBot(ChessBot):
    """
    Bot que sacrifica peças para "quebrar a maldição" cada vez que perde uma peça.
    A cada peça perdida, a probabilidade de sacrificar outra peça aumenta em 10%.
    """
    
    @property
    def name(self) -> str:
        return "Revenge Luck Bot"
    
    def __init__(self):
        super().__init__()
        self.bad_luck_counter = 0
        self.last_piece_count = 16  # Número inicial de peças
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        moves = list(board.legal_moves)
        if not moves:
            return None
        
        # Conta quantas peças temos agora
        current_pieces = sum(1 for sq in chess.SQUARES for p in [board.piece_at(sq)] 
                            if p and p.color == board.turn)
        
        # Verifica se perdemos peças desde o último movimento
        if hasattr(self, 'last_piece_count') and current_pieces < self.last_piece_count:
            # Aumenta o contador de azar (10% por peça perdida)
            pieces_lost = self.last_piece_count - current_pieces
            self.bad_luck_counter += pieces_lost * 10
            print(f"{self.name} perdeu {pieces_lost} peças! Nível de azar: {self.bad_luck_counter}%")
        
        # Verifica se ganhamos peças (acidentalmente)
        if hasattr(self, 'last_piece_count') and current_pieces > self.last_piece_count:
            # Reset do contador de azar
            print(f"{self.name} ganhou uma peça! Azar resetado!")
            self.bad_luck_counter = 0
        
        # Atualiza o contador de peças para a próxima jogada
        self.last_piece_count = current_pieces
        
        # Baseado no contador de azar, decide se vai se sacrificar
        if random.random() * 100 < self.bad_luck_counter:
            # Procura uma peça para sacrificar (mover para uma casa atacada)
            sacrifice_moves = []
            
            # Encontra casas atacadas pelo oponente
            attacked_squares = [sq for sq in chess.SQUARES if board.is_attacked_by(not board.turn, sq)]
            
            if attacked_squares:
                # Prioriza peças valiosas para o sacrifício (irônico)
                for move in moves:
                    piece = board.piece_at(move.from_square)
                    if not piece:
                        continue
                        
                    # Verifica se o movimento leva a uma casa atacada
                    if move.to_square in attacked_squares:
                        score = 0
                        # Atribui valor à peça (maior é melhor para sacrificar)
                        if piece.piece_type == chess.PAWN:
                            score = 1
                        elif piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                            score = 3
                        elif piece.piece_type == chess.ROOK:
                            score = 5
                        elif piece.piece_type == chess.QUEEN:
                            score = 9
                        # Não sacrificamos o rei (seria ilegal de qualquer forma)
                        
                        # Adiciona à lista de sacrifícios possíveis com seu valor
                        sacrifice_moves.append((move, score))
            
            # Se encontramos movimentos de sacrifício, escolhe o melhor (peça mais valiosa)
            if sacrifice_moves:
                # Organiza pelo valor (secundário) e escolhe o mais valioso
                sacrifice_moves.sort(key=lambda x: x[1], reverse=True)
                chosen_move = sacrifice_moves[0][0]
                
                # Reduz o contador de azar após o sacrifício (50%)
                self.bad_luck_counter //= 2
                print(f"{self.name} sacrifica uma peça para aplacar os deuses do xadrez! Nível de azar reduzido para {self.bad_luck_counter}%")
                
                return chosen_move
        
        # Se não vamos sacrificar ou não encontramos um bom sacrifício, jogamos normalmente
        # Tenta jogar de forma minimamente sensata
        capture_moves = [move for move in moves if board.is_capture(move)]
        check_moves = [move for move in moves if board.gives_check(move)]
        
        # Prioriza capturas > xeques > movimentos normais
        if capture_moves:
            return random.choice(capture_moves)
        elif check_moves:
            return random.choice(check_moves)
        else:
            return random.choice(moves)