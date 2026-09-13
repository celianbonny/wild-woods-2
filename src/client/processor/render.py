from typing import final, override

import esper
import pygame
from esper import Processor

from client.component import (
    CampfireTag,
    Health,
    Hitbox,
    ItemKind,
    Position,
    Sprite,
    EnemyTag,
)
from client.core import TILE_SIZE, get_bg_data
from client.core.engine import Engine
from client.factory.item import ITEM_SPRITE_PATHS
from client.processor.render_helpers import (
    Camera,
    DebugOverlay,
    draw_tiled_background,
)
from client.processor.damage import INVINCIBILITY_AFTER_HIT
from client.view.player import PlayerView

# Processeur d'affichage principal : dessine le fond, les sprites, l'interface
# (barres de vie, inventaire) et les aides visuelles de debug.

_INVENTORY_ICON_SIZE = 18  # Taille (en pixels) des icônes d'objets affichées à l'écran


@final
class RenderProc(Processor):
    def __init__(self, screen: pygame.Surface, engine: Engine):
        super().__init__()
        self.screen = screen
        self._engine = engine
        self.font = pygame.font.SysFont("Arial", 18)
        # Précharge et redimensionne les icônes de chaque type d'objet une seule fois
        self._item_icons: dict[ItemKind, pygame.Surface] = {
            kind: pygame.transform.scale(
                pygame.image.load(path).convert_alpha(),
                (_INVENTORY_ICON_SIZE, _INVENTORY_ICON_SIZE),
            )
            for kind, path in ITEM_SPRITE_PATHS.items()
        }
        self._camera = Camera(smoothness=12.0)
        self._background, _, _ = get_bg_data()

        self._debug_overlay = DebugOverlay(
            font=self.font,
            engine=self._engine,
            tile_size=TILE_SIZE,
        )

    @override
    def process(self, dt: float):
        width, height = self.screen.get_size()
        player = PlayerView.get()
        player_pos = player.pos

        # Met à jour la caméra (suit le joueur) et récupère le décalage monde->écran
        offset_x, offset_y = self._camera.update(player_pos, dt, width, height)

        # --- Fond d'écran ---
        draw_tiled_background(self.screen, self._background, offset_x, offset_y)

        # --- Sprites de toutes les entités ---
        # Chaque sprite est centré sur la position de son entité
        for _, (pos, sprite) in esper.get_components(Position, Sprite):
            self.screen.blit(
                sprite.surface,
                (
                    pos.x + offset_x - sprite.surface.get_width() / 2,
                    pos.y + offset_y - sprite.surface.get_height() / 2,
                ),
            )

        # --- Aides visuelles de debug (hitboxes, zones de portée...) ---
        if self._engine.debug_enabled:
            # Hitbox des feux de camp (vert) + cercle de zone d'exclusion autour du feu
            for _, (_, pos, hitbox) in esper.get_components(
                CampfireTag, Position, Hitbox
            ):
                hx = int(pos.x + hitbox.offset_x + offset_x - hitbox.width / 2)
                hy = int(pos.y + hitbox.offset_y + offset_y - hitbox.height / 2)
                hitbox_surf = pygame.Surface(
                    (int(hitbox.width), int(hitbox.height)), pygame.SRCALPHA
                )
                hitbox_surf.fill((0, 255, 0, 120))
                self.screen.blit(hitbox_surf, (hx, hy))
                # exclusion zone autour du feu
                pygame.draw.circle(
                    self.screen,
                    (255, 80, 0),
                    (int(pos.x + offset_x), int(pos.y + offset_y)),
                    700,
                    2,
                )

            # Cercles de portée autour du joueur (ex: portée d'arme / de détection)
            px = int(player_pos.x + offset_x)
            py = int(player_pos.y + offset_y)
            pygame.draw.circle(self.screen, (0, 180, 255), (px, py), 300, 2)
            pygame.draw.circle(self.screen, (0, 80, 255), (px, py), 800, 2)

            # Hitbox du joueur (bleu)
            hx = int(
                player.pos.x
                + player.hitbox.offset_x
                + offset_x
                - player.hitbox.width / 2
            )
            hy = int(
                player.pos.y
                + player.hitbox.offset_y
                + offset_y
                - player.hitbox.height / 2
            )
            surf = pygame.Surface(
                (int(player.hitbox.width), int(player.hitbox.height)),
                pygame.SRCALPHA,
            )
            surf.fill((0, 100, 255, 120))
            self.screen.blit(surf, (hx, hy))

            # Hitbox de chaque ennemi (rouge)
            for _, (_, epos, ehit) in esper.get_components(EnemyTag, Position, Hitbox):
                hx = int(epos.x + ehit.offset_x + offset_x - ehit.width / 2)
                hy = int(epos.y + ehit.offset_y + offset_y - ehit.height / 2)
                surf = pygame.Surface(
                    (int(ehit.width), int(ehit.height)), pygame.SRCALPHA
                )
                surf.fill((255, 0, 0, 120))
                self.screen.blit(surf, (hx, hy))

        # --- Compteur de FPS (haut droit) ---
        fps = int(1.0 / dt) if dt > 0 else 0
        num_ent = sum(1 for _ in esper.get_entities())
        fps_text = self.font.render(
            f"FPS: {max(0, min(fps, 999))} ",
            True,
            pygame.Color("black"),
        )
        self.screen.blit(fps_text, (width - fps_text.get_width() - 10, 10))

        # --- Barre de vie du feu de camp (haut, centrée) ---
        campfires = esper.get_components(CampfireTag, Health)
        if campfires:
            _, (_, c_health) = campfires[0]
            bar_w = 300
            bar_h = 20
            bar_x = (width - bar_w) // 2
            bar_y = 10
            ratio = max(0.0, c_health.current / c_health.max)
            # Fond rouge foncé (PV manquants) puis rectangle vert (PV restants)
            pygame.draw.rect(self.screen, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(
                self.screen, (0, 200, 0), (bar_x, bar_y, int(bar_w * ratio), bar_h)
            )
            label = self.font.render(
                f"Feu de camp : {int(c_health.current)}/{int(c_health.max)}",
                True,
                pygame.Color("white"),
            )
            self.screen.blit(
                label,
                (
                    bar_x + (bar_w - label.get_width()) // 2,
                    bar_y + (bar_h - label.get_height()) // 2,
                ),
            )

        # barre de pv du joueur (même principe que celle du feu de camp, mais en haut à gauche)
        bar_w = 200
        bar_h = 20
        bar_x = 10
        bar_y = 10
        ratio = max(0.0, player.hp.current / player.hp.max)
        pygame.draw.rect(self.screen, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(
            self.screen, (0, 200, 0), (bar_x, bar_y, int(bar_w * ratio), bar_h)
        )
        label = self.font.render(
            f"PV : {int(player.hp.current)}/{int(player.hp.max)}",
            True,
            pygame.Color("white"),
        )
        self.screen.blit(
            label,
            (
                bar_x + (bar_w - label.get_width()) // 2,
                bar_y + (bar_h - label.get_height()) // 2,
            ),
        )
        # si le joueur subit un dégat : flash rouge
        # (l'opacité diminue progressivement pendant la durée d'invincibilité)
        if player.invincibility.time > 0:
            alpha = int((player.invincibility.time / INVINCIBILITY_AFTER_HIT) * 80)
            flash = pygame.Surface((width, height), pygame.SRCALPHA)
            flash.fill((255, 0, 0, alpha))
            self.screen.blit(flash, (0, 0))

        # --- Overlay de debug (texte détaillé, activable séparément) ---
        self._debug_overlay.draw(
            self.screen,
            dt,
            fps,
            num_ent,
            width,
            offset_x,
            offset_y,
            self._camera.x,
            self._camera.y,
        )

        # --- Affichage de l'or possédé (sous la barre de vie) ---
        gold = player.inv.count(ItemKind.GOLD)
        icon = self._item_icons.get(ItemKind.GOLD)
        y = 10 + self.font.get_linesize() + 6
        if icon is not None:
            # Affiche l'icône de pièce suivie du nombre d'or
            self.screen.blit(icon, (10, y))
            gold_text = self.font.render(f"{gold}", True, pygame.Color("black"))
            self.screen.blit(
                gold_text,
                (
                    10 + icon.get_width() + 4,
                    y + (icon.get_height() - gold_text.get_height()) // 2,
                ),
            )
        else:
            # Solution de repli si l'icône n'a pas pu être chargée : texte seul
            gold_text = self.font.render(f"Gold: {gold}", True, pygame.Color("black"))
            self.screen.blit(gold_text, (10, y))
