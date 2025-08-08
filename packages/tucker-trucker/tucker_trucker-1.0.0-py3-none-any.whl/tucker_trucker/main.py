"""
Tucker Trucker - A 2D market timing and strategy game
featuring a Boston Terrier delivering goods around town!
"""

import pygame
import sys
from .game_engine import GameEngine
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def main():
    """Main game loop"""
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tucker Trucker - Boston Terrier Delivery Service")
    clock = pygame.time.Clock()
    
    # Initialize game engine
    game = GameEngine(screen)
    
    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)
        
        # Update game state
        game.update(dt)
        
        # Render everything
        game.render()
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
