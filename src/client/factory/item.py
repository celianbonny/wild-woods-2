import esper
import pygame

from client.component import Hitbox, ItemKind, ItemTag, Position, Sprite

# Fabrique (factory) permettant de créer les entités "objet au sol" ramassables.

# Association entre chaque type d'objet et le chemin de son image
ITEM_SPRITE_PATHS: dict[ItemKind, str] = {
    ItemKind.GOLD: "assets/sprite/icons/coin.png",
    ItemKind.HEALTH: "assets/sprite/icons/hearth.png",
    ItemKind.LIMBS: "assets/sprite/icons/limbs.png",
}

_ITEM_DROP_SIZE = 20  # Taille (en pixels) des objets affichés au sol


def create_item(pos: Position, kind: ItemKind) -> None:
    """Crée une entité "objet au sol" du type `kind` à la position `pos`."""
    raw = pygame.image.load(ITEM_SPRITE_PATHS[kind]).convert_alpha()
    surface = pygame.transform.scale(raw, (_ITEM_DROP_SIZE, _ITEM_DROP_SIZE))
    esper.create_entity(
        Position(pos.x, pos.y),
        Sprite(surface),
        ItemTag(kind),
        Hitbox(width=_ITEM_DROP_SIZE, height=_ITEM_DROP_SIZE),
    )
