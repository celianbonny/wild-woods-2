from typing import final, override

import esper

from client.component import Hitbox, Position, hitbox_bounds
from client.core.spatial import get_active_grid

# Processeur qui reconstruit à chaque frame une grille spatiale (partitionnement
# de l'espace en cellules) afin d'accélérer les recherches de collisions/proximité.


@final
class SpatialGridProc(esper.Processor):
    def __init__(self, cell_size: float = 128.0):
        super().__init__()
        # Récupère la grille spatiale active (partagée) et fixe la taille de ses cellules
        self._grid = get_active_grid()
        self._grid.cell_size = cell_size

    @override
    def process(self, dt: float) -> None:
        # On vide la grille avant de la reconstruire entièrement
        self._grid.clear()
        # Pour chaque entité ayant une position et une hitbox, on l'insère dans la grille
        # avec la boîte englobante (AABB) correspondant à sa position actuelle
        for ent, (pos, hit) in esper.get_components(Position, Hitbox):
            self._grid.insert_aabb(ent, *hitbox_bounds(pos, hit))
