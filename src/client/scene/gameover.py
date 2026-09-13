from collections.abc import Callable
from typing import final, override

import pygame

from client.core import Engine
from client.ui import NEON_PURPLE, Button

from .scene import Scene

# Scène affichée quand le joueur meurt : écran "GAME OVER" avec boutons
# pour rejouer ou quitter le jeu.


@final
class GameOverScene(Scene):
    _screen: pygame.Surface

    def __init__(self, engine: Engine, on_replay: Callable[[], None]):
        super().__init__()
        self._screen = engine.screen
        self._engine = engine
        self._on_replay = on_replay  # Callback pour relancer une partie

        self._font_subtitle = pygame.font.SysFont("Arial", 24, italic=True)
        self._font_title = pygame.font.Font("assets/fonts/Eater/Eater-Regular.ttf", 150)

        w, h = self._screen.get_size()
        self._btn_quit = Button(
            "Quitter", NEON_PURPLE, 28, 12, 10, 18, on_click=self._quit
        )
        self._btn_replay = Button(
            "Rejouer", NEON_PURPLE, 28, 12, 10, 18, on_click=self._replay
        )

        # Positionne les boutons, centrés horizontalement, l'un sous l'autre
        self._btn_quit.set_rect(w // 2, h // 2 + 100)
        self._btn_replay.set_rect(w // 2, h // 2 + 20)

    def _quit(self) -> None:
        self._engine.stop()

    def _replay(self) -> None:
        self._on_replay()

    @override
    def on_enter(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        # Fond rouge très sombre pour l'ambiance "game over"
        self._screen.fill((15, 0, 0))
        w, h = self._screen.get_size()

        # Titre avec un effet d'ombre portée (texte foncé légèrement décalé,
        # puis texte clair par-dessus) pour plus de lisibilité/style
        shadow_texte = self._font_title.render("GAME OVER", True, (80, 0, 0))
        rect_shadow = shadow_texte.get_rect(center=(w // 2 + 4, h // 2 - 146))
        self._screen.blit(shadow_texte, rect_shadow)

        image_texte = self._font_title.render("GAME OVER", True, (255, 40, 40))
        rect_texte = image_texte.get_rect(center=(w // 2, h // 2 - 150))
        self._screen.blit(image_texte, rect_texte)

        subtitle = self._font_subtitle.render(
            "L'apocalypse a eu raison de vous...", True, (150, 150, 150)
        )
        rect_sub = subtitle.get_rect(center=(w // 2, h // 2 - 40))
        self._screen.blit(subtitle, rect_sub)

        # Met à jour et affiche les boutons (gère leurs clics/survols)
        for btn in (self._btn_replay, self._btn_quit):
            btn.update(dt, events)
            btn.draw(self._screen)

        # Renvoie False : bloque la mise à jour des scènes en dessous
        # (la partie terminée ne doit plus être jouée/affichée derrière ce menu)
        return False
