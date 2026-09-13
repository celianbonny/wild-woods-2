from dataclasses import dataclass

# Composants "tags" : ils ne portent aucune donnée, ils servent uniquement
# à marquer/catégoriser une entité (ex: pour la retrouver facilement via
# esper.get_component(PlayerTag)).


@dataclass(frozen=True, slots=True)
class PlayerTag:
    """Marque une entité comme étant le joueur."""
    ...


@dataclass(frozen=True, slots=True)
class EnemyTag:
    """Marque une entité comme étant un ennemi."""
    ...


@dataclass(frozen=True, slots=True)
class ProjectileTag:
    """Marque une entité comme étant un projectile."""
    ...


@dataclass(frozen=True, slots=True)
class CampfireTag:
    """Marque une entité comme étant un feu de camp."""
    ...
