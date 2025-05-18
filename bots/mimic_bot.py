#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que tenta copiar o último movimento do adversário."""

import chess
import random
from bot import ChessBot, BotRegistry

@BotRegistry.register
class MimicBot(ChessBot):
    """Bot que tenta copiar o último movimento do adversário, mesmo quando é uma má ideia."""
    
    @property
    def name(self) -> str:
        return "Mimic Bot"
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        moves = list(board.legal_moves)
        if not moves:
            return None
        
        # Se não houver movimento anterior (primeiro movimento do jogo), mova aleatoriamente
        if not board.move_stack:
            return random.choice(moves)
        
        # Obtém o último movimento do adversário
        last_move = board.move_stack[-1]
        
        # Tenta copiar o padrão do movimento (tipo de peça e offset)
        # Por exemplo, se o adversário moveu um cavalo em L, tentaremos mover nosso cavalo em L
        
        # Calcula o offset (deslocamento) do último movimento
        last_from_file = chess.square_file(last_move.from_square)
        last_from_rank = chess.square_rank(last_move.from_square)
        last_to_file = chess.square_file(last_move.to_square)
        last_to_rank = chess.square_rank(last_move.to_square)
        
        file_offset = last_to_file - last_from_file
        rank_offset = last_to_rank - last_from_rank
        
        # Obtém o tipo da peça que foi movida pelo adversário
        last_piece = board.piece_at(last_move.to_square)
        
        # Se não conseguirmos determinar a peça (por exemplo, se foi capturada em seguida),
        # tente adivinhar pelo padrão de movimento
        if not last_piece:
            # Tenta adivinhar pelo movimento:
            if abs(file_offset) <= 1 and abs(rank_offset) <= 1:
                # Provavelmente rei ou peão
                piece_type = chess.PAWN if rank_offset != 0 else chess.KING
            elif (abs(file_offset) == 1 and abs(rank_offset) == 2) or (abs(file_offset) == 2 and abs(rank_offset) == 1):
                # Movimento típico de cavalo
                piece_type = chess.KNIGHT
            elif abs(file_offset) == abs(rank_offset):
                # Movimento diagonal (bispo ou rainha)
                piece_type = chess.BISHOP
            elif file_offset == 0 or rank_offset == 0:
                # Movimento horizontal/vertical (torre ou rainha)
                piece_type = chess.ROOK
            else:
                # Não foi possível determinar, escolha aleatório
                piece_type = None
        else:
            piece_type = last_piece.piece_type
        
        # Lista de movimentos "miméticos" (mesmo padrão, mesma peça)
        mimic_moves = []
        semi_mimic_moves = []  # Mesma peça, qualquer movimento
        
        for move in moves:
            from_square = move.from_square
            to_square = move.to_square
            
            move_piece = board.piece_at(from_square)
            
            if not move_piece:
                continue  # Isso não deveria acontecer
            
            # Calcula o offset deste movimento
            move_from_file = chess.square_file(from_square)
            move_from_rank = chess.square_rank(from_square)
            move_to_file = chess.square_file(to_square)
            move_to_rank = chess.square_rank(to_square)
            
            move_file_offset = move_to_file - move_from_file
            move_rank_offset = move_to_rank - move_from_rank
            
            # Verifica se é o mesmo tipo de peça
            if move_piece.piece_type == piece_type:
                # Adiciona à lista de movimentos da mesma peça
                semi_mimic_moves.append(move)
                
                # Verifica se tem o mesmo padrão de movimento (mais ou menos, considerando espelhamento)
                if (move_file_offset == file_offset and move_rank_offset == rank_offset) or \
                   (move_file_offset == -file_offset and move_rank_offset == -rank_offset) or \
                   (move_file_offset == file_offset and move_rank_offset == -rank_offset) or \
                   (move_file_offset == -file_offset and move_rank_offset == rank_offset):
                    mimic_moves.append(move)
        
        # Escolhe na seguinte ordem de prioridade:
        # 1. Movimento com mesmo padrão e mesma peça
        # 2. Movimento com mesma peça
        # 3. Movimento aleatório
        if mimic_moves:
            return random.choice(mimic_moves)
        elif semi_mimic_moves:
            return random.choice(semi_mimic_moves)
        else:
            # Desiste da vida e move aleatoriamente
            return random.choice(moves)