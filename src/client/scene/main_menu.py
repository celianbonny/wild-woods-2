from collections.abc import Callable
from typing import final, override

import pygame

from client.core import DEFAULT_DIFFICULTY, DIFFICULTIES, Difficulty, Engine
from client.ui.components import NEON_PURPLE, Button

from .scene import Scene

# Scène du menu principal : titre, sélecteur de difficulté animé (planète tournante)
# à gauche, et boutons "Jouer" / "Paramètres" / "Quitter" à droite.

_PLANET_FRAME_DURATION = 0.1  # Durée d'affichage de chaque frame de l'animation de la planète
_BUTTON_GAP = 18              # Espace vertical entre les boutons du menu
_ARROW_SIZE = 56              # Taille des flèches de changement de difficulté
_ARROW_GAP = 45               # Espace entre les flèches et l'image de la planète


def _slice_strip(sheet: pygame.Surface, frame_size: int) -> list[pygame.Surface]:
    """Cut a horizontal spritesheet strip into square frames."""
    # Découpe une planche de sprites (une seule ligne d'images côte à côte)
    # en autant de frames carrées que possible
    count = sheet.get_width() // frame_size
    return [
        sheet.subsurface(pygame.Rect(i * frame_size, 0, frame_size, frame_size))
        for i in range(count)
    ]


@final
class MainMenuScene(Scene):
    def __init__(self, engine: Engine, on_start: Callable[[Difficulty], None]):
        super().__init__()
        self._engine = engine
        self._screen = engine.screen
        self._on_start = on_start  # Callback appelé avec la difficulté choisie au clic sur "Jouer"
        self._font = pygame.font.SysFont("Arial", 42)
        self._subtitle = pygame.font.SysFont("Arial", 22)
        self._difficulty_font = pygame.font.SysFont("Arial", 30, bold=True)
        self._start_requested = False  # Drapeau pour différer le lancement à la fin de process()

        width, height = self._screen.get_size()

        # Calcul des positions verticales du titre/sous-titre
        self._title_y = height // 8
        self._subtitle_y = self._title_y + 45
        content_top = self._subtitle_y + self._subtitle.get_height() // 2 + 30
        content_center_y = (content_top + height) // 2

        # Difficulty selector (left column): each difficulty's strip scaled once.
        # (chaque planche d'images de difficulté n'est chargée et redimensionnée qu'une fois,
        # même si plusieurs difficultés partagent la même image)
        diameter = int(min(width * 0.35, height * 0.5))
        self._frames_by_sheet: dict[str, list[pygame.Surface]] = {}
        for difficulty in DIFFICULTIES:
            if difficulty.sheet_path in self._frames_by_sheet:
                continue
            sheet = pygame.image.load(difficulty.sheet_path).convert_alpha()
            self._frames_by_sheet[difficulty.sheet_path] = [
                pygame.transform.scale(frame, (diameter, diameter))
                for frame in _slice_strip(sheet, difficulty.frame_size)
            ]
        self._difficulty_index = DEFAULT_DIFFICULTY
        self._frame_index = 0
        self._frame_timer = 0.0

        # Calcule les positions de la planète et des flèches de navigation autour d'elle
        arrow_y = content_center_y - _ARROW_SIZE // 2
        left_arrow_cx = width // 4 - diameter // 2 - 30
        planet_left = left_arrow_cx + _ARROW_SIZE // 2 + _ARROW_GAP
        planet_cx = planet_left + diameter // 2
        planet_top = content_center_y - diameter // 2
        right_arrow_cx = planet_left + diameter + _ARROW_GAP + _ARROW_SIZE // 2

        self._planet_pos = (planet_left, planet_top)
        self._difficulty_name_pos = (planet_cx, planet_top - 28)

        self._btn_prev = Button(
            "<", NEON_PURPLE, 18, 12, 8, 28, on_click=self._prev_difficulty
        )
        self._btn_next = Button(
            ">", NEON_PURPLE, 18, 12, 8, 28, on_click=self._next_difficulty
        )
        for arrow in (self._btn_prev, self._btn_next):
            arrow.rect.size = (_ARROW_SIZE, _ARROW_SIZE)
        self._btn_prev.set_rect(left_arrow_cx, arrow_y)
        self._btn_next.set_rect(right_arrow_cx, arrow_y)

        # Right column: a vertical stack of menu buttons, centered vertically.
        right_cx = width * 3 // 4
        self._buttons = [
            Button("Jouer", NEON_PURPLE, 30, 12, 8, 24, on_click=self._start_game),
            Button("Paramètres", NEON_PURPLE, 30, 12, 8, 24, enabled=False),
            Button("Quitter", NEON_PURPLE, 30, 12, 8, 24, on_click=self._quit),
        ]
        # Normalize every button to the widest/tallest so the stack is uniform.
        # (tous les boutons prennent la taille du plus grand pour un alignement propre)
        uniform_w = max(b.rect.width for b in self._buttons)
        uniform_h = max(b.rect.height for b in self._buttons)
        for button in self._buttons:
            button.rect.size = (uniform_w, uniform_h)

        # Empile les boutons verticalement, centrés autour de content_center_y
        total_h = uniform_h * len(self._buttons) + _BUTTON_GAP * (
            len(self._buttons) - 1
        )
        y = content_center_y - total_h // 2
        for button in self._buttons:
            button.set_rect(right_cx, y)
            y += uniform_h + _BUTTON_GAP

    def _start_game(self) -> None:
        # On ne lance pas la partie tout de suite : on se contente de le noter,
        # le vrai lancement se fait à la fin de process() (voir plus bas)
        self._start_requested = True

    def _quit(self) -> None:
        self._engine.stop()

    def _prev_difficulty(self) -> None:
        """Sélectionne la difficulté précédente (boucle sur la dernière si on est au début)."""
        self._difficulty_index = (self._difficulty_index - 1) % len(DIFFICULTIES)
        self._frame_index = 0

    def _next_difficulty(self) -> None:
        """Sélectionne la difficulté suivante (boucle sur la première si on est à la fin)."""
        self._difficulty_index = (self._difficulty_index + 1) % len(DIFFICULTIES)
        self._frame_index = 0

    def _current_frames(self) -> list[pygame.Surface]:
        """Renvoie les frames d'animation correspondant à la difficulté actuellement sélectionnée."""
        return self._frames_by_sheet[DIFFICULTIES[self._difficulty_index].sheet_path]

    def _advance_animation(self, dt: float) -> None:
        """Fait avancer l'animation de la planète (boucle infinie)."""
        frames = self._current_frames()
        self._frame_timer += dt
        if self._frame_timer >= _PLANET_FRAME_DURATION:
            steps = int(self._frame_timer / _PLANET_FRAME_DURATION)
            self._frame_timer -= steps * _PLANET_FRAME_DURATION
            self._frame_index = (self._frame_index + steps) % len(frames)

    @override
    def on_enter(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        width, _ = self._screen.get_size()
        self._screen.fill(pygame.Color(20, 20, 30))

        # Titre et sous-titre du jeu
        title = self._font.render("Wild Woods 2", True, pygame.Color("white"))
        subtitle = self._subtitle.render(
            "Survivez à l'apocalypse", True, pygame.Color(180, 180, 200)
        )
        self._screen.blit(title, title.get_rect(center=(width // 2, self._title_y)))
        self._screen.blit(
            subtitle, subtitle.get_rect(center=(width // 2, self._subtitle_y))
        )

        # Difficulty selector.
        self._advance_animation(dt)
        self._screen.blit(self._current_frames()[self._frame_index], self._planet_pos)

        name = DIFFICULTIES[self._difficulty_index].name
        name_surf = self._difficulty_font.render(name, True, pygame.Color("white"))
        self._screen.blit(
            name_surf, name_surf.get_rect(center=self._difficulty_name_pos)
        )

        for arrow in (self._btn_prev, self._btn_next):
            arrow.update(dt, events)
            arrow.draw(self._screen)

        for button in self._buttons:
            button.update(dt, events)
            button.draw(self._screen)

        # Lance réellement la partie ici (après l'affichage de cette frame),
        # pour être sûr que tous les boutons ont bien été mis à jour avant de changer de scène
        if self._start_requested:
            self._start_requested = False
            self._on_start(DIFFICULTIES[self._difficulty_index])
            return False

        return False
