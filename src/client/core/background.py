import pygame

# Module gérant le chargement (une seule fois, en cache) de l'image de fond du jeu.

_bg_image = None   # Cache de la surface pygame de l'image de fond
_bg_w: int = 0     # Largeur de l'image en cache
_bg_h: int = 0     # Hauteur de l'image en cache

TILE_SIZE = 10     # Taille d'une tuile de fond, utilisée pour le défilement/répétition


def get_bg_data() -> tuple[pygame.Surface, int, int]:
    """Renvoie l'image de fond ainsi que sa largeur et sa hauteur.

    L'image n'est chargée depuis le disque qu'une seule fois (mise en cache
    dans des variables globales) afin d'éviter de la recharger à chaque appel.
    """
    global _bg_image, _bg_w, _bg_h
    if _bg_image is None:
        _bg_image = pygame.image.load("assets/map/background.png").convert()
        _bg_w = _bg_image.get_width()
        _bg_h = _bg_image.get_height()

    return _bg_image, _bg_w, _bg_h
