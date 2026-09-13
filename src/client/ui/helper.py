import pygame


def lerp_color(a: pygame.Color, b: pygame.Color, t: float) -> pygame.Color:
    """Fait une interpolation linéaire (fondu progressif) entre deux couleurs.

    t=0 -> renvoie la couleur a
    t=1 -> renvoie la couleur b
    Valeurs intermédiaires -> mélange proportionnel entre les deux couleurs
    (utile pour des animations de survol de bouton, transitions, etc.)
    """
    # On force t à rester entre 0 et 1 pour éviter les couleurs invalides
    t = max(0.0, min(1.0, t))
    return pygame.Color(
        int(a.r + (b.r - a.r) * t),
        int(a.g + (b.g - a.g) * t),
        int(a.b + (b.b - a.b) * t),
    )
