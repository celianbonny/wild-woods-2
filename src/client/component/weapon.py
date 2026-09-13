from dataclasses import dataclass


@dataclass
class Weapon:
    """Composant ECS représentant une arme (portée par une entité, ex: joueur ou tourelle)."""

    cooldown_max: float    # Temps (en secondes) à attendre entre deux tirs
    bullet_speed: float    # Vitesse de déplacement des projectiles tirés
    damage: int            # Dégâts infligés par projectile

    cooldown_current: float = 0.0  # Temps restant avant de pouvoir tirer à nouveau
