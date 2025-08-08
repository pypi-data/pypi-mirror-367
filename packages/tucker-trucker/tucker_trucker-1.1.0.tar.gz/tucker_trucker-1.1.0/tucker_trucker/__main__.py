"""
Tucker Trucker - Main entry point for the game package
"""

def main():
    """Entry point for the tucker-trucker command"""
    from .main import main as game_main
    game_main()

if __name__ == "__main__":
    main()
