from collections.abc import Iterable, Sequence
from typing import final, override

import esper
from esper import Processor

from client.component import (
    CampfireTag,
    EnemyTag,
    Hitbox,
    Position,
    hitbox_bounds,
)
from client.view.player import PlayerView

# Processeur qui empêche le joueur et les ennemis de traverser les feux de camp
# (collisions "solides" avec repositionnement).


def _resolve_against_campfires(
    movables: Iterable[tuple[Position, Hitbox]],
    campfires: Sequence[tuple[int, tuple[object, Position, Hitbox]]],
) -> None:
    """Repousse chaque entité mobile hors de chaque feu de camp qu'elle chevauche,
    en la déplaçant du plus petit déplacement possible (sur l'axe le moins pénétré)."""
    for m_pos, m_hit in movables:
        for _, (_, c_pos, c_hit) in campfires:
            ml, mt, mr, mb = hitbox_bounds(m_pos, m_hit)
            cl, ct, cr, cb = hitbox_bounds(c_pos, c_hit)

            # Calcule le chevauchement (overlap) sur chaque axe
            ox = min(mr, cr) - max(ml, cl)
            oy = min(mb, cb) - max(mt, ct)
            if ox <= 0 or oy <= 0:
                # Pas de chevauchement réel : rien à faire
                continue

            # On repousse l'entité selon l'axe où le chevauchement est le plus petit
            # (c'est la sortie de collision la plus "naturelle")
            if ox < oy:
                m_pos.x += ox if m_pos.x > c_pos.x + c_hit.offset_x else -ox
            else:
                m_pos.y += oy if m_pos.y > c_pos.y + c_hit.offset_y else -oy


@final
class CollisionProc(Processor):
    def __init__(self) -> None:
        super().__init__()
        self._campfire_timers: dict[int, float] = {}

    @override
    def process(self, dt: float) -> None:
        campfires = esper.get_components(CampfireTag, Position, Hitbox)
        if not campfires:
            # Aucun feu de camp sur la carte : rien à vérifier
            return

        # Empêche le joueur de traverser les feux de camp
        player = PlayerView.get()
        _resolve_against_campfires([(player.pos, player.hitbox)], campfires)

        # Empêche également les ennemis de traverser les feux de camp
        enemies = (
            (e_pos, e_hit)
            for _, (_, e_pos, e_hit) in esper.get_components(EnemyTag, Position, Hitbox)
        )
        _resolve_against_campfires(enemies, campfires)
