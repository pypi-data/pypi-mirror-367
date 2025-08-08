"""
Game entities: Player, Truck, Markets, Goods
"""

import pygame
import math
import random
from .constants import *

class Position:
    """Simple 2D position class"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

class Good:
    """Represents a type of good that can be traded"""
    def __init__(self, name, base_price=10):
        self.name = name
        self.base_price = base_price
        self.current_price = base_price
        self.demand = random.uniform(0.5, 1.5)  # Demand multiplier
    
    def update_price(self, dt):
        """Update price based on market conditions"""
        # Simple price fluctuation based on demand
        price_change = (self.demand - 1.0) * PRICE_FLUCTUATION_RATE * dt
        self.current_price += price_change
        self.current_price = max(1, self.current_price)  # Minimum price of 1
        
        # Randomly adjust demand
        if random.random() < DEMAND_CHANGE_RATE * dt:
            self.demand += random.uniform(-0.1, 0.1)
            self.demand = max(0.1, min(2.0, self.demand))

class Market:
    """Represents a market where goods can be bought and sold"""
    def __init__(self, name, position, market_type="general"):
        self.name = name
        self.position = position
        self.market_type = market_type
        self.goods = {}
        self.money = random.randint(500, 2000)
        
        # Initialize goods with random quantities
        for good_type in GOODS_TYPES:
            self.goods[good_type] = Good(good_type, random.randint(5, 25))
            self.goods[good_type].quantity = random.randint(0, 20)
    
    def update(self, dt):
        """Update market conditions"""
        for good in self.goods.values():
            good.update_price(dt)
            
            # Randomly generate or consume goods
            if random.random() < 0.1 * dt:  # 10% chance per second
                if random.random() < 0.6:  # 60% chance to add goods
                    good.quantity += random.randint(1, 3)
                else:  # 40% chance to consume goods
                    good.quantity = max(0, good.quantity - random.randint(1, 2))
    
    def can_buy(self, good_type, quantity):
        """Check if market can sell goods to player"""
        return (good_type in self.goods and 
                self.goods[good_type].quantity >= quantity)
    
    def can_sell(self, good_type, quantity, total_cost):
        """Check if market can buy goods from player"""
        return (good_type in self.goods and 
                self.money >= total_cost)
    
    def buy_from_market(self, good_type, quantity):
        """Player buys goods from market"""
        if self.can_buy(good_type, quantity):
            cost = self.goods[good_type].current_price * quantity
            self.goods[good_type].quantity -= quantity
            self.money += cost
            return cost
        return 0
    
    def sell_to_market(self, good_type, quantity):
        """Player sells goods to market"""
        if good_type in self.goods:
            revenue = self.goods[good_type].current_price * quantity
            if self.money >= revenue:
                self.goods[good_type].quantity += quantity
                self.money -= revenue
                return revenue
        return 0

class Player:
    """The Boston Terrier player character"""
    def __init__(self, start_x, start_y):
        self.position = Position(start_x, start_y)
        self.money = 100
        self.inventory = {good_type: 0 for good_type in GOODS_TYPES}
        self.truck = None
        self.selected_market = None
        
        # Visual properties
        self.size = 30
        self.color = BROWN
        self.image = None
        self.load_image()
    
    def load_image(self):
        """Load Tucker's image if available"""
        import os
        try:
            # Try to load Tucker's image
            base_path = os.path.dirname(__file__)
            
            # First try the custom tucker.png
            image_path = os.path.join(base_path, 'assets', 'tucker.png')
            if not os.path.exists(image_path):
                # Fall back to placeholder
                image_path = os.path.join(base_path, 'assets', 'tucker_placeholder.png')
            
            if os.path.exists(image_path):
                import pygame
                self.image = pygame.image.load(image_path)
                # Scale the image to fit our size
                self.image = pygame.transform.scale(self.image, (self.size * 2, self.size * 2))
                print(f"✅ Loaded Tucker image: {os.path.basename(image_path)}")
        except Exception as e:
            # If image loading fails, we'll use the fallback drawing
            print(f"⚠️ Could not load Tucker image: {e}")
            self.image = None
    
    def get_total_cargo(self):
        """Get total items in inventory"""
        return sum(self.inventory.values())
    
    def can_carry_more(self, quantity=1):
        """Check if player can carry more items"""
        return self.get_total_cargo() + quantity <= MAX_CARGO_CAPACITY
    
    def move(self, dx, dy, dt):
        """Move the player"""
        self.position.x += dx * PLAYER_SPEED * dt
        self.position.y += dy * PLAYER_SPEED * dt
        
        # Keep player on screen
        self.position.x = max(self.size, min(SCREEN_WIDTH - self.size, self.position.x))
        self.position.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.position.y))
    
    def buy_good(self, market, good_type, quantity):
        """Buy goods from a market"""
        if not market.can_buy(good_type, quantity):
            return False
        
        if not self.can_carry_more(quantity):
            return False
        
        cost = market.goods[good_type].current_price * quantity
        if self.money >= cost:
            actual_cost = market.buy_from_market(good_type, quantity)
            self.money -= actual_cost
            self.inventory[good_type] += quantity
            return True
        return False
    
    def sell_good(self, market, good_type, quantity):
        """Sell goods to a market"""
        if self.inventory[good_type] < quantity:
            return False
        
        revenue = market.sell_to_market(good_type, quantity)
        if revenue > 0:
            self.money += revenue
            self.inventory[good_type] -= quantity
            return True
        return False

class Truck:
    """Truck for faster transportation (future feature)"""
    def __init__(self, position):
        self.position = position
        self.capacity = 20
        self.speed = TRUCK_SPEED
        self.owned = False
        self.cost = 500
