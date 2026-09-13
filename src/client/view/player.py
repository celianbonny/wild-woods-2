from dataclasses import dataclass
from typing import Self

import esper

from client.component import (
    Health,
    Hitbox,
    Inventory,
    Invincibility,
    PlayerTag,
    Position,
    Speed,
    Velocity,
    Weapon,
)
from client.utils.ecs import get_components

# "Vue" pratique regroupant tous les composants du joueur dans un seul objet,
# afin d'éviter de refaire des requêtes ECS partout dans le code où l'on a
# besoin de plusieurs informations sur le joueur en même temps.


@dataclass
class PlayerView:
    ent: int                    # Identifiant de l'entité joueur
    pos: Position
    vel: Velocity
    speed: Speed
    hp: Health
    inv: Inventory
    hitbox: Hitbox
    invincibility: Invincibility

    @classmethod
    def get(cls) -> Self:
        """Return the player view.

        The player entity exists for the entire lifetime of the game world, so
        this never returns ``None``. If it is somehow missing, that is a bug and
        we fail fast rather than silently skipping logic.
        """
        # Recherche l'entité possédant tous les composants ci-dessous
        # (il ne doit y en avoir qu'une seule : le joueur)
        query = get_components(
            PlayerTag,
            Position,
            Velocity,
            Speed,
            Health,
            Inventory,
            Hitbox,
            Invincibility,
        )
        if not query:
            raise RuntimeError("PlayerView.get() called but no player entity exists")
        ent, data = query[0]
        # data[0] est le PlayerTag (non utilisé ici), on ne garde que le reste (data[1:])
        return cls(ent, *data[1:])

    def weapon(self) -> Weapon | None:
        """Renvoie l'arme du joueur si elle possède ce composant, sinon None
        (le joueur peut ne pas encore avoir d'arme équipée)."""
        try:
            return esper.component_for_entity(self.ent, Weapon)
        except KeyError:
            return None
