#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que força peças a retornarem para sua posição original em até 3 jogadas."""

import chess
import random
from bot import ChessBot, BotRegistry

@BotRegistry.register
class ReturnLineBot(ChessBot):
    """
    Bot que obriga suas peças a voltarem para a posição original em até 3 jogadas.
    Peças que não conseguirem retornar ficam "presas" e não podem mais ser movidas.
    """
    
    @property
    def name(self) -> str:
        return "Return Line Bot"
    
    def __init__(self):
        super().__init__()
        # Dicionário para rastrear as peças movidas
        # {square: (turno_de_saída, quadrado_original, turnos_restantes_para_retorno)}
        self.moved_pieces = {}
        # Conjunto de peças presas (que não conseguiram retornar)
        self.trapped_pieces = set()
        # Posição inicial das peças (será preenchida ao iniciar jogo)
        self.original_positions = {}
        # Número do turno atual
        self.current_turn = 0
        # Indica se as posições originais já foram registradas
        self.positions_recorded = False
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        moves = list(board.legal_moves)
        if not moves:
            return None
            
        # Incrementa o contador de turnos
        self.current_turn += 1
        
        # Se for o primeiro movimento, registra as posições originais das peças
        if not self.positions_recorded:
            self._record_original_positions(board)
            self.positions_recorded = True
        
        # Atualiza o contador de turnos restantes para retorno
        self._update_return_counters()
        
        # Lista de movimentos prioritários (retornando à posição original)
        return_moves = []
        # Lista de movimentos permitidos (peças que ainda não foram movidas ou que podem ser movidas)
        allowed_moves = []
        # Lista de movimentos de emergência (quando não há alternativa)
        emergency_moves = []
        
        for move in moves:
            from_square = move.from_square
            piece = board.piece_at(from_square)
            
            # Ignora peças que estão presas
            if from_square in self.trapped_pieces:
                continue
                
            # Verifica se este movimento é um retorno à posição original
            if from_square in self.moved_pieces:
                original_square = self.moved_pieces[from_square][1]
                if move.to_square == original_square:
                    # Este movimento retorna a peça à sua posição original!
                    return_moves.append(move)
                elif self.moved_pieces[from_square][2] > 1:
                    # Esta peça ainda tem tempo para retornar
                    allowed_moves.append(move)
            else:
                # Peça ainda não movida, pode se mover livremente
                allowed_moves.append(move)
                
            # Movimentos de emergência incluem todos os movimentos possíveis,
            # mesmo com peças presas (usado apenas se não houver alternativa)
            emergency_moves.append(move)
        
        # Prioriza retornar peças à posição original
        if return_moves:
            chosen_move = random.choice(return_moves)
            # Remove a peça da lista de peças movidas quando retorna
            if chosen_move.from_square in self.moved_pieces and chosen_move.to_square == self.moved_pieces[chosen_move.from_square][1]:
                print(f"{self.name}: Peça retornou à sua posição original!")
                del self.moved_pieces[chosen_move.from_square]
            return chosen_move
            
        # Se não há retornos, usa movimentos permitidos
        if allowed_moves:
            chosen_move = random.choice(allowed_moves)
            # Se esta é uma peça que ainda não moveu, registra-a
            if chosen_move.from_square not in self.moved_pieces:
                original_square = chosen_move.from_square
                self.moved_pieces[chosen_move.to_square] = (self.current_turn, original_square, 3)
                print(f"{self.name}: Nova peça movida, deve retornar em 3 turnos!")
            else:
                # Atualiza a posição da peça já movida
                original_exit_turn, original_square, remaining_turns = self.moved_pieces.pop(chosen_move.from_square)
                self.moved_pieces[chosen_move.to_square] = (original_exit_turn, original_square, remaining_turns)
            return chosen_move
            
        # Se nenhum movimento é permitido, temos emergência
        if emergency_moves:
            print(f"{self.name}: EMERGÊNCIA - Movendo peça presa (contra as regras)!")
            return random.choice(emergency_moves)
            
        # Isso não deveria acontecer
        return random.choice(moves)
    
    def _record_original_positions(self, board):
        """Registra as posições originais de todas as peças no início do jogo."""
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == board.turn:
                self.original_positions[square] = piece.piece_type
    
    def _update_return_counters(self):
        """Atualiza os contadores de turnos restantes para retorno de cada peça."""
        # Cria uma cópia das chaves para poder modificar durante a iteração
        moved_squares = list(self.moved_pieces.keys())
        
        for square in moved_squares:
            exit_turn, original_square, turns_remaining = self.moved_pieces[square]
            
            # Decrementa o contador
            turns_remaining -= 1
            
            if turns_remaining <= 0:
                # A peça não conseguiu retornar a tempo e fica presa
                print(f"{self.name}: Peça presa! Não conseguiu retornar a tempo!")
                self.trapped_pieces.add(square)
                del self.moved_pieces[square]
            else:
                # Atualiza o contador
                self.moved_pieces[square] = (exit_turn, original_square, turns_remaining)