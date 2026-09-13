# Ré-expose les fonctions de fabrication d'entités (factories) pour un import simplifié
# depuis "client.factory" au lieu d'aller chercher dans chaque sous-module.
from .bandit import create_bandit
from .campfire import create_campfire
from .item import create_item
from .player import create_player

__all__ = [
    "create_bandit",
    "create_campfire",
    "create_item",
    "create_player",
]
