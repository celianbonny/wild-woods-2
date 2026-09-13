import math
from typing import final, override

import esper

from client.component import EnemyTag, Position, Targeting
from client.view.player import PlayerView

# Processeur qui met à jour le ciblage des ennemis (savent-ils où est le joueur ?)


@final
class TargetingProc(esper.Processor):
    @override
    def process(self, dt: float):
        """
        For each enemy, find the player and check if it's within range.
        If it is, set the target and distance. Otherwise, clear target info.
        """
        player = PlayerView.get()

        # Pour chaque ennemi ayant un composant de ciblage
        for _, (_, pos, targeting) in esper.get_components(
            EnemyTag, Position, Targeting
        ):
            # Calcule la distance euclidienne entre l'ennemi et le joueur
            dist = math.hypot(player.pos.x - pos.x, player.pos.y - pos.y)
            if dist < targeting.range:
                # Le joueur est à portée : on le désigne comme cible
                targeting.target = player.ent
                targeting.distance = dist
            else:
                # Le joueur est hors de portée : on efface la cible
                targeting.target = None
                targeting.distance = float("inf")
