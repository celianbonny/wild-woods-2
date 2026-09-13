from dataclasses import dataclass, field

# Grille spatiale (spatial hashing) : découpe le monde en cellules pour accélérer
# les recherches de collisions/proximité (au lieu de comparer toutes les entités
# entre elles, on ne compare que celles présentes dans les mêmes cellules).


@dataclass
class SpatialGrid:
    cell_size: float
    # Dictionnaire associant les coordonnées d'une cellule (cx, cy)
    # à la liste des identifiants d'entités qu'elle contient
    cells: dict[tuple[int, int], list[int]] = field(default_factory=dict)

    def clear(self) -> None:
        """Vide entièrement la grille (à faire à chaque frame avant de la reconstruire)."""
        self.cells.clear()

    def _cell_coords(self, x: float, y: float) -> tuple[int, int]:
        """Convertit une position du monde (x, y) en coordonnées de cellule (cx, cy)."""
        return (int(x // self.cell_size), int(y // self.cell_size))

    def insert(self, entity_id: int, x: float, y: float) -> None:
        """Insère une entité ponctuelle (un seul point) dans la cellule correspondante."""
        cell = self._cell_coords(x, y)
        self.cells.setdefault(cell, []).append(entity_id)

    def insert_aabb(
        self, entity_id: int, left: float, top: float, right: float, bottom: float
    ) -> None:
        """Insère une entité ayant une taille (boîte englobante AABB) dans TOUTES
        les cellules qu'elle recouvre (elle peut donc apparaître dans plusieurs cellules)."""
        min_cx = int(left // self.cell_size)
        max_cx = int(right // self.cell_size)
        min_cy = int(top // self.cell_size)
        max_cy = int(bottom // self.cell_size)
        for cy in range(min_cy, max_cy + 1):
            for cx in range(min_cx, max_cx + 1):
                self.cells.setdefault((cx, cy), []).append(entity_id)

    def query_aabb(
        self, left: float, top: float, right: float, bottom: float
    ) -> list[int]:
        """Renvoie la liste (avec doublons possibles) des entités présentes dans
        les cellules recouvertes par la zone (left, top, right, bottom)."""
        min_cx = int(left // self.cell_size)
        max_cx = int(right // self.cell_size)
        min_cy = int(top // self.cell_size)
        max_cy = int(bottom // self.cell_size)

        results: list[int] = []
        for cy in range(min_cy, max_cy + 1):
            for cx in range(min_cx, max_cx + 1):
                results.extend(self.cells.get((cx, cy), []))
        return results


# Grille spatiale unique, partagée par tout le jeu (pattern singleton simplifié)
_ACTIVE_GRID = SpatialGrid(cell_size=128.0)


def get_active_grid() -> SpatialGrid:
    """Renvoie la grille spatiale active partagée par le jeu."""
    return _ACTIVE_GRID
