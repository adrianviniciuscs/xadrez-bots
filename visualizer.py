#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Visualizador de partidas de xadrez usando Pygame
"""

import os
import pygame
import chess
import chess.svg
import cairosvg
import io
from PIL import Image
import numpy as np
from typing import Tuple, Optional

class ChessVisualizer:
    """Classe para visualizar partidas de xadrez usando Pygame."""
    
    def __init__(self, width=600, height=600):
        """
        Inicializa o visualizador de xadrez.
        
        Args:
            width: Largura da janela.
            height: Altura da janela.
        """
        pygame.init()
        pygame.display.set_caption("Chess Tournament Visualizer")
        
        self.width = width
        self.height = height
        self.board_size = min(width, height) - 80
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 14)
        self.large_font = pygame.font.SysFont('Arial', 20, bold=True)
        
        # Cooldown entre movimentos (em milissegundos)
        self.cooldown = 1000  # 1 segundo inicial
        self.min_cooldown = 100    # 0.1 segundo
        self.max_cooldown = 5000   # 5 segundos
        
        # Estado atual
        self.is_running = False
        self.last_move = "Nenhum"
        self.move_count = 0
        self.white_bot_name = ""
        self.black_bot_name = ""
        
        # Superfície para renderizar o tabuleiro
        self.board_surface = pygame.Surface((self.board_size, self.board_size))
    
    def svg_to_pygame_surface(self, svg_string: str) -> pygame.Surface:
        """
        Converte uma string SVG em uma superfície Pygame.
        
        Args:
            svg_string: String SVG do tabuleiro.
            
        Returns:
            Superfície Pygame com o tabuleiro renderizado.
        """
        # Converte SVG para PNG usando cairosvg
        png_data = cairosvg.svg2png(bytestring=svg_string.encode('utf-8'))
        
        # Converte PNG para imagem PIL
        pil_img = Image.open(io.BytesIO(png_data))
        pil_img = pil_img.resize((self.board_size, self.board_size))
        
        # Converte PIL para um array numpy
        img_array = np.array(pil_img)
        
        # Certifica-se de que a imagem está em formato RGBA
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')
            img_array = np.array(pil_img)
        
        # Verifica se as dimensões correspondem aos bytes
        expected_buffer_size = pil_img.width * pil_img.height * 4  # 4 bytes para RGBA
        actual_buffer_size = img_array.nbytes
        
        if expected_buffer_size != actual_buffer_size:
            # Cria uma nova superfície Pygame e usa blit para transferir a imagem
            # Essa é uma abordagem alternativa quando frombuffer não funciona corretamente
            surface = pygame.Surface((pil_img.width, pil_img.height), pygame.SRCALPHA)
            
            # Converte a imagem PIL para uma string de bytes no formato correto
            img_str = pil_img.tobytes()
            
            # Cria uma superfície temporária a partir da string de bytes
            temp_surface = pygame.image.fromstring(
                img_str, pil_img.size, pil_img.mode
            )
            
            # Copia a superfície temporária para a superfície final
            surface.blit(temp_surface, (0, 0))
            
            return surface
        
        # Se as dimensões corresponderem, use o método tradicional
        return pygame.image.frombuffer(img_array.tobytes(), pil_img.size, "RGBA")
    
    def update_board(self, board: chess.Board) -> None:
        """
        Atualiza o tabuleiro na tela.
        
        Args:
            board: Objeto Board de chess representando o estado atual.
        """
        # Obtém a representação SVG do tabuleiro
        svg_string = chess.svg.board(board, size=self.board_size)
        
        # Converte para superfície Pygame
        self.board_surface = self.svg_to_pygame_surface(svg_string)
    
    def render_info_panel(self, board: chess.Board) -> None:
        """
        Renderiza o painel de informações.
        
        Args:
            board: Objeto Board de chess representando o estado atual.
        """
        # Fundo do painel de informações
        info_rect = pygame.Rect(0, self.board_size, self.width, self.height - self.board_size)
        pygame.draw.rect(self.screen, (240, 240, 240), info_rect)
        
        # Informações do jogo
        turn = "Brancas" if board.turn == chess.WHITE else "Pretas"
        current_bot = self.white_bot_name if board.turn == chess.WHITE else self.black_bot_name
        
        texts = [
            f"Movimento: {self.move_count}",
            f"Último movimento: {self.last_move}",
            f"Vez de: {turn} ({current_bot})",
            f"Cooldown: {self.cooldown/1000:.1f}s (Use +/- para ajustar)",
            f"{self.white_bot_name} (Brancas) vs {self.black_bot_name} (Pretas)"
        ]
        
        # Renderiza textos
        for i, text in enumerate(texts):
            text_surf = self.font.render(text, True, (0, 0, 0))
            text_rect = text_surf.get_rect(left=10, top=self.board_size + 10 + i * 15)
            self.screen.blit(text_surf, text_rect)
    
    def render_result(self, result: str) -> None:
        """
        Renderiza o resultado do jogo.
        
        Args:
            result: String com o resultado ("white", "black" ou "draw").
        """
        if result == "white":
            msg = f"{self.white_bot_name} (Brancas) venceu!"
            color = (0, 128, 0)  # Verde
        elif result == "black":
            msg = f"{self.black_bot_name} (Pretas) venceu!"
            color = (0, 128, 0)  # Verde
        else:
            msg = "Empate!"
            color = (0, 0, 128)  # Azul
        
        # Renderiza mensagem de resultado
        result_surf = self.large_font.render(msg, True, color)
        result_rect = result_surf.get_rect(center=(self.width // 2, self.board_size + 50))
        
        # Fundo transparente
        overlay = pygame.Surface((result_rect.width + 20, result_rect.height + 10), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 200))
        overlay_rect = overlay.get_rect(center=result_rect.center)
        
        self.screen.blit(overlay, overlay_rect)
        self.screen.blit(result_surf, result_rect)
        
        # Mensagem para continuar
        continue_surf = self.font.render("Pressione qualquer tecla para continuar", True, (0, 0, 0))
        continue_rect = continue_surf.get_rect(center=(self.width // 2, self.board_size + 75))
        self.screen.blit(continue_surf, continue_rect)
    
    def show_game(self, board: chess.Board, white_bot_name: str, black_bot_name: str, 
                  move_callback, end_callback=None) -> None:
        """
        Mostra o jogo de xadrez em tempo real.
        
        Args:
            board: Tabuleiro inicial.
            white_bot_name: Nome do bot com as peças brancas.
            black_bot_name: Nome do bot com as peças pretas.
            move_callback: Função que executa o próximo movimento e retorna (board, move_san).
            end_callback: Função chamada quando o jogo terminar.
        """
        self.white_bot_name = white_bot_name
        self.black_bot_name = black_bot_name
        self.move_count = 0
        self.last_move = "Nenhum"
        self.is_running = True
        
        # Timer para cooldown entre movimentos
        pygame.time.set_timer(pygame.USEREVENT, self.cooldown)
        
        game_over = False
        result = None
        
        # Loop principal
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    pygame.quit()
                    return
                
                # Processar movimento
                elif event.type == pygame.USEREVENT and not game_over:
                    try:
                        if not board.is_game_over():
                            current_bot = self.white_bot_name if board.turn == chess.WHITE else self.black_bot_name
                            board, move_san = move_callback(board)
                            self.move_count += 1
                            self.last_move = f"{current_bot}: {move_san}"
                        else:
                            game_over = True
                            if board.result() == "1-0":
                                result = "white"
                            elif board.result() == "0-1":
                                result = "black"
                            else:
                                result = "draw"
                    except Exception as e:
                        print(f"Erro ao executar movimento: {e}")
                        game_over = True
                
                # Ajuste de cooldown
                elif event.type == pygame.KEYDOWN:
                    if game_over:  # Qualquer tecla fecha o resultado
                        self.is_running = False
                        if end_callback:
                            end_callback(result)
                        return
                    
                    if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                        # Diminui o cooldown (movimento mais rápido)
                        self.cooldown = max(self.min_cooldown, self.cooldown - 100)
                        pygame.time.set_timer(pygame.USEREVENT, self.cooldown)
                    
                    elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                        # Aumenta o cooldown (movimento mais lento)
                        self.cooldown = min(self.max_cooldown, self.cooldown + 100)
                        pygame.time.set_timer(pygame.USEREVENT, self.cooldown)
                        
                    elif event.key == pygame.K_ESCAPE:
                        self.is_running = False
                        if end_callback:
                            end_callback(None)  # Cancelado pelo usuário
                        return
            
            # Renderização
            self.screen.fill((255, 255, 255))
            self.update_board(board)
            self.screen.blit(self.board_surface, (40, 40))
            self.render_info_panel(board)
            
            if game_over:
                self.render_result(result)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        # Cleanup
        pygame.quit()