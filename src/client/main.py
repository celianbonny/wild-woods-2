from client.core import Difficulty, Engine
from client.scene.main_menu import MainMenuScene


def main() -> int:
    # Crée le moteur du jeu (fenêtre, boucle principale, gestionnaire de scènes...)
    engine = Engine()

    def go_to_menu() -> None:
        # Vide toutes les scènes empilées et revient au menu principal
        # (utilisé par exemple après une partie terminée ou pour quitter une partie)
        engine.sm.clear()
        engine.sm.push(MainMenuScene, engine, start_game)

    def start_game(difficulty: Difficulty) -> None:
        # Import différé pour éviter les imports circulaires entre main.py et game.py
        from client.scene.game import GameScene

        # On retire le menu principal de la pile de scènes...
        engine.sm.pop()
        # ...puis on ajoute la scène de jeu avec la difficulté choisie
        # et la fonction à appeler pour revenir au menu (go_to_menu)
        engine.sm.push(GameScene, engine, difficulty, go_to_menu)

    # Au lancement, on affiche d'abord le menu principal
    engine.sm.push(MainMenuScene, engine, start_game)
    # Lance la boucle de jeu et renvoie le code de sortie
    return engine.run()


if __name__ == "__main__":
    # Point d'entrée du programme : lance main() et transmet son code de retour au système
    raise SystemExit(main())