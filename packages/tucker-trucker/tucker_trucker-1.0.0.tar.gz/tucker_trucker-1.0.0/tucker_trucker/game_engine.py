"""
Main game engine that coordinates all game systems
"""

import pygame
import random
from .constants import *
from .entities import Player, Market, Position
from .ui import UI

class GameEngine:
    """Main game engine class"""
    def __init__(self, screen):
        self.screen = screen
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.markets = []
        self.ui = UI(screen)
        
        # Game state
        self.game_time = 0.0  # Game time in seconds
        self.day_number = 1
        
        # Initialize markets
        self.create_markets()
        
    def create_markets(self):
        """Create markets around the game world"""
        market_names = [
            "Doggy Depot", 
            "Paws & Claws Market", 
            "The Bone Zone", 
            "Furry Friends Store", 
            "Pet Paradise"
        ]
        
        # Create markets at different locations
        market_positions = [
            (200, 150),   # Top left
            (1000, 200),  # Top right  
            (150, 600),   # Bottom left
            (950, 650),   # Bottom right
            (600, 400)    # Center
        ]
        
        for i, (name, pos) in enumerate(zip(market_names, market_positions)):
            market = Market(name, Position(pos[0], pos[1]))
            self.markets.append(market)
    
    def handle_event(self, event):
        """Handle game events"""
        self.ui.handle_event(event, self.player, self.markets)
    
    def update(self, dt):
        """Update game state"""
        self.game_time += dt
        
        # Handle player movement
        keys = pygame.key.get_pressed()
        dx = dy = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707  # 1/sqrt(2)
            dy *= 0.707
        
        self.player.move(dx, dy, dt)
        
        # Update markets
        for market in self.markets:
            market.update(dt)
        
        # Check for day progression
        if self.game_time > GAME_DAY_LENGTH:
            self.advance_day()
    
    def advance_day(self):
        """Advance to the next day"""
        self.day_number += 1
        self.game_time = 0.0
        
        # Reset market conditions for new day
        for market in self.markets:
            for good in market.goods.values():
                # Add some random stock
                good.quantity += random.randint(1, 5)
                # Reset demand with some variation
                good.demand = random.uniform(0.5, 1.5)
    
    def render(self):
        """Render the game"""
        # Clear screen with a grass-like background
        self.screen.fill(GREEN)
        
        # Draw roads (simple grid)
        road_color = DARK_GRAY
        # Horizontal roads
        for y in range(0, SCREEN_HEIGHT, 200):
            pygame.draw.rect(self.screen, road_color, (0, y - 10, SCREEN_WIDTH, 20))
        # Vertical roads  
        for x in range(0, SCREEN_WIDTH, 200):
            pygame.draw.rect(self.screen, road_color, (x - 10, 0, 20, SCREEN_HEIGHT))
        
        # Draw game entities
        self.ui.draw_markets(self.markets)
        self.ui.draw_player(self.player)
        
        # Draw UI elements
        self.ui.draw_player_info(self.player)
        self.ui.draw_inventory(self.player)
        self.ui.draw_market_info(self.ui.selected_market)
        
        # Draw day counter
        day_text = self.ui.large_font.render(f"Day {self.day_number}", True, BLACK)
        self.screen.blit(day_text, (SCREEN_WIDTH // 2 - 50, 10))
        
        # Draw game time progress bar
        time_progress = self.game_time / GAME_DAY_LENGTH
        bar_width = 200
        bar_rect = pygame.Rect(SCREEN_WIDTH // 2 - bar_width // 2, 50, bar_width, 10)
        pygame.draw.rect(self.screen, WHITE, bar_rect)
        pygame.draw.rect(self.screen, BLACK, bar_rect, 2)
        
        progress_rect = pygame.Rect(bar_rect.x, bar_rect.y, bar_width * time_progress, 10)
        pygame.draw.rect(self.screen, YELLOW, progress_rect)
