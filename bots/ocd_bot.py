#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez com TOC que tenta organizar suas peças em formações perfeitas."""

import chess
import random
from bot import ChessBot, BotRegistry

@BotRegistry.register
class OCDBot(ChessBot):
    """
    Bot com Transtorno Obsessivo-Compulsivo de Xadrez que tenta alinhar suas peças
    em formações "perfeitas", mesmo que isso prejudique sua estratégia.
    """
    
    @property
    def name(self) -> str:
        return "OCD Bot"
    
    def __init__(self):
        super().__init__()
        # Escolhe uma fileira alvo para os peões (entre 2 e 6)
        self.target_pawn_rank = random.randint(2, 6)
        # Escolhe uma coluna alvo para as torres (0-7 para a-h)
        self.target_rook_file = random.randint(0, 7)
        # Escolhe padrão para os cavalos (diagonal ou mesma fileira)
        self.knight_pattern = random.choice(["diagonal", "rank", "file"])
        # Metas de formação atingidas
        self.formation_completed = False
        # Contador de turnos
        self.turn_count = 0
        
    def choose_move(self, board: chess.Board) -> chess.Move:
        moves = list(board.legal_moves)
        if not moves:
            return None
            
        # Incrementa o contador de turnos
        self.turn_count += 1
        
        # A cada 15 turnos, muda o objetivo para manter as coisas interessantes
        if self.turn_count % 15 == 0:
            self.target_pawn_rank = random.randint(2, 6)
            self.target_rook_file = random.randint(0, 7)
            self.knight_pattern = random.choice(["diagonal", "rank", "file"])
            print(f"{self.name}: Nova formação desejada! Peões na fileira {self.target_pawn_rank+1}, Torres na coluna {chess.FILE_NAMES[self.target_rook_file]}")
        
        # Verifica se a formação está completa
        self.formation_completed = self._check_formation(board)
        
        # Se a formação estiver completa, podemos atacar
        if self.formation_completed:
            return self._choose_attack_move(board, moves)
            
        # Caso contrário, corrigimos a formação
        return self._choose_formation_move(board, moves)
    
    def _check_formation(self, board):
        """Verifica se todas as peças estão na formação desejada."""
        # Contadores para peças em formação
        pawns_in_formation = 0
        rooks_in_formation = 0
        knights_in_formation = 0
        
        # Total de cada tipo de peça
        total_pawns = 0
        total_rooks = 0
        total_knights = 0
        
        # Verifica cada peça no tabuleiro
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece or piece.color != board.turn:
                continue
                
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            
            if piece.piece_type == chess.PAWN:
                total_pawns += 1
                if rank == self.target_pawn_rank:
                    pawns_in_formation += 1
                    
            elif piece.piece_type == chess.ROOK:
                total_rooks += 1
                if file == self.target_rook_file:
                    rooks_in_formation += 1
                    
            elif piece.piece_type == chess.KNIGHT:
                total_knights += 1
                # Diferentes formações para cavalos
                if self.knight_pattern == "diagonal":
                    if file == rank or file == 7-rank:
                        knights_in_formation += 1
                elif self.knight_pattern == "rank":
                    if rank == self.target_pawn_rank:
                        knights_in_formation += 1
                elif self.knight_pattern == "file":
                    if file == self.target_rook_file:
                        knights_in_formation += 1
        
        # Considera formação completa se pelo menos 70% das peças estiverem alinhadas
        pawn_completion = pawns_in_formation / total_pawns if total_pawns > 0 else 1.0
        rook_completion = rooks_in_formation / total_rooks if total_rooks > 0 else 1.0
        knight_completion = knights_in_formation / total_knights if total_knights > 0 else 1.0
        
        # Média ponderada dando mais peso aos peões
        total_completion = (pawn_completion * 0.6 + rook_completion * 0.2 + knight_completion * 0.2)
        
        return total_completion >= 0.7
    
    def _choose_formation_move(self, board, moves):
        """Escolhe movimento para melhorar a formação."""
        formation_moves = []
        capture_formation_moves = []
        
        for move in moves:
            from_square = move.from_square
            to_square = move.to_square
            piece = board.piece_at(from_square)
            
            if not piece:
                continue
                
            to_rank = chess.square_rank(to_square)
            to_file = chess.square_file(to_square)
            
            # Para peões, queremos alcançar a fileira alvo
            if piece.piece_type == chess.PAWN and to_rank == self.target_pawn_rank:
                if board.is_capture(move):
                    capture_formation_moves.append(move)
                else:
                    formation_moves.append(move)
                    
            # Para torres, queremos alcançar a coluna alvo
            elif piece.piece_type == chess.ROOK and to_file == self.target_rook_file:
                if board.is_capture(move):
                    capture_formation_moves.append(move)
                else:
                    formation_moves.append(move)
                    
            # Para cavalos, depende do padrão escolhido
            elif piece.piece_type == chess.KNIGHT:
                in_pattern = False
                if self.knight_pattern == "diagonal" and (to_file == to_rank or to_file == 7-to_rank):
                    in_pattern = True
                elif self.knight_pattern == "rank" and to_rank == self.target_pawn_rank:
                    in_pattern = True
                elif self.knight_pattern == "file" and to_file == self.target_rook_file:
                    in_pattern = True
                    
                if in_pattern:
                    if board.is_capture(move):
                        capture_formation_moves.append(move)
                    else:
                        formation_moves.append(move)
        
        # Prioriza capturas que também melhoram a formação
        if capture_formation_moves:
            return random.choice(capture_formation_moves)
            
        # Em seguida, prioriza movimentos que melhoram a formação
        if formation_moves:
            return random.choice(formation_moves)
            
        # Se não conseguirmos melhorar a formação, jogaremos normalmente
        # Prioriza capturas > xeques > movimentos normais
        capture_moves = [move for move in moves if board.is_capture(move)]
        check_moves = [move for move in moves if board.gives_check(move)]
        
        if capture_moves:
            return random.choice(capture_moves)
        elif check_moves:
            return random.choice(check_moves)
        else:
            return random.choice(moves)
    
    def _choose_attack_move(self, board, moves):
        """Escolhe movimento de ataque quando a formação estiver completa."""
        # Quando em formação, priorizamos capturas e xeques
        capture_moves = [move for move in moves if board.is_capture(move)]
        check_moves = [move for move in moves if board.gives_check(move)]
        
        # Movimento que mantém a formação
        formation_moves = []
        
        for move in moves:
            from_square = move.from_square
            to_square = move.to_square
            piece = board.piece_at(from_square)
            
            if not piece:
                continue
                
            to_rank = chess.square_rank(to_square)
            to_file = chess.square_file(to_square)
            
            # Verifica se o movimento mantém a formação para cada tipo de peça
            maintain_formation = False
            
            if piece.piece_type == chess.PAWN:
                if to_rank == self.target_pawn_rank:
                    maintain_formation = True
            elif piece.piece_type == chess.ROOK:
                if to_file == self.target_rook_file:
                    maintain_formation = True
            elif piece.piece_type == chess.KNIGHT:
                if (self.knight_pattern == "diagonal" and (to_file == to_rank or to_file == 7-to_rank)) or \
                   (self.knight_pattern == "rank" and to_rank == self.target_pawn_rank) or \
                   (self.knight_pattern == "file" and to_file == self.target_rook_file):
                    maintain_formation = True
            
            if maintain_formation:
                formation_moves.append(move)
        
        # Prioriza capturas > xeques > movimentos que mantêm a formação > outros
        if capture_moves:
            # Encontra capturas que também mantêm a formação
            maintain_formation_captures = [move for move in capture_moves if move in formation_moves]
            if maintain_formation_captures:
                return random.choice(maintain_formation_captures)
            return random.choice(capture_moves)
        elif check_moves:
            # Encontra xeques que também mantêm a formação
            maintain_formation_checks = [move for move in check_moves if move in formation_moves]
            if maintain_formation_checks:
                return random.choice(maintain_formation_checks)
            return random.choice(check_moves)
        elif formation_moves:
            return random.choice(formation_moves)
        else:
            # Movimento aleatório como último recurso
            return random.choice(moves)