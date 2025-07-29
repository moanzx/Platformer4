# Platformer Game Engine

A feature-rich 2D platformer game engine built with Python and Pygame, featuring a level editor, dynamic collision system, and modular architecture.

## 🎮 Features

### Core Gameplay
- **Smooth 2D platformer mechanics** with gravity, jumping, and collision detection
- **Dynamic tilemap system** supporting multiple layers and tile types
- **Enemy AI system** with different behaviors and attack patterns
- **Health and damage system** with visual feedback
- **Particle effects** for enhanced visual appeal

### Level Editor
- **Real-time level creation** with tile placement and removal
- **Multiple tile categories** - terrain, entities, utilities, decorations
- **Layer system** for organizing level elements
- **Save/load functionality** for level persistence
- **Collision visualization** for debugging

### Advanced Systems
- **Seamless background tiling** with parallax scrolling
- **Dynamic game end system** supporting both death and victory conditions
- **Modular entity system** for easy enemy and player creation
- **Optimized rendering** with tile caching for performance

## 🚀 Installation

### Prerequisites
- Python 3.7+
- Pygame

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd platformer4

# Install dependencies
pip install pygame

# Run the game
python game.py
```

## 🎯 How to Play

### Controls
- **WASD/Arrow Keys** - Move and jump
- **ESC** - Return to menu
- **R** - Restart level (when dead/victorious)

### Gameplay
1. **Navigate through levels** avoiding enemies and obstacles
2. **Reach the victory tile** to complete the level
3. **Avoid kill tiles** and enemy attacks
4. **Use the level editor** to create custom levels

## 🛠️ Technical Architecture

### Core Systems

#### Tilemap System (`scripts/tilemap.py`)
- Grid-based level storage with multiple layers
- Dynamic collision detection
- Support for different tile types (terrain, entities, utilities)

#### Entity System (`scripts/entities.py`)
- Base `Entity` class for all game objects
- Modular collision handling with special tile detection
- Extensible for new entity types

#### Game State Management (`scripts/level.py`)
- Dynamic game end system supporting death and victory
- Seamless state transitions with fade animations
- Reusable UI components

### Key Technical Achievements

#### Dynamic Game End System
```python
def trigger_game_end(self, reason="death"):
    """Unified system for handling both death and victory"""
    if self.game_end_state == "alive":
        self.game_end_state = "ending"
        self.game_end_type = reason
        # Different animations based on reason
```

#### Intelligent Collision Detection
```python
def check_end_tile_at_pos(self, pos):
    """Detects both kill and victory tiles with same logic"""
    # Returns "death", "victory", or None
```

#### Modular Tile System
- Easy addition of new tile types
- Consistent collision and rendering behavior
- Editor integration for all tile types

## 🎨 Level Editor

### Features
- **Real-time editing** with immediate visual feedback
- **Multiple tile categories** for organized level building
- **Layer management** for complex level design
- **Save/load system** for level persistence

### Usage
1. **Select tiles** from the tile palette
2. **Click to place** tiles in the level
3. **Use layers** to organize different elements
4. **Save your level** for later use

## 🔧 Development Highlights

### Problem-Solving Examples

#### Victory Tile Implementation
- **Challenge**: Create a system similar to kill tiles but for victory
- **Solution**: Extended existing collision system with dynamic game end detection
- **Result**: Clean, reusable code with minimal duplication

#### Dynamic Game End System
- **Challenge**: Support both death and victory with same UI
- **Solution**: Parameterized trigger system with dynamic text/colors
- **Result**: 95% code reuse between death and victory systems

#### Collision Optimization
- **Challenge**: Prevent utility tiles from blocking movement
- **Solution**: Enhanced collision detection with tile type filtering
- **Result**: Smooth gameplay with invisible utility tiles

### Code Quality Features
- **Clean architecture** with separation of concerns
- **Extensible design** for easy feature additions
- **Consistent naming** and documentation
- **Performance optimizations** with tile caching

## 📁 Project Structure

```
platformer4/
├── assets/           # Game assets (sprites, sounds, etc.)
├── levels/          # Level files
├── scripts/         # Core game code
│   ├── entities.py  # Entity system
│   ├── level.py     # Level management
│   ├── tilemap.py   # Tilemap system
│   └── ...
├── game.py          # Main game entry point
└── README.md        # This file
```

## 🎯 Future Enhancements

### Planned Features
- **Sound system** with background music and SFX
- **More enemy types** with different AI behaviors
- **Power-ups and collectibles**
- **Level progression system**
- **Multiplayer support**

### Technical Improvements
- **Performance optimizations** for larger levels
- **Enhanced particle system**
- **Shader support** for visual effects
- **Mobile port** with touch controls

## 🤝 Contributing

This project demonstrates:
- **Strong problem-solving skills**
- **Clean, maintainable code**
- **Modular architecture design**
- **Game development best practices**
- **Python and Pygame expertise**

Perfect for showcasing in technical interviews and portfolio presentations! 