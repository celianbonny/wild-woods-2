from dataclasses import dataclass

# Composants ECS liés à la santé et aux dégâts.


@dataclass
class Health:
    """Points de vie d'une entité."""
    max: float       # PV maximum
    current: float   # PV actuels


@dataclass
class DamageDealer:
    """Portée par une entité capable d'infliger des dégâts (ex: projectile)."""
    amount: float    # Quantité de dégâts infligés au contact


@dataclass
class Invincibility:
    """Marque une entité comme temporairement invincible."""
    time: float      # Temps restant (en secondes) avant la fin de l'invincibilité
