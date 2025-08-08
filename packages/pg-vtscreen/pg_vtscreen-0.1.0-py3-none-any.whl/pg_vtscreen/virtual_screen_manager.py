import pygame
import sys


class VirtualScreenManager:
    def __init__(self):
        """Initialize the virtual screen manager"""
        # Virtual screen related
        self.virtual_screen = None
        self.virtual_width = 0
        self.virtual_height = 0

        # Display window related
        self.screen = None
        self.original_window_size = (800, 600)

        # Fullscreen key
        self.fullscreen_key = pygame.K_F11
        self.is_fullscreen = False

    def create_virtual_window(self, width, height):
        """
        Create a virtual window (game logic drawing area)

        Parameters:
            width: Virtual window width in pixels
            height: Virtual window height in pixels

        Returns:
            pygame.Surface: Virtual screen surface object
        """
        self.virtual_width = width
        self.virtual_height = height
        self.virtual_screen = pygame.Surface((width, height))
        return self.virtual_screen

    def create_display_window(self, size=(), flags=0, depth=0, display=0, vsync=0, caption="Virtual Screen Window"):
        """
        Create an actual display window (enhanced pygame.display.set_mode)

        Parameters:
            size: Window size tuple (width, height)
            flags: Window flags (e.g., pygame.RESIZABLE)
            depth: Color depth
            display: Display device index
            vsync: Vertical synchronization
            caption: Window title

        Returns:
            pygame.Surface: Display window surface object
        """
        if not (flags & pygame.FULLSCREEN) and size:
            self.original_window_size = size

        self.screen = pygame.display.set_mode(
            size=size,
            flags=flags,
            depth=depth,
            display=display,
            vsync=vsync
        )

        pygame.display.set_caption(caption)
        self.is_fullscreen = (flags & pygame.FULLSCREEN) != 0

        return self.screen

    def set_fullscreen_key(self, key):
        """Set the fullscreen toggle key"""
        self.fullscreen_key = key

    def project_to_screen(self, maintain_aspect_ratio=True):
        """Project virtual window content to actual display window"""
        if not self.virtual_screen or not self.screen:
            raise ValueError("Please create virtual window and display window first")

        current_width, current_height = self.screen.get_size()

        if maintain_aspect_ratio:
            t_scale_x = current_width / self.virtual_width
            t_scale_y = current_height / self.virtual_height
            scale = min(t_scale_x, t_scale_y)
            scaled_w = int(self.virtual_width * scale)
            scaled_h = int(self.virtual_height * scale)
            x = (current_width - scaled_w) // 2
            y = (current_height - scaled_h) // 2
        else:
            scaled_w = current_width
            scaled_h = current_height
            x, y = 0, 0

        scaled_surface = pygame.transform.scale(self.virtual_screen, (scaled_w, scaled_h))
        self.screen.blit(scaled_surface, (x, y))
        pygame.display.flip()

    def handle_events(self):
        """
        Basic event handling (put in user's main loop)
        Only handles window closing and fullscreen toggling, returns no state
        """
        for event in pygame.event.get():
            # Window close event (exit program directly)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Window size change event
            elif event.type == 1032:  # WINDOWEVENT_SIZE_CHANGED
                if not self.is_fullscreen:
                    self.original_window_size = (event.w, event.h)

            # Fullscreen toggle key
            elif event.type == pygame.KEYDOWN:
                if event.key == self.fullscreen_key:
                    self.is_fullscreen = not self.is_fullscreen
                    current_flags = pygame.display.get_window_flags()

                    if self.is_fullscreen:
                        self.original_window_size = self.screen.get_size()
                        new_flags = current_flags | pygame.FULLSCREEN
                        info = pygame.display.Info()
                        self.screen = pygame.display.set_mode(
                            (info.current_w, info.current_h),
                            new_flags
                        )
                    else:
                        new_flags = current_flags & ~pygame.FULLSCREEN
                        self.screen = pygame.display.set_mode(
                            self.original_window_size,
                            new_flags
                        )
