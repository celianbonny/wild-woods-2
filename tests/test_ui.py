import pygame
import pytest

from client.ui import (
    NEON_PURPLE,
    NEON_PURPLE_SWITCH,
    Button,
    ToggleSwitch,
    lerp_color,
)

# Tests unitaires des composants d'interface (Button, ToggleSwitch) et de la
# fonction utilitaire lerp_color.


@pytest.fixture(scope="module", autouse=True)
def init_pygame_font():
    """Initialise le module de police pygame pour tout le fichier de test
    (nécessaire pour créer des Button/ToggleSwitch, qui rendent du texte),
    puis le libère à la fin."""
    pygame.font.init()
    yield
    pygame.font.quit()


def test_lerp_color_clamps_bounds():
    # Vérifie que les valeurs de t en dehors de [0, 1] sont "clampées"
    # (ramenées aux bornes) plutôt que de produire des couleurs invalides
    a = pygame.Color(0, 0, 0)
    b = pygame.Color(255, 255, 255)

    assert lerp_color(a, b, -1.0) == a
    assert lerp_color(a, b, 2.0) == b


def test_button_click_invokes_handler(monkeypatch):
    clicked = {"value": False}

    def on_click() -> None:
        clicked["value"] = True

    button = Button("OK", NEON_PURPLE, 10, 5, 4, on_click=on_click)
    button.set_rect(50, 20)

    # Simule la souris positionnée exactement sur le centre du bouton
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: button.rect.center)
    # Simule un clic gauche (button=1)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
    button.update(0.016, [event])

    # Le callback on_click doit avoir été déclenché
    assert clicked["value"] is True


def test_button_disabled_skips_interaction(monkeypatch):
    button = Button("OK", NEON_PURPLE, 10, 5, 4, enabled=False)
    button.set_rect(50, 20)

    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: button.rect.center)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
    button.update(0.016, [event])

    surface = pygame.Surface((100, 60))
    button.draw(surface)

    # Un bouton désactivé doit rester désactivé (et ne pas planter au dessin)
    assert button.enabled is False


def test_toggle_switch_toggles_on_click(monkeypatch):
    values: list[bool] = []

    def on_toggle(value: bool) -> None:
        values.append(value)

    switch = ToggleSwitch(NEON_PURPLE_SWITCH, 60, 28, value=False, on_toggle=on_toggle)
    switch.set_rect(50, 20)

    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: switch.rect.center)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
    switch.update(0.016, [event])

    # Le clic doit avoir basculé la valeur de False à True, et déclenché le callback
    assert switch.value is True
    assert values == [True]


def test_toggle_switch_disabled_draws(monkeypatch):
    switch = ToggleSwitch(NEON_PURPLE_SWITCH, 60, 28, value=False, enabled=False)
    switch.set_rect(50, 20)

    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: switch.rect.center)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
    switch.update(0.016, [event])

    surface = pygame.Surface((100, 60))
    switch.draw(surface)

    # Un interrupteur désactivé ne doit pas réagir au clic et rester désactivé
    assert switch.enabled is False
