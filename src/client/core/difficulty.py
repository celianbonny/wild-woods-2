from dataclasses import dataclass


@dataclass(frozen=True)
class Difficulty:
    """Représente un niveau de difficulté avec tous ses paramètres de jeu."""

    name: str                    # Nom affiché du niveau de difficulté
    sheet_path: str               # Chemin vers l'image de fond associée
    frame_size: int               # Taille d'une frame du sprite associé
    player_health: int            # joueur : PV de départ
    enemy_level_offset: int       # bonus de niveau initial des ennemis (vitesse + PV)
    spawn_interval_base: float    # intervalle de base entre les spawns (secondes)
    spawn_interval_min: float     # intervalle minimal (vitesse maximale d'apparition)


# Liste des difficultés disponibles.
# Difficulty(nom, img, img size, pv, lvl bonus enemy, spawn rate de base, spawn rate max)
DIFFICULTIES: list[Difficulty] = [
    Difficulty("Facile", "assets/map/planet.png", 80, 10, 0, 6.0, 1.0),
    Difficulty("Normal", "assets/map/planet.png", 80, 8, 10, 4.0, 0.8),
    Difficulty("Difficile", "assets/map/planet.png", 80, 6, 20, 3.0, 0.6),
    Difficulty("Impossible", "assets/map/blackhole.png", 200, 4, 20, 2.0, 0.5),
]
DEFAULT_DIFFICULTY = 1  # Index de la difficulté choisie par défaut (Normal)
