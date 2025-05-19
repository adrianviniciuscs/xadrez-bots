#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bot de xadrez que usa a heurística 'Fractal Cluster Expansion' (FCE)."""

import chess
import random
import numpy as np
from bot import ChessBot, BotRegistry

@BotRegistry.register
class FractalBot(ChessBot):
    """
    Bot que avalia posições usando dimensão fractal das distribuições de peças.
    
    Trata o tabuleiro como um objeto geométrico vivo. Quanto mais "espalhada" e "complexa" for 
    a distribuição das suas peças (e ao mesmo tempo mais "concentrada" e "simples" a do oponente), 
    melhor seu controle e flexibilidade estratégica.
    """
    
    @property
    def name(self) -> str:
        return "Fractal Bot"
    
    def choose_move(self, board: chess.Board) -> chess.Move:
        """Escolhe um movimento baseado na heurística FCE."""
        moves = list(board.legal_moves)
        if not moves:
            return None
            
        # Avalia cada movimento possível
        best_moves = []
        best_score = float('-inf')
        
        for move in moves:
            # Simula o movimento
            board.push(move)
            
            # Calcula o score baseado na dimensão fractal após o movimento
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
        Avalia a posição calculando a diferença entre as dimensões fractais
        das distribuições de peças do jogador e do oponente.
        
        Args:
            board: Estado atual do tabuleiro
            
        Returns:
            Score: Down - Dopp (dimensão fractal própria - dimensão fractal do oponente)
        """
        # Calcula a dimensão fractal para as peças do jogador atual
        own_dimension = self._calculate_fractal_dimension(board, board.turn)
        
        # Calcula a dimensão fractal para as peças do oponente
        opp_dimension = self._calculate_fractal_dimension(board, not board.turn)
        
        # Retorna a diferença (própria - oponente)
        return own_dimension - opp_dimension
    
    def _calculate_fractal_dimension(self, board: chess.Board, color: bool) -> float:
        """
        Calcula a dimensão fractal da distribuição de peças usando o método box-counting.
        
        Args:
            board: Estado atual do tabuleiro
            color: Cor das peças a considerar (True para brancas, False para pretas)
            
        Returns:
            A dimensão fractal estimada da distribuição de peças
        """
        # Cria um mapa de ocupação do tabuleiro (1 para presença de peça, 0 para ausência)
        occupation_map = np.zeros((8, 8), dtype=int)
        
        # Preenche o mapa com as posições das peças da cor especificada
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == color:
                file_idx = chess.square_file(square)
                rank_idx = chess.square_rank(square)
                occupation_map[rank_idx][file_idx] = 1
        
        # Escalas para o box-counting: 1x1, 2x2 e 4x4
        scales = [1, 2, 4]
        counts = []
        
        for scale in scales:
            # Conta as caixas não vazias em cada escala
            if scale == 1:
                # Para escala 1x1, é simplesmente a contagem de peças
                counts.append(np.sum(occupation_map))
            else:
                # Para escalas maiores, particiona o tabuleiro em caixas de tamanho scale x scale
                count = 0
                for i in range(0, 8, scale):
                    for j in range(0, 8, scale):
                        # Verifica se a caixa contém pelo menos uma peça
                        box = occupation_map[i:min(i+scale, 8), j:min(j+scale, 8)]
                        if np.any(box):
                            count += 1
                counts.append(count)
        
        # Evita divisão por zero e casos com poucas peças
        if len(counts) < 2 or counts[0] <= 1:
            return 0.0
        
        # Calcula a dimensão fractal usando regressão linear
        x = np.log(1.0 / np.array(scales, dtype=float))
        y = np.log(np.array(counts, dtype=float))
        
        # Evita problemas com log(0)
        valid_indices = np.isfinite(y)
        if np.sum(valid_indices) < 2:
            return 0.0
            
        x = x[valid_indices]
        y = y[valid_indices]
        
        # Coeficiente angular da reta é a estimativa da dimensão fractal
        if len(x) >= 2:
            # Usa polifit para regressão linear
            coeffs = np.polyfit(x, y, 1)
            dimension = coeffs[0]  # Coeficiente angular
            return max(0.0, min(2.0, dimension))  # Limita entre 0 e 2
        else:
            return 0.0