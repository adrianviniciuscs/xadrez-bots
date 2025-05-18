#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de bots para o torneio de xadrez
"""

import chess
from abc import ABC, abstractmethod
from typing import Dict, Type

# Classe base para os bots de xadrez
class ChessBot(ABC):
    """Classe base para implementação de bots de xadrez."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do bot."""
        pass
    
    @abstractmethod
    def choose_move(self, board: chess.Board) -> chess.Move:
        """
        Escolhe um movimento para o bot.
        
        Args:
            board: Tabuleiro atual do jogo.
            
        Returns:
            O movimento escolhido.
        """
        pass

# Registro automático de bots
class BotRegistry:
    """Registro de bots de xadrez."""
    
    _bots: Dict[str, Type[ChessBot]] = {}
    
    @classmethod
    def register(cls, bot_class: Type[ChessBot]) -> Type[ChessBot]:
        """
        Registra um bot no sistema.
        
        Args:
            bot_class: Classe do bot a ser registrada.
            
        Returns:
            A classe do bot registrado.
        """
        cls._bots[bot_class.__name__] = bot_class
        return bot_class
    
    @classmethod
    def get_all_bots(cls) -> Dict[str, Type[ChessBot]]:
        """
        Retorna todos os bots registrados.
        
        Returns:
            Dicionário com todos os bots registrados.
        """
        return cls._bots.copy()
    
    @classmethod
    def create_bot(cls, bot_name: str) -> ChessBot:
        """
        Cria uma instância de um bot pelo nome.
        
        Args:
            bot_name: Nome da classe do bot.
            
        Returns:
            Instância do bot solicitado.
        """
        if bot_name not in cls._bots:
            raise ValueError(f"Bot não encontrado: {bot_name}")
        return cls._bots[bot_name]()