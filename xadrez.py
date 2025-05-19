#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Torneio automatizado de Xadrez entre bots
"""

import chess
import chess.svg
import chess.pgn
import random
import time
import itertools
import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Type, Optional
import webbrowser
from tempfile import NamedTemporaryFile
import datetime
import matplotlib.pyplot as plt
import numpy as np
# Import visualizer
from visualizer import ChessVisualizer
# Import bots
from bot import ChessBot, BotRegistry
# Import all bots
from bots import *

# Sistema de torneio
class ChessTournament:
    """Sistema para gerenciar torneios de xadrez entre bots."""
    
    def __init__(self, bots: List[ChessBot], rounds: int = 1, move_timeout: float = 0.5, move_limit: int = 500):
        """
        Inicializa o torneio de xadrez.
        
        Args:
            bots: Lista de bots participantes.
            rounds: Número de rodadas do torneio.
            move_timeout: Tempo máximo (em segundos) para cada movimento.
            move_limit: Número máximo de movimentos por partida (150 por padrão).
        """
        self.bots = bots
        self.rounds = rounds
        self.move_timeout = move_timeout
        self.move_limit = move_limit
        self.results = {bot.name: {"wins": 0, "losses": 0, "draws": 0, "points": 0} for bot in bots}
        
        # Cria pasta para armazenar os PGNs do torneio
        self.tournament_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.pgn_dir = f"torneio_pgns_{self.tournament_date}"
        self._create_pgn_directory()
    
    def _create_pgn_directory(self):
        """Cria o diretório para armazenar os PGNs das partidas."""
        if not os.path.exists(self.pgn_dir):
            os.makedirs(self.pgn_dir)
            print(f"Diretório para PGNs criado: {self.pgn_dir}")
    
    def _save_pgn(self, white_bot: ChessBot, black_bot: ChessBot, moves: List[chess.Move], winner: str, reason: str, round_num: int):
        """
        Salva a partida em formato PGN.
        
        Args:
            white_bot: Bot das peças brancas
            black_bot: Bot das peças pretas
            moves: Lista de movimentos da partida
            winner: Quem venceu ('white', 'black' ou 'draw')
            reason: Motivo do término da partida
            round_num: Número da rodada
        """
        # Criar um objeto de jogo PGN
        game = chess.pgn.Game()
        
        # Configurar os cabeçalhos do PGN
        date_str = datetime.datetime.now().strftime("%Y.%m.%d")
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Resultado em formato padrão PGN
        if winner == "white":
            result = "1-0"
        elif winner == "black":
            result = "0-1"
        else:
            result = "1/2-1/2"
            
        # Definir cabeçalhos com metadados
        game.headers["Event"] = f"Torneio de Bots de Xadrez {self.tournament_date}"
        game.headers["Site"] = "Torneio Local"
        game.headers["Date"] = date_str
        game.headers["Round"] = str(round_num)
        game.headers["White"] = white_bot.name
        game.headers["Black"] = black_bot.name
        game.headers["Result"] = result
        game.headers["WhiteType"] = "computer"
        game.headers["BlackType"] = "computer"
        game.headers["Termination"] = reason
        game.headers["TimeControl"] = f"{self.move_timeout}s"
        
        # Adicionar os movimentos ao PGN
        node = game
        for move in moves:
            node = node.add_variation(move)
            
        # Criar nome de arquivo descritivo
        result_short = "vitoria_brancas" if winner == "white" else "vitoria_pretas" if winner == "black" else "empate"
        clean_reason = reason.replace(" ", "_")
        filename = f"R{round_num}_{white_bot.name}_vs_{black_bot.name}_{result_short}_{clean_reason}.pgn"
        # Remover caracteres especiais do nome do arquivo
        filename = "".join(c if c.isalnum() or c in "_-." else "_" for c in filename)
        
        # Caminho completo para o arquivo
        pgn_path = os.path.join(self.pgn_dir, filename)
        
        # Salvar o PGN
        with open(pgn_path, "w", encoding="utf-8") as pgn_file:
            exporter = chess.pgn.FileExporter(pgn_file)
            game.accept(exporter)
            
        print(f"PGN da partida salvo em: {pgn_path}")
    
    def run_match(self, white_bot: ChessBot, black_bot: ChessBot, 
                  display: bool = False, delay: float = 0.5, round_num: int = 1) -> Tuple[str, str]:
        """
        Executa uma partida entre dois bots.
        
        Args:
            white_bot: Bot com as peças brancas.
            black_bot: Bot com as peças pretas.
            display: Se True, mostra o tabuleiro usando pygame.
            delay: Tempo de espera entre movimentos quando display=True.
            round_num: Número da rodada atual.
            
        Returns:
            Tupla com o resultado (white, black, draw) e a razão do término.
        """
        board = chess.Board()
        game_moves = []  # Lista para armazenar os movimentos da partida
        
        if display:
            # Inicializa o visualizador pygame
            visualizer = ChessVisualizer()
            
            # Função de callback para processar o próximo movimento
            def move_callback(current_board):
                current_bot = white_bot if current_board.turn == chess.WHITE else black_bot
                try:
                    start_time = time.time()
                    move = current_bot.choose_move(current_board)
                    elapsed = time.time() - start_time
                    
                    # Verifica timeout
                    if elapsed > self.move_timeout:
                        raise TimeoutError(f"{current_bot.name} excedeu o tempo limite!")
                    
                    # Executa o movimento
                    san_move = current_board.san(move)
                    current_board.push(move)
                    # Armazena o movimento para o PGN
                    game_moves.append(move)
                    return current_board, san_move
                except Exception as e:
                    print(f"Erro no bot {current_bot.name}: {e}")
                    raise
            
            # Função de callback para processar o final do jogo
            def end_callback(result):
                nonlocal winner, reason
                if result == "white":
                    winner, reason = "white", "finished"
                elif result == "black":
                    winner, reason = "black", "finished"
                elif result == "draw":
                    winner, reason = "draw", "finished"
                else:
                    winner, reason = "draw", "canceled"
            
            # Inicializa o resultado
            winner, reason = None, None
            
            # Executa a visualização
            visualizer.show_game(board, white_bot.name, black_bot.name, move_callback, end_callback)
            
            # Verificar se atingiu limite de movimentos
            if board.fullmove_number >= self.move_limit // 2:  # Dividido por 2 porque chess.Board conta movimentos completos (branco+preto)
                winner, reason = "draw", "move limit"
            # Se não tiver um resultado válido (jogo foi fechado), determina o resultado atual do tabuleiro
            elif winner is None:
                # Determinar o resultado
                result = board.result()
                reason = "checkmate" if board.is_checkmate() else "stalemate" if board.is_stalemate() else "draw"
                
                if result == "1-0":
                    winner = "white"
                elif result == "0-1":
                    winner = "black"
                else:
                    winner = "draw"
                
        else:
            # Execução sem visualização
            move_count = 0
            while not board.is_game_over() and move_count < self.move_limit:
                current_bot = white_bot if board.turn == chess.WHITE else black_bot
                
                try:
                    start_time = time.time()
                    move = current_bot.choose_move(board)
                    elapsed = time.time() - start_time
                    
                    # Verifica timeout
                    if elapsed > self.move_timeout:
                        print(f"Timeout: {current_bot.name} excedeu o tempo limite!")
                        return ("black", "timeout") if board.turn == chess.WHITE else ("white", "timeout")
                    
                    # Executa o movimento
                    board.push(move)
                    # Armazena o movimento para o PGN
                    game_moves.append(move)
                    move_count += 1
                    
                except Exception as e:
                    print(f"Erro no bot {current_bot.name}: {e}")
                    return ("black", "error") if board.turn == chess.WHITE else ("white", "error")
            
            # Determinar o resultado
            if move_count >= self.move_limit:
                winner, reason = "draw", "move limit"
            else:
                result = board.result()
                reason = "checkmate" if board.is_checkmate() else "stalemate" if board.is_stalemate() else "draw"
                
                if result == "1-0":
                    winner = "white"
                elif result == "0-1":
                    winner = "black"
                else:
                    winner = "draw"
        
        # Salvar o PGN da partida
        self._save_pgn(white_bot, black_bot, game_moves, winner, reason, round_num)
        
        return (winner, reason)
    
    def run_tournament(self, display_games: bool = False) -> Dict:
        """
        Executa o torneio round-robin entre todos os bots.
        
        Args:
            display_games: Se True, exibe o tabuleiro durante as partidas.
            
        Returns:
            Dicionário com os resultados do torneio.
        """
        matches = list(itertools.permutations(self.bots, 2))
        
        for round_num in range(self.rounds):
            print(f"Iniciando rodada {round_num + 1} de {self.rounds}")
            
            for white_bot, black_bot in matches:
                print(f"Partida: {white_bot.name} (Brancas) vs {black_bot.name} (Pretas)")
                
                winner, reason = self.run_match(white_bot, black_bot, display=display_games, round_num=round_num + 1)
                
                if winner == "white":
                    self.results[white_bot.name]["wins"] += 1
                    self.results[white_bot.name]["points"] += 1
                    self.results[black_bot.name]["losses"] += 1
                elif winner == "black":
                    self.results[black_bot.name]["wins"] += 1
                    self.results[black_bot.name]["points"] += 1
                    self.results[white_bot.name]["losses"] += 1
                else:  # Empate
                    self.results[white_bot.name]["draws"] += 1
                    self.results[black_bot.name]["draws"] += 1
                    self.results[white_bot.name]["points"] += 0.5
                    self.results[black_bot.name]["points"] += 0.5
                
                print(f"Resultado: {winner} ({reason})")
        
        return self.results
    
    def print_results(self):
        """Imprime os resultados do torneio de forma organizada."""
        
        # Ordena os resultados por pontos
        sorted_results = sorted(self.results.items(), key=lambda x: x[1]["points"], reverse=True)
        
        print("\n=== RESULTADOS DO TORNEIO ===")
        print(f"{'Bot':<20} {'Vitórias':<10} {'Derrotas':<10} {'Empates':<10} {'Pontos':<10}")
        print("-" * 60)
        
        for bot_name, stats in sorted_results:
            print(f"{bot_name:<20} {stats['wins']:<10} {stats['losses']:<10} {stats['draws']:<10} {stats['points']:<10}")
    
    def plot_results(self):
        """Plota os resultados do torneio em um gráfico de barras."""
        bot_names = list(self.results.keys())
        points = [stats["points"] for stats in self.results.values()]
        wins = [stats["wins"] for stats in self.results.values()]
        draws = [stats["draws"] for stats in self.results.values()]
        
        sorted_indices = np.argsort(points)[::-1]
        bot_names = [bot_names[i] for i in sorted_indices]
        points = [points[i] for i in sorted_indices]
        wins = [wins[i] for i in sorted_indices]
        draws = [draws[i] for i in sorted_indices]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(bot_names))
        width = 0.25
        
        ax.bar(x - width, points, width, label='Pontos')
        ax.bar(x, wins, width, label='Vitórias')
        ax.bar(x + width, draws, width, label='Empates')
        
        ax.set_title('Resultados do Torneio de Xadrez')
        ax.set_xticks(x)
        ax.set_xticklabels(bot_names, rotation=45, ha='right')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig('resultados_torneio.png')
        plt.show()


# Interface de linha de comando
def main():
    """Função principal para executar o torneio via linha de comando."""
    
    # Obter todos os bots disponíveis
    available_bots = BotRegistry.get_all_bots()
    
    print("=== Torneio de Xadrez entre Bots ===\n")
    print(f"Bots disponíveis ({len(available_bots)}):")
    
    for i, (bot_name, _) in enumerate(available_bots.items(), 1):
        bot_instance = BotRegistry.create_bot(bot_name)
        print(f"{i}. {bot_instance.name} ({bot_name})")
    
    print("\nOpções:")
    print("1. Executar torneio round-robin completo")
    print("2. Assistir a uma partida específica")
    print("3. Sair")
    
    choice = input("\nEscolha uma opção: ")
    
    if choice == '1':
        # Torneio completo
        rounds = int(input("Número de rodadas: ") or "1")
        display = input("Visualizar os jogos? (s/N): ").lower() == 's'
        
        # Criar instâncias de todos os bots
        bots = [BotRegistry.create_bot(bot_name) for bot_name in available_bots.keys()]
        
        tournament = ChessTournament(bots, rounds=rounds)
        tournament.run_tournament(display_games=display)
        tournament.print_results()
        tournament.plot_results()
        
    elif choice == '2':
        # Partida específica
        print("Selecione o bot para jogar com as brancas:")
        white_idx = int(input()) - 1
        
        print("Selecione o bot para jogar com as pretas:")
        black_idx = int(input()) - 1
        
        bot_names = list(available_bots.keys())
        white_bot = BotRegistry.create_bot(bot_names[white_idx])
        black_bot = BotRegistry.create_bot(bot_names[black_idx])
        
        print(f"Iniciando partida: {white_bot.name} (Brancas) vs {black_bot.name} (Pretas)")
        
        tournament = ChessTournament([white_bot, black_bot])
        result, reason = tournament.run_match(white_bot, black_bot, display=True, delay=1.0, round_num=1)
        
        print(f"Resultado: {result} ({reason})")
    
    elif choice == '3':
        print("Saindo...")
        return
    
    else:
        print("Opção inválida!")


if __name__ == "__main__":
    main()