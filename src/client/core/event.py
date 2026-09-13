from enum import StrEnum, unique
from uuid import uuid4


@unique
class EngineEvent(StrEnum):
    """Enum pour les différents types d'événements internes au moteur de jeu."""

    # Événement personnalisé pygame signalant l'arrêt du moteur (fermeture du jeu).
    # On utilise un uuid4 comme valeur pour être certain qu'il ne rentre jamais
    # en collision avec un identifiant d'événement pygame déjà existant.
    STOP = uuid4().hex
