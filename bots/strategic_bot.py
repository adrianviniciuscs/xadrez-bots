#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que combina múltiplas estratégias avançadas para vencer qualquer oponente."""

import chess
import random
import numpy as np
from bot import ChessBot, BotRegistry

@BotRegistry.register
class StrategicBot(ChessBot):
    """
    Bot estratégico que combina avaliação material, posicional e táticas avançadas.
    
    Utiliza uma combinação de:
    1. Avaliação material precisa
    2. Tabelas de posição para cada tipo de peça
    3. Análise de segurança do rei
    4. Controle do centro
    5. Mobilidade das peças
    6. Estrutura de peões
    """
    
    @property
    def name(self) -> str:
        return "Strategic Bot"
    
    def __init__(self):
        super().__init__()
        # Valores das peças (padrão + ajustes)
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000  # Valor alto para proteger o rei a todo custo
        }
        
        # Tabelas de valor posicional para cada tipo de peça
        # Peões: valoriza avanço e controle do centro
        self.pawn_table = np.array([
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [ 5,  5, 10, 25, 25, 10,  5,  5],
            [ 0,  0,  0, 20, 20,  0,  0,  0],
            [ 5, -5,-10,  0,  0,-10, -5,  5],
            [ 5, 10, 10,-20,-20, 10, 10,  5],
            [ 0,  0,  0,  0,  0,  0,  0,  0]
        ])
        
        # Cavalos: valoriza posições próximas ao centro e evita bordas
        self.knight_table = np.array([
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ])
        
        # Bispos: valoriza diagonais longas e evita cantos
        self.bishop_table = np.array([
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5,  5,  5,  5,  5,-10],
            [-10,  0,  5,  0,  0,  5,  0,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ])
        
        # Torres: valoriza colunas abertas e 7ª fileira
        self.rook_table = np.array([
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [ 5, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [ 0,  0,  0,  5,  5,  0,  0,  0]
        ])
        
        # Dama: combina mobilidade com segurança
        self.queen_table = np.array([
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [ -5,  0,  5,  5,  5,  5,  0, -5],
            [  0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ])
        
        # Rei: valoriza segurança e roque no início, atividade no final
        self.king_table_midgame = np.array([
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [ 20, 20,  0,  0,  0,  0, 20, 20],
            [ 20, 30, 10,  0,  0, 10, 30, 20]
        ])
        
        self.king_table_endgame = np.array([
            [-50,-40,-30,-20,-20,-30,-40,-50],
            [-30,-20,-10,  0,  0,-10,-20,-30],
            [-30,-10, 20, 30, 30, 20,-10,-30],
            [-30,-10, 30, 40, 40, 30,-10,-30],
            [-30,-10, 30, 40, 40, 30,-10,-30],
            [-30,-10, 20, 30, 30, 20,-10,-30],
            [-30,-30,  0,  0,  0,  0,-30,-30],
            [-50,-30,-30,-30,-30,-30,-30,-50]
        ])
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        """Escolhe o melhor movimento baseado na avaliação estratégica do tabuleiro."""
        moves = list(board.legal_moves)
        if not moves:
            return None
            
        # Avalia cada movimento possível
        best_moves = []
        best_score = float('-inf')
        
        for move in moves:
            # Simula o movimento
            board.push(move)
            
            # Calcula o score baseado na posição após o movimento
            score = self._evaluate_position(board)
            
            # Desfaz o movimento
            board.pop()
            
            # Atualiza os melhores movimentos
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        # Se tivermos vários movimentos com pontuação igual, priorizamos certos tipos
        if len(best_moves) > 1:
            for priority_move in best_moves:
                # Prioridade 1: Xeque-mate (obviamente)
                board.push(priority_move)
                if board.is_checkmate():
                    board.pop()
                    return priority_move
                board.pop()
                
                # Prioridade 2: Captura de peça valiosa
                if board.is_capture(priority_move):
                    capture_square = priority_move.to_square
                    captured_piece = board.piece_at(capture_square)
                    if captured_piece and self.piece_values.get(captured_piece.piece_type, 0) >= 300:  # Pelo menos um cavalo/bispo
                        return priority_move
                
                # Prioridade 3: Promoção de peão
                if priority_move.promotion == chess.QUEEN:
                    return priority_move
        
        # Escolhe aleatoriamente entre os melhores movimentos
        return random.choice(best_moves)
    
    def _evaluate_position(self, board: chess.Board) -> float:
        """
        Avalia a posição atual do tabuleiro.
        
        Args:
            board: Estado atual do tabuleiro
            
        Returns:
            Uma pontuação da posição (positivo favorece o jogador atual)
        """
        if board.is_checkmate():
            # Xeque-mate é o melhor/pior resultado possível
            return -10000 if board.turn else 10000
            
        if board.is_stalemate() or board.is_insufficient_material():
            # Empate - neutro
            return 0
        
        # Contagem de material
        material_score = self._evaluate_material(board)
        
        # Avaliação posicional
        position_score = self._evaluate_piece_positions(board)
        
        # Mobilidade (número de movimentos legais)
        mobility_score = self._evaluate_mobility(board)
        
        # Segurança do rei
        king_safety_score = self._evaluate_king_safety(board)
        
        # Estrutura de peões
        pawn_structure_score = self._evaluate_pawn_structure(board)
        
        # Combinar todas as avaliações com pesos
        total_score = (
            material_score * 1.0 +  # Material é o mais importante
            position_score * 0.3 +  # Posição das peças
            mobility_score * 0.2 +  # Mobilidade
            king_safety_score * 0.4 +  # Segurança do rei
            pawn_structure_score * 0.1  # Estrutura de peões
        )
        
        # Retorna o score na perspectiva do jogador atual
        return total_score if board.turn else -total_score
    
    def _evaluate_material(self, board: chess.Board) -> float:
        """Avalia o balanço de material no tabuleiro."""
        score = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.piece_values.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
        
        return score
    
    def _evaluate_piece_positions(self, board: chess.Board) -> float:
        """Avalia a qualidade das posições das peças usando tabelas de valor posicional."""
        score = 0
        
        # Determina se estamos no final do jogo
        endgame = self._is_endgame(board)
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece:
                continue
                
            # Obtém a posição na tabela (invertida para as pretas)
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            
            # Inverte o rank para peças pretas
            position_rank = rank if piece.color else 7 - rank
            
            # Avalia a posição de acordo com o tipo de peça
            position_value = 0
            
            if piece.piece_type == chess.PAWN:
                position_value = self.pawn_table[position_rank][file]
            elif piece.piece_type == chess.KNIGHT:
                position_value = self.knight_table[position_rank][file]
            elif piece.piece_type == chess.BISHOP:
                position_value = self.bishop_table[position_rank][file]
            elif piece.piece_type == chess.ROOK:
                position_value = self.rook_table[position_rank][file]
            elif piece.piece_type == chess.QUEEN:
                position_value = self.queen_table[position_rank][file]
            elif piece.piece_type == chess.KING:
                # Use a tabela apropriada com base no estágio do jogo
                if endgame:
                    position_value = self.king_table_endgame[position_rank][file]
                else:
                    position_value = self.king_table_midgame[position_rank][file]
            
            # Adiciona o valor da posição ao score (positivo para brancas, negativo para pretas)
            if piece.color == chess.WHITE:
                score += position_value
            else:
                score -= position_value
        
        return score
    
    def _evaluate_mobility(self, board: chess.Board) -> float:
        """Avalia a mobilidade (número de movimentos legais disponíveis)."""
        # Salva o turno original
        original_turn = board.turn
        
        # Conta movimentos para as brancas
        board.turn = chess.WHITE
        white_mobility = len(list(board.legal_moves))
        
        # Conta movimentos para as pretas
        board.turn = chess.BLACK
        black_mobility = len(list(board.legal_moves))
        
        # Restaura o turno original
        board.turn = original_turn
        
        # Retorna a diferença de mobilidade (positiva para as brancas)
        return white_mobility - black_mobility
    
    def _evaluate_king_safety(self, board: chess.Board) -> float:
        """Avalia a segurança do rei."""
        score = 0
        
        # Localiza os reis
        white_king_square = board.king(chess.WHITE)
        black_king_square = board.king(chess.BLACK)
        
        # Se algum rei não for encontrado (não deve acontecer em um jogo normal), retorna 0
        if white_king_square is None or black_king_square is None:
            return 0
        
        # Verifica o número de peças que atacam o rei
        # Guarda o turno original
        original_turn = board.turn
        
        # Número de atacantes aos reis
        board.turn = chess.BLACK  # Simulamos turno das pretas para verificar ataques ao rei branco
        white_king_attackers = len(list(board.attackers(chess.BLACK, white_king_square)))
        
        board.turn = chess.WHITE  # Simulamos turno das brancas para verificar ataques ao rei preto
        black_king_attackers = len(list(board.attackers(chess.WHITE, black_king_square)))
        
        # Restaura o turno original
        board.turn = original_turn
        
        # Penaliza para cada atacante (-50 pontos por atacante)
        score -= white_king_attackers * 50
        score += black_king_attackers * 50
        
        # Verifica xeque
        if board.turn == chess.WHITE and board.is_check():
            score -= 30  # Penalidade para as brancas estarem em xeque
        elif board.turn == chess.BLACK and board.is_check():
            score += 30  # Penalidade para as pretas estarem em xeque
            
        # Avalia proteção do rei por peças aliadas
        white_king_defenders = len(list(board.attackers(chess.WHITE, white_king_square)))
        black_king_defenders = len(list(board.attackers(chess.BLACK, black_king_square)))
        
        score += white_king_defenders * 10  # Bônus para proteção do rei branco
        score -= black_king_defenders * 10  # Bônus para proteção do rei preto
        
        # Peões na frente do rei após roque (proteção)
        white_king_file = chess.square_file(white_king_square)
        black_king_file = chess.square_file(black_king_square)
        white_king_rank = chess.square_rank(white_king_square)
        black_king_rank = chess.square_rank(black_king_square)
        
        # Verifica roque
        if white_king_file in (2, 6) and white_king_rank == 0:  # Rei branco fez roque
            for f in range(max(0, white_king_file - 1), min(8, white_king_file + 2)):
                pawn_square = chess.square(f, 1)  # Peão na 2ª fileira
                if board.piece_at(pawn_square) == chess.Piece(chess.PAWN, chess.WHITE):
                    score += 15  # Bônus para peões protegendo o rei depois do roque
                    
        if black_king_file in (2, 6) and black_king_rank == 7:  # Rei preto fez roque
            for f in range(max(0, black_king_file - 1), min(8, black_king_file + 2)):
                pawn_square = chess.square(f, 6)  # Peão na 7ª fileira
                if board.piece_at(pawn_square) == chess.Piece(chess.PAWN, chess.BLACK):
                    score -= 15  # Bônus para peões protegendo o rei depois do roque
        
        return score
    
    def _evaluate_pawn_structure(self, board: chess.Board) -> float:
        """Avalia a estrutura de peões."""
        score = 0
        
        # Conta peões por coluna para identificar peões dobrados
        white_pawn_files = [0] * 8
        black_pawn_files = [0] * 8
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN:
                file = chess.square_file(square)
                if piece.color == chess.WHITE:
                    white_pawn_files[file] += 1
                else:
                    black_pawn_files[file] += 1
        
        # Penalidade para peões dobrados (-10 por peão extra na mesma coluna)
        for file_count in white_pawn_files:
            if file_count > 1:
                score -= (file_count - 1) * 10
                
        for file_count in black_pawn_files:
            if file_count > 1:
                score += (file_count - 1) * 10
        
        # Identifica peões isolados
        for file in range(8):
            # Peão branco está isolado se não há peões brancos nas colunas adjacentes
            if white_pawn_files[file] > 0:
                isolated = (file == 0 or white_pawn_files[file-1] == 0) and (file == 7 or white_pawn_files[file+1] == 0)
                if isolated:
                    score -= 15 * white_pawn_files[file]  # Penalidade para peões isolados
                    
            # Peão preto está isolado se não há peões pretos nas colunas adjacentes
            if black_pawn_files[file] > 0:
                isolated = (file == 0 or black_pawn_files[file-1] == 0) and (file == 7 or black_pawn_files[file+1] == 0)
                if isolated:
                    score += 15 * black_pawn_files[file]  # Penalidade para peões isolados
        
        # Identifica peões avançados
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN:
                rank = chess.square_rank(square)
                if piece.color == chess.WHITE:
                    # Bônus para peões avançados (quanto mais avançado, maior o bônus)
                    score += rank * 5
                else:
                    # Para peões pretos, o rank 7 é o mais próximo da promoção
                    score -= (7 - rank) * 5
        
        return score
    
    def _is_endgame(self, board: chess.Board) -> bool:
        """Determina se estamos no final do jogo."""
        # Contagem de peças importantes (dama e torre)
        white_major_pieces = 0
        black_major_pieces = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece:
                continue
                
            if piece.piece_type in (chess.QUEEN, chess.ROOK):
                if piece.color == chess.WHITE:
                    white_major_pieces += 1
                else:
                    black_major_pieces += 1
        
        # Considera endgame se ambos os lados têm 0 ou 1 peça importante
        return white_major_pieces <= 1 and black_major_pieces <= 1