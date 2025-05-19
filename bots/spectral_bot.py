#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que usa a heurística 'Ressonância Espectral' (RE)."""

import chess
import random
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh
from bot import ChessBot, BotRegistry

@BotRegistry.register
class SpectralBot(ChessBot):
    """
    Bot que avalia posições usando teoria espectral de grafos.
    
    Trata o tabuleiro como uma rede de controle, onde cada peça é um nó e sua influência 
    (ataque/defesa) são arestas. Usa teoria espectral de grafos para medir quão "coeso" e 
    "resiliente" é o controle versus o do oponente.
    """
    
    @property
    def name(self) -> str:
        return "Spectral Bot"
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        """Escolhe um movimento baseado na heurística de Ressonância Espectral."""
        moves = list(board.legal_moves)
        if not moves:
            return None
            
        # Avalia cada movimento possível
        best_moves = []
        best_score = float('-inf')
        
        for move in moves:
            # Simula o movimento
            board.push(move)
            
            # Calcula o score baseado no valor de Fiedler após o movimento
            score = self._evaluate_position(board)
            
            # Desfaz o movimento
            board.pop()
            
            # Atualiza os melhores movimentos
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        # Escolhe aleatoriamente entre os melhores movimentos
        return random.choice(best_moves)
    
    def _evaluate_position(self, board: chess.Board) -> float:
        """
        Avalia a posição calculando a diferença entre os valores de Fiedler
        dos subgrafos do jogador e do oponente.
        
        Args:
            board: Estado atual do tabuleiro
            
        Returns:
            Score: λ2,own - λ2,opp (valor de Fiedler próprio - valor de Fiedler do oponente)
        """
        # Calcula o valor de Fiedler para o subgrafo do jogador atual
        own_fiedler = self._calculate_fiedler_value(board, board.turn)
        
        # Calcula o valor de Fiedler para o subgrafo do oponente
        opp_fiedler = self._calculate_fiedler_value(board, not board.turn)
        
        # Retorna a diferença (próprio - oponente)
        return own_fiedler - opp_fiedler
    
    def _calculate_fiedler_value(self, board: chess.Board, color: bool) -> float:
        """
        Calcula o valor de Fiedler (segundo menor autovalor da matriz Laplaciana)
        do subgrafo formado pelas peças da cor especificada.
        
        Args:
            board: Estado atual do tabuleiro
            color: Cor das peças a considerar (True para brancas, False para pretas)
            
        Returns:
            O valor de Fiedler do subgrafo
        """
        # Identifica todas as peças da cor especificada
        pieces = {}
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == color:
                pieces[square] = piece
        
        # Se não há peças suficientes, retorna 0
        if len(pieces) < 2:
            return 0.0
        
        # Constrói a matriz de adjacência
        n = len(pieces)
        adj_matrix = np.zeros((n, n))
        
        # Lista de quadrados para mapear índices da matriz
        squares_list = list(pieces.keys())
        
        # Constrói o grafo ponderado
        for i, square1 in enumerate(squares_list):
            piece1 = pieces[square1]
            for j, square2 in enumerate(squares_list[i+1:], i+1):
                piece2 = pieces[square2]
                
                # Calcula o peso da aresta com base na influência mútua
                weight = self._calculate_edge_weight(board, square1, square2)
                
                # Atualiza a matriz de adjacência (simétrica)
                if weight > 0:
                    adj_matrix[i, j] = weight
                    adj_matrix[j, i] = weight
        
        # Calcula a matriz Laplaciana
        degree_matrix = np.diag(np.sum(adj_matrix, axis=1))
        laplacian = degree_matrix - adj_matrix
        
        # Calcula os autovalores da matriz Laplaciana
        try:
            # Usando scipy.sparse.linalg.eigsh para eficiência
            if n > 1:
                # Converte para matriz esparsa para melhor desempenho
                sparse_laplacian = sparse.csr_matrix(laplacian)
                eigenvalues = eigsh(sparse_laplacian, k=2, which='SM', return_eigenvectors=False)
                # O segundo menor autovalor é o valor de Fiedler (índice 1)
                fiedler_value = eigenvalues[1] if len(eigenvalues) > 1 else 0.0
            else:
                fiedler_value = 0.0
        except Exception:
            # Fallback para cálculo tradicional se o eigsh falhar
            try:
                eigenvalues = np.linalg.eigvalsh(laplacian)
                # Organiza os autovalores em ordem crescente
                eigenvalues.sort()
                # O segundo menor autovalor é o valor de Fiedler (índice 1)
                fiedler_value = eigenvalues[1] if len(eigenvalues) > 1 else 0.0
            except Exception:
                # Em caso de erro, retorna um valor padrão
                fiedler_value = 0.0
        
        # Limita o valor para evitar números extremos
        return max(0.0, min(10.0, fiedler_value))
    
    def _calculate_edge_weight(self, board: chess.Board, square1: int, square2: int) -> float:
        """
        Calcula o peso da aresta entre duas peças com base em sua influência mútua.
        
        Args:
            board: Estado atual do tabuleiro
            square1: Quadrado da primeira peça
            square2: Quadrado da segunda peça
            
        Returns:
            Peso da aresta entre as duas peças
        """
        # Se as peças estão muito longe, não há aresta
        distance = self._calculate_distance(board, square1, square2)
        if distance > 5:  # Limite arbitrário para o tamanho do grafo
            return 0.0
        
        # Peso = 1 / (distância * 0.5 + 0.5)
        weight = 1.0 / (distance * 0.5 + 0.5)
        return weight
    
    def _calculate_distance(self, board: chess.Board, square1: int, square2: int) -> int:
        """
        Calcula a distância entre duas casas no tabuleiro em termos de movimento mínimo.
        
        Args:
            board: Estado atual do tabuleiro
            square1: Primeira casa
            square2: Segunda casa
            
        Returns:
            A distância mínima em movimentos entre as casas
        """
        piece = board.piece_at(square1)
        if not piece:
            return float('inf')
        
        # Implementação simplificada: distância Manhattan ou diagonal
        file1, rank1 = chess.square_file(square1), chess.square_rank(square1)
        file2, rank2 = chess.square_file(square2), chess.square_rank(square2)
        
        file_diff = abs(file1 - file2)
        rank_diff = abs(rank1 - rank2)
        
        # Distância ajustada pelo tipo de peça
        if piece.piece_type == chess.KNIGHT:
            # Movimento do cavalo é especial, estimativa aproximada
            # Número mínimo de movimentos para um cavalo chegar a qualquer ponto do tabuleiro
            if file_diff == 0 and rank_diff == 0:
                return 0
            elif (file_diff == 1 and rank_diff == 2) or (file_diff == 2 and rank_diff == 1):
                return 1
            elif file_diff + rank_diff <= 3:
                return 2
            else:
                return 3
        elif piece.piece_type == chess.BISHOP:
            # Bispo se move na diagonal
            return float('inf') if file_diff != rank_diff else file_diff
        elif piece.piece_type == chess.ROOK:
            # Torre se move em linha reta
            return float('inf') if file_diff != 0 and rank_diff != 0 else file_diff + rank_diff
        elif piece.piece_type == chess.QUEEN:
            # Rainha pode se mover em qualquer direção
            return max(file_diff, rank_diff) if file_diff == rank_diff or file_diff == 0 or rank_diff == 0 else file_diff + rank_diff
        elif piece.piece_type == chess.KING:
            # Rei se move uma casa em qualquer direção
            return max(file_diff, rank_diff)
        else:  # Peão
            # Simplificação extrema para peão: só conta a distância
            return file_diff + rank_diff