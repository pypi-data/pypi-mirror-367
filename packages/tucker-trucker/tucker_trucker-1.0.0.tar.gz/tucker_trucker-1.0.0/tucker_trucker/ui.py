"""
User interface components
"""

import pygame
from .constants import *

class UI:
    """Main UI manager"""
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.large_font = pygame.font.Font(None, 36)
        
        # UI state
        self.show_inventory = False
        self.show_market_info = False
        self.selected_market = None
        self.trade_mode = False
        self.selected_good = None
        self.trade_quantity = 1
    
    def draw_player_info(self, player):
        """Draw player information panel"""
        # Money
        money_text = self.font.render(f"Money: ${player.money:.2f}", True, BLACK)
        self.screen.blit(money_text, (10, 10))
        
        # Cargo capacity
        cargo_text = self.font.render(
            f"Cargo: {player.get_total_cargo()}/{MAX_CARGO_CAPACITY}", 
            True, BLACK
        )
        self.screen.blit(cargo_text, (10, 35))
        
        # Instructions
        instructions = [
            "WASD: Move",
            "E: Toggle Inventory", 
            "R: Interact with Market",
            "ESC: Close menus"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, DARK_GRAY)
            self.screen.blit(text, (10, SCREEN_HEIGHT - 80 + i * 15))
    
    def draw_inventory(self, player):
        """Draw inventory panel"""
        if not self.show_inventory:
            return
            
        # Background panel
        panel_rect = pygame.Rect(SCREEN_WIDTH - 250, 10, 240, 300)
        pygame.draw.rect(self.screen, WHITE, panel_rect)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 2)
        
        # Title
        title = self.font.render("Inventory", True, BLACK)
        self.screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        
        # Goods list
        y_offset = 40
        for good_type in GOODS_TYPES:
            quantity = player.inventory[good_type]
            color = GOODS_COLORS[good_type]
            
            # Color indicator
            color_rect = pygame.Rect(panel_rect.x + 10, panel_rect.y + y_offset, 20, 20)
            pygame.draw.rect(self.screen, color, color_rect)
            pygame.draw.rect(self.screen, BLACK, color_rect, 1)
            
            # Good name and quantity
            text = self.small_font.render(f"{good_type}: {quantity}", True, BLACK)
            self.screen.blit(text, (panel_rect.x + 40, panel_rect.y + y_offset + 2))
            
            y_offset += 25
    
    def draw_market_info(self, market):
        """Draw market information panel"""
        if not self.show_market_info or not market:
            return
            
        # Background panel
        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 50, 400, 400)
        pygame.draw.rect(self.screen, WHITE, panel_rect)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 2)
        
        # Title
        title = self.font.render(f"{market.name}", True, BLACK)
        self.screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        
        # Market money
        money_text = self.small_font.render(f"Market Money: ${market.money:.2f}", True, BLACK)
        self.screen.blit(money_text, (panel_rect.x + 10, panel_rect.y + 35))
        
        # Goods header
        headers = self.small_font.render("Good | Qty | Price | Demand", True, BLACK)
        self.screen.blit(headers, (panel_rect.x + 10, panel_rect.y + 60))
        
        # Goods list
        y_offset = 85
        for good_type in GOODS_TYPES:
            good = market.goods[good_type]
            color = GOODS_COLORS[good_type]
            
            # Color indicator
            color_rect = pygame.Rect(panel_rect.x + 10, panel_rect.y + y_offset, 15, 15)
            pygame.draw.rect(self.screen, color, color_rect)
            pygame.draw.rect(self.screen, BLACK, color_rect, 1)
            
            # Good info
            demand_indicator = "High" if good.demand > 1.2 else "Med" if good.demand > 0.8 else "Low"
            text = self.small_font.render(
                f"{good_type[:4]} | {good.quantity:2d} | ${good.current_price:5.2f} | {demand_indicator}", 
                True, BLACK
            )
            self.screen.blit(text, (panel_rect.x + 30, panel_rect.y + y_offset))
            
            y_offset += 20
        
        # Trading interface
        if self.trade_mode:
            self.draw_trade_interface(panel_rect, market)
    
    def draw_trade_interface(self, panel_rect, market):
        """Draw trading interface within market panel"""
        trade_y = panel_rect.y + 250
        
        # Trade mode indicator
        mode_text = self.small_font.render("TRADE MODE - Select good with 1-5, +/- quantity, B/S to trade", True, RED)
        self.screen.blit(mode_text, (panel_rect.x + 10, trade_y))
        
        if self.selected_good:
            good = market.goods[self.selected_good]
            
            # Selected good info
            selected_text = self.small_font.render(
                f"Selected: {self.selected_good} (Qty: {self.trade_quantity})", 
                True, BLACK
            )
            self.screen.blit(selected_text, (panel_rect.x + 10, trade_y + 20))
            
            # Cost/Revenue calculation
            total_cost = good.current_price * self.trade_quantity
            cost_text = self.small_font.render(f"Total: ${total_cost:.2f}", True, BLACK)
            self.screen.blit(cost_text, (panel_rect.x + 10, trade_y + 40))
    
    def draw_markets(self, markets):
        """Draw market locations on the map"""
        for market in markets:
            # Market building
            market_rect = pygame.Rect(
                market.position.x - 25, market.position.y - 25, 50, 50
            )
            pygame.draw.rect(self.screen, GRAY, market_rect)
            pygame.draw.rect(self.screen, BLACK, market_rect, 2)
            
            # Market name
            name_text = self.small_font.render(market.name, True, BLACK)
            text_rect = name_text.get_rect(center=(market.position.x, market.position.y + 35))
            self.screen.blit(name_text, text_rect)
    
    def draw_player(self, player):
        """Draw the Boston Terrier player"""
        # Body (main circle)
        pygame.draw.circle(
            self.screen, player.color, 
            (int(player.position.x), int(player.position.y)), 
            player.size // 2
        )
        
        # Head (smaller circle)
        head_x = int(player.position.x)
        head_y = int(player.position.y - player.size // 3)
        pygame.draw.circle(self.screen, player.color, (head_x, head_y), player.size // 3)
        
        # Eyes
        eye_size = 3
        left_eye = (head_x - 5, head_y - 3)
        right_eye = (head_x + 5, head_y - 3)
        pygame.draw.circle(self.screen, BLACK, left_eye, eye_size)
        pygame.draw.circle(self.screen, BLACK, right_eye, eye_size)
        
        # Ears (Boston Terrier style - upright)
        ear_points_left = [
            (head_x - 12, head_y - 8),
            (head_x - 15, head_y - 15),
            (head_x - 8, head_y - 12)
        ]
        ear_points_right = [
            (head_x + 12, head_y - 8),
            (head_x + 15, head_y - 15),
            (head_x + 8, head_y - 12)
        ]
        pygame.draw.polygon(self.screen, BLACK, ear_points_left)
        pygame.draw.polygon(self.screen, BLACK, ear_points_right)
        
        # Outline
        pygame.draw.circle(
            self.screen, BLACK, 
            (int(player.position.x), int(player.position.y)), 
            player.size // 2, 2
        )
        pygame.draw.circle(self.screen, BLACK, (head_x, head_y), player.size // 3, 2)
    
    def handle_event(self, event, player, markets):
        """Handle UI events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.show_inventory = not self.show_inventory
            
            elif event.key == pygame.K_r:
                # Find nearest market
                nearest_market = None
                min_distance = float('inf')
                
                for market in markets:
                    distance = player.position.distance_to(market.position)
                    if distance < 80 and distance < min_distance:  # Interaction range
                        min_distance = distance
                        nearest_market = market
                
                if nearest_market:
                    self.selected_market = nearest_market
                    self.show_market_info = True
                    self.trade_mode = True
            
            elif event.key == pygame.K_ESCAPE:
                self.show_inventory = False
                self.show_market_info = False
                self.trade_mode = False
                self.selected_market = None
                self.selected_good = None
            
            # Trading controls
            elif self.trade_mode and self.selected_market:
                # Select goods with number keys
                good_keys = {
                    pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, 
                    pygame.K_4: 3, pygame.K_5: 4
                }
                
                if event.key in good_keys:
                    good_index = good_keys[event.key]
                    if good_index < len(GOODS_TYPES):
                        self.selected_good = GOODS_TYPES[good_index]
                        self.trade_quantity = 1
                
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    if self.selected_good:
                        self.trade_quantity = min(10, self.trade_quantity + 1)
                
                elif event.key == pygame.K_MINUS:
                    if self.selected_good:
                        self.trade_quantity = max(1, self.trade_quantity - 1)
                
                elif event.key == pygame.K_b:  # Buy
                    if self.selected_good:
                        player.buy_good(self.selected_market, self.selected_good, self.trade_quantity)
                
                elif event.key == pygame.K_s:  # Sell
                    if self.selected_good:
                        player.sell_good(self.selected_market, self.selected_good, self.trade_quantity)
