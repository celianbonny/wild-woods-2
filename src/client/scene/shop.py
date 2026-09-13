from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from typing import cast, final, override

import pygame

from client.component import Health, Inventory, ItemKind, Weapon
from client.core import Engine
from client.ui.components import NEON_PURPLE, Button

from .scene import Scene

# Scène de la boutique du campement : permet au joueur de dépenser son or
# pour améliorer ses PV, la cadence de tir ou les dégâts de son arme,
# ou pour déclencher la victoire une fois assez d'or accumulé.

_GOLD = pygame.Color(255, 215, 0)
_WHITE = pygame.Color(255, 255, 255)
_GRAY = pygame.Color(160, 160, 180)
_BORDER = pygame.Color(106, 79, 207)
_RED = pygame.Color(200, 70, 70)


@dataclass
class _Upgrade:
    """Représente une amélioration achetable dans la boutique."""
    label: str
    desc: str
    base_cost: int      # Coût de la première amélioration
    increment: int       # Augmentation du coût à chaque nouvel achat
    count: int = field(default=0)  # Nombre de fois déjà achetée

    def cost(self) -> int:
        """Coût de la prochaine amélioration (augmente à chaque achat)."""
        return self.base_cost + self.count * self.increment


@final
class ShopScene(Scene):
    def __init__(
        self,
        engine: Engine,
        hp: Health,
        weapon: Weapon,
        inv: Inventory,
        on_win: Callable[[], None],
        purchase_counts: list[int],
    ):
        super().__init__()
        self._engine = engine
        self._screen = engine.screen
        self._hp = hp
        self._weapon = weapon
        self._inv = inv
        self._on_win = on_win  # Callback appelé quand le joueur "achète" la victoire
        # Compteurs d'achats persistants, partagés avec la scène de jeu, afin que
        # les prix restent cohérents si le joueur quitte puis rouvre la boutique
        self._purchase_counts = purchase_counts

        # Définit les 3 améliorations disponibles, avec leur nombre d'achats déjà réalisés
        self._upgrades = [
            _Upgrade("+1 Vie", "Augmente les PV max de 1", 5, 1, purchase_counts[0]),
            _Upgrade(
                "Cadence +10%",
                "Réduit le délai de tir de 10%",
                2,
                2,
                purchase_counts[1],
            ),
            _Upgrade(
                "Dégâts +25%", "Augmente les dégâts de 25%", 2, 1, purchase_counts[2]
            ),
        ]

        w, h = self._screen.get_size()

        # Capture the rendered game frame — push happens after esper.process so it's fresh
        # (on capture une image du jeu en fond, pour donner l'impression que la boutique
        # s'ouvre "par-dessus" la partie en cours, sans redessiner le monde du jeu)
        self._bg = engine.screen.copy()

        # Voile semi-transparent sombre par-dessus l'image du jeu, pour assombrir le fond
        self._overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        self._overlay.fill((10, 5, 20, 160))

        self._font_title = pygame.font.SysFont("Arial", 52, bold=True)
        self._font_name = pygame.font.SysFont("Arial", 22, bold=True)
        self._font_small = pygame.font.SysFont("Arial", 15)
        self._font_gold = pygame.font.SysFont("Arial", 24, bold=True)
        self._font_hint = pygame.font.SysFont("Arial", 14)

        # Un bouton "Acheter" par amélioration, chacun sachant quel index il concerne
        # grâce à functools.partial
        self._btns = [
            Button("Acheter", NEON_PURPLE, 14, 8, 8, 18, on_click=partial(self._buy, i))
            for i in range(3)
        ]

        self._btn_win = Button(
            "VICTOIRE - 100 pièces",
            NEON_PURPLE,
            20,
            14,
            10,
            22,
            on_click=self._buy_win,
        )
        self._btn_win.rect.width = w - 160
        self._btn_win.rect.height = 70

    def _buy(self, i: int) -> None:
        """Achète l'amélioration d'index `i` si le joueur a assez d'or."""
        upg = self._upgrades[i]
        gold = self._inv.count(ItemKind.GOLD)
        if gold < upg.cost():
            return
        self._inv.counts[ItemKind.GOLD] = gold - upg.cost()
        upg.count += 1
        self._purchase_counts[i] = upg.count
        # Applique l'effet réel de l'amélioration selon son index
        if i == 0:
            # +1 Vie : augmente à la fois le maximum et les PV actuels
            self._hp.max += 1
            self._hp.current += 1
        elif i == 1:
            # Cadence +10% : réduit le temps de recharge de 10% (minimum 0.05s)
            self._weapon.cooldown_max = max(0.05, self._weapon.cooldown_max * 0.9)
        else:
            # Dégâts +25% : augmente les dégâts de l'arme de 25% (minimum 1)
            self._weapon.damage = max(1, int(self._weapon.damage * 1.25))

    def _buy_win(self) -> None:
        """Déclenche la victoire si le joueur possède au moins 100 pièces d'or."""
        gold = self._inv.count(ItemKind.GOLD)
        if gold < 100:
            return
        self._inv.counts[ItemKind.GOLD] = gold - 100
        self._on_win()

    @override
    def on_enter(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        w, h = self._screen.get_size()

        # La touche E permet de fermer la boutique et de revenir à la partie
        for event in events:
            if event.type == pygame.KEYDOWN and cast(int, event.key) == pygame.K_e:
                self._engine.sm.pop()
                return False

        # Dessine le fond figé du jeu, puis le voile sombre par-dessus
        self._screen.blit(self._bg, (0, 0))
        self._screen.blit(self._overlay, (0, 0))

        # Title
        title_s = self._font_title.render("BOUTIQUE", True, _WHITE)
        self._screen.blit(title_s, title_s.get_rect(center=(w // 2, 60)))

        # Gold
        gold = self._inv.count(ItemKind.GOLD)
        gold_s = self._font_gold.render(f"Or : {gold}", True, _GOLD)
        self._screen.blit(gold_s, gold_s.get_rect(center=(w // 2, 115)))

        # Layout zones
        # Calcule la disposition : 3 cartes d'amélioration en haut, bouton de victoire en bas
        win_h = 100
        win_top = h - win_h - 20
        card_top = 150
        card_h = win_top - card_top - 20
        card_w = (w - 160 - 40) // 3  # 3 cards, 2 gaps of 20

        for i, (upg, btn) in enumerate(zip(self._upgrades, self._btns)):
            x = 80 + i * (card_w + 20)
            cx = x + card_w // 2

            # Card background
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            card_surf.fill((20, 15, 40, 230))
            pygame.draw.rect(
                card_surf, _BORDER, card_surf.get_rect(), width=2, border_radius=12
            )
            self._screen.blit(card_surf, (x, card_top))

            # Name
            name_s = self._font_name.render(upg.label, True, _WHITE)
            self._screen.blit(name_s, name_s.get_rect(centerx=cx, top=card_top + 22))

            # Description
            desc_s = self._font_small.render(upg.desc, True, _GRAY)
            self._screen.blit(desc_s, desc_s.get_rect(centerx=cx, top=card_top + 60))

            # Purchase count
            count_s = self._font_small.render(f"Acheté : {upg.count}×", True, _GRAY)
            self._screen.blit(count_s, count_s.get_rect(centerx=cx, top=card_top + 85))

            # Cost (colored by affordability)
            # Le prix s'affiche en doré si le joueur peut se le permettre, en rouge sinon
            cost = upg.cost()
            cost_s = self._font_name.render(
                f"{cost} pièces", True, _GOLD if gold >= cost else _RED
            )
            self._screen.blit(cost_s, cost_s.get_rect(centerx=cx, top=card_top + 118))

            # Buy button
            btn.enabled = gold >= cost
            btn.set_rect(cx, card_top + card_h - btn.rect.height - 20)
            btn.update(dt, events)
            btn.draw(self._screen)

        # Win button (wide, bottom)
        self._btn_win.enabled = gold >= 100
        self._btn_win.rect.width = w - 160
        self._btn_win.set_rect(w // 2, win_top)
        self._btn_win.update(dt, events)
        self._btn_win.draw(self._screen)

        # Close hint
        hint_s = self._font_hint.render("E — Fermer la boutique", True, _GRAY)
        self._screen.blit(hint_s, hint_s.get_rect(centerx=w // 2, bottom=h - 6))

        return False
