# mypy: ignore-errors
# pyright: reportCallIssue=false, reportArgumentType=false, reportReturnType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportGeneralTypeIssues=false
from typing import overload

import esper

# Petit "wrapper" typé autour de esper.get_components().
# La bibliothèque esper n'est pas fortement typée (elle accepte un nombre variable
# de types de composants), ce qui empêche les outils d'analyse statique de connaître
# le type exact du résultat. Les surcharges (@overload) ci-dessous permettent de
# déclarer explicitement le type de retour pour 5, 6, 7 ou 8 composants,
# afin que l'auto-complétion et le vérificateur de types fonctionnent correctement.


@overload
def get_components[C1, C2, C3, C4, C5](
    c1: type[C1],
    c2: type[C2],
    c3: type[C3],
    c4: type[C4],
    c5: type[C5],
    /,
) -> list[tuple[int, tuple[C1, C2, C3, C4, C5]]]: ...
@overload
def get_components[C1, C2, C3, C4, C5, C6](
    c1: type[C1],
    c2: type[C2],
    c3: type[C3],
    c4: type[C4],
    c5: type[C5],
    c6: type[C6],
    /,
) -> list[tuple[int, tuple[C1, C2, C3, C4, C5, C6]]]: ...
@overload
def get_components[C1, C2, C3, C4, C5, C6, C7](
    c1: type[C1],
    c2: type[C2],
    c3: type[C3],
    c4: type[C4],
    c5: type[C5],
    c6: type[C6],
    c7: type[C7],
    /,
) -> list[tuple[int, tuple[C1, C2, C3, C4, C5, C6, C7]]]: ...
@overload
def get_components[C1, C2, C3, C4, C5, C6, C7, C8](
    c1: type[C1],
    c2: type[C2],
    c3: type[C3],
    c4: type[C4],
    c5: type[C5],
    c6: type[C6],
    c7: type[C7],
    c8: type[C8],
    /,
) -> list[tuple[int, tuple[C1, C2, C3, C4, C5, C6, C7, C8]]]: ...


def get_components(*args: type) -> list[tuple[int, tuple[object, ...]]]:
    # Implémentation réelle : on se contente de déléguer à esper,
    # les surcharges ci-dessus ne servent qu'à typer le résultat
    return esper.get_components(*args)
