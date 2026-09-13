from collections.abc import Iterator
from typing import final, override
import pygame
import esper

from client.component import (
    CampfireTag,
    DamageDealer,
    EnemyTag,
    Health,
    Hitbox,
    Invincibility,
    Position,
    ProjectileTag,
    aabb_overlap,
    hitbox_bounds,
)
from client.core.spatial import SpatialGrid, get_active_grid
from client.utils.ecs import get_components
from client.view.player import PlayerView

# Processeur central des dégâts : gère les collisions "qui font mal"
# (ennemis vs joueur, ennemis vs feu de camp, projectiles vs ennemis).

INVINCIBILITY_AFTER_HIT = 1.0  # Durée d'invincibilité (secondes) après avoir été touché


def _aabb_candidates(
    grid: SpatialGrid,
    bounds: tuple[float, float, float, float],
    exclude_ent: int,
) -> Iterator[int]:
    """Renvoie les entités "candidates" à une collision avec `bounds`, en utilisant
    la grille spatiale pour ne pas avoir à tester toutes les entités du jeu.
    `exclude_ent` permet d'exclure l'entité elle-même de sa propre recherche,
    et les doublons (une entité peut apparaître dans plusieurs cellules) sont filtrés."""
    seen: set[int] = set()
    for ent in grid.query_aabb(*bounds):
        if ent == exclude_ent or ent in seen:
            continue
        seen.add(ent)
        yield ent


@final
class DamageProc(esper.Processor):
    def __init__(self):
        self._hurt_sound = pygame.mixer.Sound("assets/sound/hurt.mp3")

    @override
    def process(self, dt: float):
        # Traite les trois sources de dégâts possibles à chaque frame
        self._enemies_damage_player(dt)
        self._enemies_damage_campfire(dt)
        self._projectiles_damage_enemies()

    def _enemies_damage_player(self, dt: float) -> None:
        """Inflige des dégâts au joueur s'il touche un ennemi (avec période
        d'invincibilité après chaque coup pour éviter le "grignotage" continu)."""
        player = PlayerView.get()

        player.invincibility.time -= dt
        if player.invincibility.time > 0:
            # Le joueur est encore invincible suite à un coup précédent
            return

        p_bounds = hitbox_bounds(player.pos, player.hitbox)
        for ent in _aabb_candidates(get_active_grid(), p_bounds, player.ent):
            try:
                # On ne garde que les entités qui sont bien des ennemis capables
                # d'infliger des dégâts (les autres lèvent KeyError et sont ignorées)
                edmg = esper.component_for_entity(ent, DamageDealer)
                ehit = esper.component_for_entity(ent, Hitbox)
                esper.component_for_entity(ent, EnemyTag)
                epos = esper.component_for_entity(ent, Position)
            except KeyError:
                continue

            if aabb_overlap(p_bounds, hitbox_bounds(epos, ehit)):
                player.hp.current -= edmg.amount
                player.invincibility.time = INVINCIBILITY_AFTER_HIT
                self._hurt_sound.play()
                # On s'arrête au premier ennemi touché sur cette frame
                return

    def _projectiles_damage_enemies(self) -> None:
        """Inflige des dégâts aux ennemis touchés par un projectile, et détruit
        le projectile après impact."""
        grid = get_active_grid()
        to_delete: set[int] = set()
        for b_ent, (_, bpos, bdmg, bhit) in esper.get_components(
            ProjectileTag, Position, DamageDealer, Hitbox
        ):
            b_bounds = hitbox_bounds(bpos, bhit)
            for ent in _aabb_candidates(grid, b_bounds, b_ent):
                try:
                    ehp = esper.component_for_entity(ent, Health)
                    ehit = esper.component_for_entity(ent, Hitbox)
                    esper.component_for_entity(ent, EnemyTag)
                    epos = esper.component_for_entity(ent, Position)
                except KeyError:
                    continue

                if aabb_overlap(b_bounds, hitbox_bounds(epos, ehit)):
                    ehp.current -= bdmg.amount
                    to_delete.add(b_ent)
                    # Le projectile ne peut toucher qu'un seul ennemi (il est détruit ensuite)
                    break

        # Suppression des projectiles ayant touché une cible, une fois la boucle terminée
        for b_ent in to_delete:
            esper.delete_entity(b_ent)

    def _enemies_damage_campfire(self, dt: float) -> None:
        """Inflige des dégâts au(x) feu(x) de camp touché(s) par un ennemi,
        avec une petite période d'invincibilité entre deux coups."""
        campfires = get_components(CampfireTag, Position, Health, Hitbox, Invincibility)
        if not campfires:
            return
        for _, (_, cpos, chp, chit, cinv) in campfires:
            cinv.time -= dt
            if cinv.time > 0:
                continue

            c_bounds = hitbox_bounds(cpos, chit)
            for _, (_, epos, edmg, ehit) in esper.get_components(
                EnemyTag, Position, DamageDealer, Hitbox
            ):
                if aabb_overlap(c_bounds, hitbox_bounds(epos, ehit)):
                    chp.current -= edmg.amount
                    cinv.time = 1.0
                    break
