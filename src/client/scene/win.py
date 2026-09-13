from collections.abc import Callable
from typing import final, override

import pygame

from client.core import Engine
from client.ui import NEON_PURPLE, Button

from .scene import Scene

# Scène affichée quand les joueurs remportent la partie (antidote synthétisé) :
# écran de victoire avec boutons pour revenir au menu ou quitter.


@final
class WinScene(Scene):
    _screen: pygame.Surface

    def __init__(self, engine: Engine, on_menu: Callable[[], None]):
        super().__init__()
        self._screen = engine.screen
        self._engine = engine
        self._on_menu = on_menu  # Callback pour revenir au menu principal

        self._font_title = pygame.font.Font(
            "assets/fonts/Instrument_Serif/InstrumentSerif-Italic.ttf", 150
        )
        self._font_subtitle = pygame.font.SysFont("Arial", 24, italic=True)

        w, h = self._screen.get_size()
        self._btn_menu = Button(
            "Menu", NEON_PURPLE, 28, 12, 10, 18, on_click=self._go_menu
        )
        self._btn_quit = Button(
            "Quitter", NEON_PURPLE, 28, 12, 10, 18, on_click=self._quit
        )
        self._btn_menu.set_rect(w // 2, h // 2 + 20)
        self._btn_quit.set_rect(w // 2, h // 2 + 100)

    def _go_menu(self) -> None:
        self._on_menu()

    def _quit(self) -> None:
        self._engine.stop()

    @override
    def on_enter(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        # Fond vert très sombre pour l'ambiance "victoire"
        self._screen.fill((0, 20, 5))
        w, h = self._screen.get_size()

        # Titre "Victoire !" avec ombre portée dorée
        shadow = self._font_title.render("Victoire !", True, (100, 70, 0))
        self._screen.blit(shadow, shadow.get_rect(center=(w // 2 + 5, h // 2 - 145)))

        title = self._font_title.render("Victoire !", True, (255, 215, 0))
        self._screen.blit(title, title.get_rect(center=(w // 2, h // 2 - 150)))

        subtitle = self._font_subtitle.render(
            "Vous avez survécu à l'apocalypse.", True, (150, 200, 150)
        )
        self._screen.blit(subtitle, subtitle.get_rect(center=(w // 2, h // 2 - 40)))

        for btn in (self._btn_menu, self._btn_quit):
            btn.update(dt, events)
            btn.draw(self._screen)

        # Bloque la propagation vers les scènes en dessous
        return False
