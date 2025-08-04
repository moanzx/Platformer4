# 🎮 Platformer4 - Complete 2D Game Engine

![Demo](gifs/Game3.gif)

A complete 2D platformer engine built in Python using Pygame. It includes a visual level editor, modular architecture, responsive physics, AI, and rendering systems. This project demonstrates solid software design and integration of multiple systems into a single cohesive game.

---

## 🔬 Gameplay Systems

* Smooth player movement with gravity and velocity-based physics
* Separate X/Y collision handling for glitch-free responsiveness
* Enemy AI with edge detection, ranged attacks
* Projectile mechanics with trajectory calculation and impact detection
* Game state logic including victory/defeat, restart, and health systems

![Demo](gifs/Game1.gif)

---

## 🧱️ Level Editor & Engine Architecture

* Visual level editor with grid snapping, layer switching, and categorized hotbar
* Multi-layer tilemap engine with collision toggles
* Automatic tile variance calculation for seamless tile connections
* JSON-based save/load system for levels and configurations
* Component-based architecture with factory patterns for entity instantiation
* Dynamic asset discovery

![Demo](gifs/Editor1.gif)

---

## 🖼️ Visual & Rendering Systems

* Sprite animation system with per-entity states (idle, run, jump, etc.)
* Smooth camera scrolling with easing and parallax background layers
* Particle systems with blending, physics, and mathematical distribution
* Multi-layer rendering with correct depth ordering
* Surface caching for efficient tile rendering

![Demo](gifs/Camera1.gif)

---

## 🧠 Technical Highlights

* Dynamic Entity-Component design for modularity and reusability
* Grid-based spatial indexing for fast lookups and optimized collision
* State machines drive animations, game logic, and UI behavior
* JSON used across levels, assets, and animation configurations
* Organized structure across core systems: editor, gameplay, rendering, UI

---

## 🚀 Getting Started
**To run the game:**
```
python game.py
```


**Controls:**

* **Menu:**

  * **Mouse**: Navigate menus
* **Game:**

  * **WASD and arrow keys**: Move player
  * **ESC/R**: Restart level (when dead)
* **Editor:**

  * **Mouse**: Place/remove tiles in editor with left and right click
  * **Middle Click + Drag**: Pan editor view
  * **Mouse Wheel**: Switch editor layers
  * **B:** Activate camera border selection
  * **Escape**: Return to menu

---
