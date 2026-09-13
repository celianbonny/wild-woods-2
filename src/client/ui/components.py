from typing import Callable, ClassVar, cast, final

import pygame

from .helper import lerp_color

# Composants d'interface réutilisables : bouton cliquable animé (Button) et
# interrupteur à bascule (ToggleSwitch), tous deux avec des transitions de
# couleur douces (survol/pression) plutôt que des changements instantanés.


@final
class Button:
    """Bouton cliquable avec animation de survol et de pression, et son
    (optionnel) au premier survol."""
    _hover_sound: ClassVar[pygame.mixer.Sound | None] = None

    def __init__(
        # var avec arguments par défaut à mettre à la fin
        self,
        text: str,
        colors: dict[str, pygame.Color],
        padding_x: int,  # marge intérieure gauche/droite
        padding_y: int,  # marge intérieure haut/bas
        radius: int,  # arrondi des coins
        font_size: int = 18,
        on_click: Callable[[], None] | None = None,
        enabled: bool = True,
    ):
        self.text = text
        self.colors = colors
        self.on_click = on_click
        self.enabled = enabled
        self._radius = radius

        # Police et taille du bouton calculées à partir du texte + marges
        self._font = pygame.font.SysFont("Arial", font_size)
        text_w, text_h = self._font.size(text)
        self.rect = pygame.Rect(0, 0, text_w + padding_x * 2, text_h + padding_y * 2)

        # t = 0 : état normal, t = 1 : état pleinement hover/pressé
        self._hover_t: float = 0.0
        self._press_t: float = 0.0
        self._was_hovered: bool = False

    @classmethod
    def _get_hover_sound(cls) -> pygame.mixer.Sound | None:
        """Charge et met en cache (au niveau de la classe) le son de survol,
        partagé par tous les boutons pour éviter de le recharger à chaque fois."""
        if cls._hover_sound is not None:
            return cls._hover_sound

        try:
            if cast(None | tuple[int, int, int], pygame.mixer.get_init()) is None:
                pygame.mixer.init()
            cls._hover_sound = pygame.mixer.Sound("assets/sound/hover.wav")
        except pygame.error:
            cls._hover_sound = None
        return cls._hover_sound

    def set_rect(self, cx: int, y: int) -> None:
        """Place le bouton centré horizontalement sur cx, bord supérieur à y."""
        self.rect.centerx = cx
        self.rect.y = y

    def update(self, dt: float, events: list[pygame.event.Event]) -> None:
        # Aucune interaction si le bouton est désactivé
        if not self.enabled:
            self._hover_t = 0.0
            self._press_t = 0.0
            self._was_hovered = False
            return

        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        if hovered and not self._was_hovered:
            sound = self._get_hover_sound()
            if sound is not None:
                sound.play()
        self._was_hovered = hovered
        speed = 8.0

        # Transition smooth vers 1 si survolé, vers 0 sinon
        self._hover_t = max(
            0.0, min(1.0, self._hover_t + speed * dt * (1.0 if hovered else -1.0))
        )

        # L'effet de pression disparaît progressivement après le clic
        self._press_t = max(0.0, self._press_t - speed * 2 * dt)

        for event in events:
            if event.type != pygame.MOUSEBUTTONDOWN:
                continue
            if cast(int, event.button) == 1 and hovered:
                self._press_t = 1.0  # Déclenche l'animation de pression
                if self.on_click:
                    self.on_click()

    def draw(self, surface: pygame.Surface) -> None:
        c = self.colors

        # Rendu simplifié sans effets si désactivé
        if not self.enabled:
            pygame.draw.rect(
                surface, c["bg_disabled"], self.rect, border_radius=self._radius
            )
            pygame.draw.rect(
                surface,
                c["border_disabled"],
                self.rect,
                width=2,
                border_radius=self._radius,
            )
            label = self._font.render(self.text, True, c["text_disabled"])
            surface.blit(label, label.get_rect(center=self.rect.center))
            return

        # Interpolation des couleurs selon l'état hover puis press
        bg = lerp_color(
            lerp_color(c["bg"], c["bg_hover"], self._hover_t),
            c["bg_press"],
            self._press_t,
        )
        border = lerp_color(c["border"], c["border_hover"], self._hover_t)
        text_c = lerp_color(c["text"], c["text_hover"], self._hover_t)

        pygame.draw.rect(surface, bg, self.rect, border_radius=self._radius)
        pygame.draw.rect(
            surface, border, self.rect, width=2, border_radius=self._radius
        )

        # Rendu du texte centré dans le bouton
        label = self._font.render(self.text, True, text_c)
        surface.blit(label, label.get_rect(center=self.rect.center))


@final
class ToggleSwitch:
    """Interrupteur à bascule (ex: activer/désactiver la musique) avec une
    animation de glissement du rond entre les positions on/off."""

    def __init__(
        self,
        colors: dict[str, pygame.Color],
        width: int,
        height: int,
        value: bool = True,
        on_toggle: Callable[[bool], None] | None = None,
        enabled: bool = True,
    ):
        self.colors = colors
        self.on_toggle = on_toggle
        self.enabled = enabled
        self.value = value
        self.rect = pygame.Rect(0, 0, width, height)

        self._slide_t: float = 1.0 if value else 0.0
        self._hover_t: float = 0.0

    def set_rect(self, cx: int, y: int) -> None:
        """Place le switch centré horizontalement sur cx, bord supérieur à y."""
        self.rect.centerx = cx
        self.rect.y = y

    def update(self, dt: float, events: list[pygame.event.Event]) -> None:
        speed = 8.0

        if not self.enabled:
            self._hover_t = 0.0
            return

        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        self._hover_t = max(
            0.0, min(1.0, self._hover_t + speed * dt * (1.0 if hovered else -1.0))
        )

        # Animation du glissement
        target = 1.0 if self.value else 0.0
        self._slide_t += (target - self._slide_t) * min(1.0, speed * 2 * dt)

        for event in events:
            if event.type != pygame.MOUSEBUTTONDOWN:
                continue
            if cast(int, event.button) == 1 and hovered:
                self.value = not self.value
                if self.on_toggle:
                    self.on_toggle(self.value)

    def draw(self, surface: pygame.Surface) -> None:
        c = self.colors
        r = self.rect.height // 2  # rayon de la piste
        knob_r = r - 3  # rayon du rond

        if not self.enabled:
            pygame.draw.rect(surface, c["track_disabled"], self.rect, border_radius=r)
            pygame.draw.circle(
                surface,
                c["knob_disabled"],
                (self.rect.x + r, self.rect.centery),
                knob_r,
            )
            return

        track = lerp_color(c["track_off"], c["track_on"], self._slide_t)
        track = lerp_color(track, c["track_hover"], self._hover_t * 0.3)
        pygame.draw.rect(surface, track, self.rect, border_radius=r)

        # Position du rond : de (x + r) à (x + width - r)
        knob_x = int(self.rect.x + r + (self.rect.width - 2 * r) * self._slide_t)
        pygame.draw.circle(surface, c["knob"], (knob_x, self.rect.centery), knob_r)


# Palette de couleurs "néon violet" utilisée par défaut pour les boutons et interrupteurs
NEON_PURPLE: dict[str, pygame.Color] = {
    "bg": pygame.Color(22, 18, 42),  # fond normal
    "bg_hover": pygame.Color(30, 24, 64),  # fond au survol
    "bg_press": pygame.Color(18, 15, 32),  # fond au clic
    "border": pygame.Color(106, 79, 207),  # bordure normale
    "border_hover": pygame.Color(160, 125, 255),  # bordure au survol
    "text": pygame.Color(200, 184, 255),  # texte normal
    "text_hover": pygame.Color(255, 255, 255),  # texte au survol
    "bg_disabled": pygame.Color(17, 17, 24),  # fond si désactivé
    "border_disabled": pygame.Color(51, 51, 51),  # bordure si désactivé
    "text_disabled": pygame.Color(85, 85, 85),  # texte si désactivé
}

NEON_PURPLE_SWITCH: dict[str, pygame.Color] = {
    "track_off": pygame.Color(40, 35, 60),  # piste éteinte
    "track_on": pygame.Color(106, 79, 207),  # piste allumée
    "track_hover": pygame.Color(160, 125, 255),  # piste au survol
    "knob": pygame.Color(230, 220, 255),  # rond
    "track_disabled": pygame.Color(25, 25, 35),  # piste désactivée
    "knob_disabled": pygame.Color(60, 60, 70),  # rond désactivé
}
