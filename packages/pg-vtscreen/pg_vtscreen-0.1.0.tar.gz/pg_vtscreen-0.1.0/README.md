# pg_vtscreen

A virtual screen manager for Pygame that handles window scaling, aspect ratio maintenance, and fullscreen functionality.

## Features

- Create a virtual screen (game logic drawing area) independent of the display window
- Manage the actual display window with enhanced functionality
- Support fullscreen toggle (default F11 key)
- Maintain aspect ratio when resizing windows
- Handle basic window events (close, resize)

## Installation
pip install pg_vtscreen
## Usage Example
import pygame
from pg_vtscreen import VirtualScreenManager

# Initialize Pygame
pygame.init()

# Create virtual screen manager
vsm = VirtualScreenManager()

# Create virtual screen (game resolution)
virtual_screen = vsm.create_virtual_window(1280, 720)

# Create display window (user's window)
display_screen = vsm.create_display_window(
    size=(800, 600),
    flags=pygame.RESIZABLE,
    caption="pg_vtscreen Example"
)

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    # Handle events
    vsm.handle_events()
    
    # Draw on virtual screen
    virtual_screen.fill((0, 0, 0))  # Black background
    pygame.draw.circle(virtual_screen, (0, 255, 0), (640, 360), 50)  # Green circle in center
    
    # Project virtual screen to display
    vsm.project_to_screen(maintain_aspect_ratio=True)
    
    # Maintain 60 FPS
    clock.tick(60)
## Documentation

### VirtualScreenManager Class

#### Methods

- `__init__()`: Initialize the virtual screen manager
- `create_virtual_window(width, height)`: Create a virtual drawing surface
- `create_display_window(size=(), flags=0, ...)`: Create the actual display window
- `set_fullscreen_key(key)`: Set custom key for fullscreen toggle (default F11)
- `project_to_screen(maintain_aspect_ratio=True)`: Scale and draw virtual screen to display
- `handle_events()`: Handle basic window events (close, resize, fullscreen)

## License

This project is licensed under the BSD License - see the LICENSE file for details.
    