#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que usa fórmulas matemáticas absurdas para escolher seus movimentos."""

import chess
import math
import random
from datetime import datetime
from bot import ChessBot, BotRegistry

@BotRegistry.register
class MathBot(ChessBot):
    """Bot que escolhe movimentos baseado em fórmulas matemáticas absurdamente complexas."""
    
    @property
    def name(self) -> str:
        return "Math Bot"
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        moves = list(board.legal_moves)
        
        if not moves:
            return None
            
        # Constantes matemáticas bizarras para nossa fórmula
        pi = math.pi
        phi = (1 + math.sqrt(5)) / 2  # Número áureo
        e = math.e  # Número de Euler
        
        # Fatores de tempo
        current_time = datetime.now()
        hour_factor = current_time.hour / 12 * pi
        minute_factor = current_time.minute / 30 * e
        second_factor = current_time.second / 30 * phi
        
        # Fatores do tabuleiro
        board_factor = len(list(board.piece_map())) / 32 * e  # Densidade do tabuleiro
        turn_factor = board.fullmove_number * phi / 10
        check_factor = 2 if board.is_check() else 1
        
        # Um valor de "aleatoriedade controlada" baseado em todos esses fatores
        magic_number = abs(math.sin(hour_factor) * math.cos(minute_factor) * 
                        math.tan(second_factor + 0.1) * board_factor * 
                        turn_factor * check_factor) % 1.0
                        
        # Cada quadrado no tabuleiro tem um valor baseado em sua posição
        def square_value(square):
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            
            # Valor baseado no padrão espiralado da sequência de Fibonacci
            return (phi ** (file+1) * math.sin(rank * pi/4)) % 1.0
        
        # Avaliação única para cada movimento baseada em:
        # - A coordenada de origem
        # - A coordenada de destino
        # - Nosso número mágico
        # - Série de Taylor para operações trigonométricas (desnecessariamente complicado)
        def evaluate_move(move):
            from_square = move.from_square
            to_square = move.to_square
            
            # Valores dos quadrados
            from_value = square_value(from_square)
            to_value = square_value(to_square)
            
            # Computação bizarra baseada em séries truncadas e operações de ponto flutuante
            value = (math.sin(from_value * pi) * math.cos(to_value * pi) * 
                    math.exp(magic_number * e / 10) * 
                    math.log(board_factor + 1) * 
                    (phi ** (abs(from_square - to_square) % 8) / 10))
            
            # Adiciona fatores especiais para capturas e promoções
            if board.is_capture(move):
                captured = board.piece_at(to_square)
                if captured:
                    value *= (captured.piece_type ** 2 / 36)  # Tipo da peça ao quadrado
            
            if move.promotion:
                value *= (move.promotion ** 2 / 25)
            
            # Termo adicional baseado na coordenada numérica da casa
            # Isso é totalmente arbitrário e só para tornar a fórmula mais absurda
            value += math.sqrt(from_square * to_square + 1) / 64
            
            return value
        
        # Avalia todos os movimentos com nossa fórmula absurda
        scored_moves = [(move, evaluate_move(move)) for move in moves]
        
        # A seleção final é baseada em um método de roleta
        # onde as probabilidades são baseadas nos valores calculados
        total_score = sum(abs(score) for _, score in scored_moves) or 1.0
        probabilities = [abs(score)/total_score for _, score in scored_moves]
        
        # Escolhe um movimento com base nas probabilidades calculadas
        try:
            chosen_move = random.choices([move for move, _ in scored_moves], weights=probabilities)[0]
            return chosen_move
        except Exception:
            # Fallback se algo der errado com nossa matemática maluca
            return random.choice(moves)