from typing import cast, final, override

import pygame

from client.core import Engine
from client.ui import NEON_PURPLE, NEON_PURPLE_SWITCH, Button, ToggleSwitch

from .scene import Scene

# Scène de pause : s'affiche PAR-DESSUS la scène de jeu (elle n'est pas remplacée,
# juste empilée). Comme process() renvoie False, la scène de jeu en dessous
# ne se met plus à jour tant que la pause est active (mais reste visible en fond
# puisqu'on ne redessine pas par-dessus tout l'écran ici).


@final
class PauseScene(Scene):
    _screen: pygame.Surface

    def __init__(self, engine: Engine):
        super().__init__()
        self._screen = engine.screen
        self._engine = engine

        w, h = self._screen.get_size()
        self._btn_resume = Button(
            "Reprendre", NEON_PURPLE, 28, 12, 10, 18, on_click=self._resume
        )
        self._btn_quit = Button(
            "Quitter", NEON_PURPLE, 28, 12, 10, 18, on_click=self._quit
        )
        self._font_label = pygame.font.SysFont("Arial", 18)
        # Calcul de la position pour centrer "Musique" + switch horizontalement
        label_w, _ = self._font_label.size("Musique")
        gap, switch_w, switch_h = 10, 50, 28
        total_w = label_w + gap + switch_w
        self._sound_label_x = w // 2 - total_w // 2  # bord gauche du label
        initial_music_on = (
            pygame.mixer.music.get_volume() > 0
        )  # True si la musique est active (volume > 0)
        self._sound_switch = ToggleSwitch(
            NEON_PURPLE_SWITCH,
            switch_w,
            switch_h,
            value=initial_music_on,  # état initial calé sur le volume actuel
            on_toggle=self._toggle_music,  # callback appelé à chaque bascule
        )
        switch_cx = (
            w // 2 - total_w // 2 + label_w + gap + switch_w // 2
        )  # centre du switch
        switch_y = h // 2 + 110 - switch_h // 2

        self._btn_resume.set_rect(w // 2, h // 2 - 30)
        self._btn_quit.set_rect(w // 2, h // 2 + 35)
        self._sound_switch.set_rect(switch_cx, switch_y)

    def _toggle_music(self, enabled: bool) -> None:
        # Met le volume à 1.0 si activé, 0.0 si désactivé
        pygame.mixer.music.set_volume(1.0 if enabled else 0.0)

    def _resume(self) -> None:
        """Retire la scène de pause du sommet de la pile pour revenir au jeu."""
        self._engine.sm.pop()

    def _quit(self) -> None:
        self._engine.stop()

    @override
    def on_enter(self) -> None:
        pass

    @override
    def on_exit(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        # Échap ou P permettent aussi de reprendre la partie (pas seulement le bouton)
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            key = cast(int, event.key)
            if key in (pygame.K_ESCAPE, pygame.K_p):
                self._resume()

        for btn in (self._btn_resume, self._btn_quit):
            btn.update(dt, events)
            btn.draw(self._screen)

        # Affiche le libellé "Musique" à côté de l'interrupteur
        label = self._font_label.render("Musique", True, pygame.Color(200, 184, 255))
        self._screen.blit(
            label,
            (
                self._sound_label_x,
                self._sound_switch.rect.centery - label.get_height() // 2,
            ),
        )
        self._sound_switch.update(dt, events)
        self._sound_switch.draw(self._screen)

        # Bloque la mise à jour de la scène de jeu tant que la pause est active
        return False
