#!/usr/bin/env python3
"""
Script to create Tucker's sprite image for the game.
This script shows you how to prepare and place Tucker's image.
"""

import os

def setup_tucker_image():
    """Instructions for setting up Tucker's image"""
    print("🐕 Tucker Trucker - Image Setup Guide")
    print("=" * 40)
    print()
    print("To use the custom Tucker image you provided:")
    print()
    print("1. Save your Tucker image as 'tucker.png'")
    print("2. Place it in: tucker_trucker/assets/tucker.png")
    print("3. The game will automatically detect and use it!")
    print()
    
    assets_dir = os.path.join(os.path.dirname(__file__), 'tucker_trucker', 'assets')
    image_path = os.path.join(assets_dir, 'tucker.png')
    
    print(f"📁 Expected location: {image_path}")
    print()
    
    if os.path.exists(image_path):
        print("✅ Tucker image found! The game will use your custom sprite.")
        
        # Test if we can load it with pygame
        try:
            import pygame
            pygame.init()
            image = pygame.image.load(image_path)
            print(f"✅ Image loaded successfully!")
            print(f"   Size: {image.get_width()}x{image.get_height()} pixels")
            print(f"   Will be scaled to 60x60 pixels in-game")
        except Exception as e:
            print(f"⚠️  Image found but couldn't load: {e}")
            print("   Make sure it's a valid PNG file")
    else:
        print("📋 To add Tucker's image:")
        print("   1. Right-click the Tucker image you have")
        print("   2. Save it as 'tucker.png'")
        print(f"   3. Copy it to: {assets_dir}")
        print("   4. Run the game - Tucker will appear with your image!")
        print()
        print("🎮 The game will work without the image too (using the drawn sprite)")
    
    print()
    print("🚀 Game features with custom Tucker:")
    print("   - Higher quality character sprite")
    print("   - Better visual appeal")
    print("   - Professional game appearance")
    print("   - Maintains all gameplay functionality")

if __name__ == "__main__":
    setup_tucker_image()
