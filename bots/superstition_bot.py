#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que joga baseado em superstições e crenças absurdas sobre o jogo."""

import chess
import random
import datetime
from bot import ChessBot, BotRegistry

@BotRegistry.register
class SuperstitionBot(ChessBot):
    """Bot que joga baseado em crenças supersticiosas sobre o xadrez."""
    
    @property
    def name(self) -> str:
        return "Superstition Bot"
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        moves = list(board.legal_moves)
        if not moves:
            return None
            
        # Dia da semana influencia a estratégia
        day_of_week = datetime.datetime.now().weekday()
        
        # Casas "amaldiçoadas" - muda de acordo com o dia da semana
        cursed_squares = []
        if day_of_week == 0:  # Segunda = a1, h1, a8, h8 (cantos)
            cursed_squares = [chess.A1, chess.H1, chess.A8, chess.H8]
        elif day_of_week == 1:  # Terça = casas centrais
            cursed_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        elif day_of_week == 2:  # Quarta = casas pretas
            cursed_squares = [sq for sq in chess.SQUARES if (chess.square_file(sq) + chess.square_rank(sq)) % 2 == 1]
        elif day_of_week == 3:  # Quinta = casas brancas
            cursed_squares = [sq for sq in chess.SQUARES if (chess.square_file(sq) + chess.square_rank(sq)) % 2 == 0]
        elif day_of_week == 4:  # Sexta = primeira e última coluna
            cursed_squares = [sq for sq in chess.SQUARES if chess.square_file(sq) in (0, 7)]
        elif day_of_week == 5:  # Sábado = primeira e última fileira
            cursed_squares = [sq for sq in chess.SQUARES if chess.square_rank(sq) in (0, 7)]
        else:  # Domingo = nenhuma casa é amaldiçoada (dia de sorte!)
            cursed_squares = []
        
        # Lista de "peças da sorte" baseada no número do movimento
        move_number = board.fullmove_number
        lucky_pieces = []
        if move_number % 7 == 1:
            lucky_pieces = [chess.PAWN]  # Peões são sortudos
        elif move_number % 7 == 2:
            lucky_pieces = [chess.KNIGHT]  # Cavalos são sortudos
        elif move_number % 7 == 3:
            lucky_pieces = [chess.BISHOP]  # Bispos são sortudos
        elif move_number % 7 == 4:
            lucky_pieces = [chess.ROOK]  # Torres são sortudas
        elif move_number % 7 == 5:
            lucky_pieces = [chess.QUEEN]  # Damas são sortudas
        elif move_number % 7 == 6:
            lucky_pieces = [chess.KING]  # Reis são sortudos
        else:
            lucky_pieces = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
        
        # Avalia os movimentos baseado em superstições
        good_moves = []
        neutral_moves = []
        bad_moves = []
        
        for move in moves:
            piece = board.piece_at(move.from_square)
            
            # Ignora movimentos se não encontramos a peça (não deve acontecer)
            if not piece:
                neutral_moves.append(move)
                continue
            
            # Se é uma captura, verifica se é "captura de boa sorte" (baseado no dia)
            is_lucky_capture = False
            if board.is_capture(move):
                captured_piece = board.piece_at(move.to_square)
                if captured_piece and day_of_week == captured_piece.piece_type:
                    is_lucky_capture = True
            
            # Peça movendo da casa amaldiçoada: ótimo
            # Peça movendo para casa amaldiçoada: péssimo
            # Peça da sorte se movendo: ótimo
            if move.from_square in cursed_squares:
                good_moves.append(move)
            elif move.to_square in cursed_squares:
                bad_moves.append(move)
            elif piece.piece_type in lucky_pieces:
                good_moves.append(move)
            elif is_lucky_capture:
                good_moves.append(move)
            else:
                neutral_moves.append(move)
        
        # Escolhe um movimento baseado nas superstições
        if good_moves and random.random() < 0.7:  # 70% de chance de escolher um movimento "bom"
            return random.choice(good_moves)
        elif neutral_moves and (not bad_moves or random.random() < 0.9):  # Evita movimentos "ruins"
            return random.choice(neutral_moves)
        elif bad_moves:
            return random.choice(bad_moves)
        else:
            # Se algo der errado, escolhe aleatoriamente
            return random.choice(moves)