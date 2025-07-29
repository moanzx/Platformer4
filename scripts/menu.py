import pygame, sys, os, json
from scripts.utils import *

class MenuButton:
    def __init__(self, game, rect, text, action) -> None:
        self.game = game
        self.rect = rect
        self.text = text
        self.action = action
        self.state = "normal"  # normal, hover, clicked
        self.current_scale = 1.0
        self.hover_scale = 1.1
        self.click_scale = 0.95
        
        # Colors
        self.normal_color = (100, 100, 100)
        self.hover_color = (150, 150, 150)
        self.clicked_color = (200, 200, 200)
        self.text_color = (255, 255, 255)
        
    def update(self):
        # Update scale based on state
        if self.state == "hover":
            target_scale = self.hover_scale
        elif self.state == "clicked":
            target_scale = self.click_scale
        else:
            target_scale = 1.0
            
        self.current_scale += (target_scale - self.current_scale) * 0.15
    
    def render(self, font):
        # Apply scale transformation
        scaled_rect = self.rect.copy()
        scaled_rect.width = int(self.rect.width * self.current_scale)
        scaled_rect.height = int(self.rect.height * self.current_scale)
        scaled_rect.center = self.rect.center
        
        # Get color based on state
        if self.state == "hover":
            color = self.hover_color
        elif self.state == "clicked":
            color = self.clicked_color
        else:
            color = self.normal_color
        
        # Create semi-transparent surface for button background
        button_surface = pygame.Surface((scaled_rect.width, scaled_rect.height))
        button_surface.set_alpha(180)  # Semi-transparent (180/255 = ~70% opacity)
        button_surface.fill(color)
        
        # Draw button
        self.game.display.blit(button_surface, scaled_rect)
        pygame.draw.rect(self.game.display, (255, 255, 255), scaled_rect, 2)
        
        # Draw text
        text = font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=scaled_rect.center)
        self.game.display.blit(text, text_rect)

class Menu:
    def __init__(self, game) -> None:
        self.game = game
        self.current_menu = "main"  # main, level_select, naming_dialog
        self.buttons = []
        self.font = pygame.font.SysFont('Arial', 32)
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        
        self.menu_options = {
            "main": ["Play Game", "Level Editor", "Exit"]
        }
        
        self.selected_level = "level1"
        self.selected_mode = None  # Will be set when user chooses Play Game or Level Editor
        
        # Button dimensions
        self.button_width = 300
        self.button_height = 60
        self.button_margin = 20
        
        # Colors
        self.title_color = (255, 255, 0)
        self.background_color = (50, 50, 100)
        
        # Page system for levels
        self.levels_per_page = 5  # Show 5 levels per page
        self.current_page = 0
        self.available_levels = self.get_available_levels()
        
        # Level creation dialog
        self.dialog_text = ""
        self.max_name_length = 20
        self.clean_level_data = {
            "layer_list": [
                {
                    "collision": True, 
                    "visible": True, 
                    "off_grid": {}, 
                    "grid": {
                        "16;8": {
                            "world_element_type": "utils", 
                            "element": "player_spawner", 
                            "variance": 0, 
                            "pos": [16, 8]
                        },
                        "16;9": {
                            "world_element_type": "tiles", 
                            "element": "mossy_stone", 
                            "variance": 0, 
                            "pos": [16, 9]
                        }
                    }
                }
            ], 
            "background_list": [], 
            "borders": {"top": 0, "bottom": 16, "left": 0, "right": 32}
        }
        
        # Background scrolling
        self.background_scroll = 0
        self.background_speed = 0.5  # Pixels per frame
        self.background_image = None
        self.background_img_size = (0, 0)
        self.make_background_img()
        
        self.create_buttons()
        
    def make_background_img(self):
        """Create a tiled background image - 1 row, 3 columns"""
        try:
            # Load the ellinia background
            background_path = "assets/backgrounds/ellinia.jpeg"
            if os.path.exists(background_path):
                img = pygame.image.load(background_path).convert()
            else:
                self.background_image = None
                self.background_img_size = (0, 0)
                return
            
            img_size = img.get_size()
            new_img = pygame.Surface((img_size[0] * 3, img_size[1]))

            for i in range(3):
                new_img.blit(img, (i*img_size[0], 0))
            
            self.background_image = new_img
            self.background_img_size = img_size
            
        except Exception as e:
            print(f"Error loading background: {e}")
            self.background_image = None
            self.background_img_size = (0, 0)
    
    def update_background(self):
        """Update the background scroll position"""
        if self.background_image:
            self.background_scroll -= self.background_speed
            # Reset scroll when image has scrolled completely
            if self.background_scroll <= -self.background_img_size[0]:
                self.background_scroll = 0
    
    def render_background(self):
        """Render the scrolling background with seamless looping"""
        if self.background_image:
            # Scale image to fit screen height while maintaining aspect ratio
            scale_factor = self.game.height / self.background_img_size[1]
            scaled_width = int(self.background_img_size[0] * 3 * scale_factor)
            scaled_height = self.game.height
            
            # Scale the image
            scaled_image = pygame.transform.scale(self.background_image, (scaled_width, scaled_height))
            
            # Calculate positions for seamless scrolling
            x1 = int(self.background_scroll * scale_factor)
            x2 = x1 + scaled_width
            
            # Draw the background images to ensure no black screen
            self.game.display.blit(scaled_image, (x1, 0))
            self.game.display.blit(scaled_image, (x2, 0))
            
            # Add a semi-transparent overlay to make text more readable
            overlay = pygame.Surface((self.game.width, self.game.height))
            overlay.set_alpha(100)  # Semi-transparent
            overlay.fill((0, 0, 0))  # Black overlay
            self.game.display.blit(overlay, (0, 0))
    
    def get_available_levels(self):
        """Get all level files from the levels directory"""
        levels = []
        if os.path.exists("levels"):
            for file in os.listdir("levels"):
                # Include all files in the levels directory
                levels.append(file)
        return sorted(levels)  # Sort alphabetically
    
    def get_current_page_levels(self):
        """Get levels for current page"""
        start_index = self.current_page * self.levels_per_page
        end_index = start_index + self.levels_per_page
        return self.available_levels[start_index:end_index]
    
    def get_total_pages(self):
        """Calculate total number of pages"""
        return (len(self.available_levels) + self.levels_per_page - 1) // self.levels_per_page
    
    def create_level(self, level_name):
        """Create a new level file with the given name"""
        # Check for duplicates
        if level_name in self.available_levels:
            return False, "Level name already exists!"
        
        # Validate name length
        if len(level_name) > self.max_name_length:
            return False, f"Name too long! Max {self.max_name_length} characters."
        
        # Validate name characters (no special characters that could cause file issues)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
        for char in invalid_chars:
            if char in level_name:
                return False, f"Invalid character: {char}"
        
        try:
            # Create the level file
            level_path = os.path.join("levels", level_name)
            with open(level_path, 'w') as f:
                json.dump(self.clean_level_data, f)
            
            # Refresh the level list
            self.available_levels = self.get_available_levels()
            
            return True, f"Level '{level_name}' created successfully!"
        except Exception as e:
            return False, f"Error creating level: {str(e)}"
        

    
    def create_buttons(self):
        """Create buttons for current menu"""
        self.buttons = []
        
        if self.current_menu == "main":
            options = self.menu_options["main"]
            start_y = 250
            for i, option in enumerate(options):
                button_rect = pygame.Rect(
                    (self.game.width - self.button_width) // 2,
                    start_y + i * (self.button_height + self.button_margin),
                    self.button_width,
                    self.button_height
                )
                self.buttons.append(MenuButton(self.game, button_rect, option, self.get_action(option)))
                
        elif self.current_menu == "level_select":
            page_levels = self.get_current_page_levels()
            start_y = 120  # Adjusted for better spacing
            
            for i, level in enumerate(page_levels):
                button_rect = pygame.Rect(
                    (self.game.width - self.button_width) // 2,
                    start_y + i * (self.button_height + self.button_margin),
                    self.button_width,
                    self.button_height
                )
                self.buttons.append(MenuButton(self.game, button_rect, level, self.get_action(level)))
            
            nav_start_y = start_y + len(page_levels) * (self.button_height + self.button_margin) + 20
            
            # Previous/Next buttons
            if self.current_page > 0:
                prev_rect = pygame.Rect(
                    (self.game.width - self.button_width) // 2 - 140 - 20,
                    start_y,
                    140,
                    self.button_height
                )
                self.buttons.append(MenuButton(self.game, prev_rect, "<", "prev_page"))
            
            if self.current_page < self.get_total_pages() - 1:
                next_rect = pygame.Rect(
                    (self.game.width - self.button_width) // 2 + self.button_width + 20,
                    start_y,
                    140,
                    self.button_height
                )
                self.buttons.append(MenuButton(self.game, next_rect, ">", "next_page"))
            
            # Back button
            back_rect = pygame.Rect(
                (self.game.width - self.button_width) // 2,
                nav_start_y,
                self.button_width,
                self.button_height
            )
            self.buttons.append(MenuButton(self.game, back_rect, "Back", "main"))
            
            # Add level button (only in editor mode)
            if self.selected_mode == "editor":
                add_rect = pygame.Rect(
                    (self.game.width - self.button_width) // 2 + self.button_width + 20,
                    nav_start_y,
                    140,
                    self.button_height
                )
                self.buttons.append(MenuButton(self.game, add_rect, "+", "add_level"))
                
        elif self.current_menu == "naming_dialog":
            # Input box (not a button, but rendered in render method)
            # Back button
            back_rect = pygame.Rect(
                (self.game.width - self.button_width) // 2,
                self.game.height - 120,
                self.button_width,
                self.button_height
            )
            self.buttons.append(MenuButton(self.game, back_rect, "Back", "Back"))
    
    def get_action(self, option):
        """Get the action for a menu option"""
        if self.current_menu == "main":
            if option == "Play Game":
                return "level_select"
            elif option == "Level Editor":
                return "level_select"
            elif option == "Exit":
                return "exit"
        elif self.current_menu == "level_select":
            if option in self.available_levels:
                return (self.selected_mode, option)
            elif option == "prev_page":
                self.current_page = max(0, self.current_page - 1)
                self.create_buttons()
                return None
            elif option == "next_page":
                self.current_page = min(self.get_total_pages() - 1, self.current_page + 1)
                self.create_buttons()
                return None
            elif option == "add_level":
                # Show naming dialog and create level
                new_level_name = self.show_naming_dialog()
                if new_level_name:
                    # Refresh the level list and buttons
                    self.available_levels = self.get_available_levels()
                    self.create_buttons()
                    # Navigate to the new level in editor
                    return ("editor", new_level_name)
                return None
            elif option == "Back":
                self.current_page = 0  # Reset to first page
                return "main"
        elif self.current_menu == "naming_dialog":
            if option == "Back":
                self.current_menu = "level_select"
                self.create_buttons()
                return None
            return None
        return None
    
    def handle_events(self):
        """Handle all events for the current menu state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_menu == "main":
                        return "exit"
                    elif self.current_menu == "naming_dialog":
                        self.current_menu = "level_select"
                        self.create_buttons()
                        return None
                    else:
                        self.current_menu = "main"
                        self.current_page = 0
                        self.selected_mode = None
                        self.create_buttons()
                        return None
                
                # Handle naming dialog input
                if self.current_menu == "naming_dialog":
                    if event.key == pygame.K_RETURN:
                        if self.dialog_text.strip():
                            success, message = self.create_level(self.dialog_text.strip())
                            if success:
                                # Navigate to the new level in editor
                                return ("editor", self.dialog_text.strip())
                            else:
                                print(message)  # For now, just print to console
                    elif event.key == pygame.K_BACKSPACE:
                        self.dialog_text = self.dialog_text[:-1]
                    else:
                        # Add character if within limit
                        if len(self.dialog_text) < self.max_name_length:
                            self.dialog_text += event.unicode
                    return None
                
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for button in self.buttons:
                        if button.rect.collidepoint(mouse_pos) and button.state == "clicked":
                            action = button.action
                            
                            if action == "exit":
                                return "exit"
                            elif isinstance(action, tuple):
                                return action
                            elif action in ["main", "level_select"]:
                                self.current_menu = action
                                if action == "main":
                                    self.current_page = 0
                                    self.selected_mode = None
                                elif action == "level_select":
                                    # Set selected_mode based on which button was clicked
                                    for btn in self.buttons:
                                        if btn.rect.collidepoint(mouse_pos):
                                            if btn.text == "Play Game":
                                                self.selected_mode = "game"
                                            elif btn.text == "Level Editor":
                                                self.selected_mode = "editor"
                                            break
                                self.create_buttons()
                                return None
                            elif action in ["prev_page", "next_page"]:
                                if action == "prev_page":
                                    self.current_page = max(0, self.current_page - 1)
                                    self.create_buttons()
                                elif action == "next_page":
                                    self.current_page = min(self.get_total_pages() - 1, self.current_page + 1)
                                    self.create_buttons()
                                return None
                            elif action == "add_level":
                                # Switch to naming dialog state
                                self.current_menu = "naming_dialog"
                                self.dialog_text = ""
                                self.create_buttons()
                                return None
                            elif action == "Back":
                                if self.current_menu == "naming_dialog":
                                    self.current_menu = "level_select"
                                    self.create_buttons()
                                    return None
                                else:
                                    self.current_menu = "main"
                                    self.current_page = 0
                                    self.selected_mode = None
                                    self.create_buttons()
                                    return None
                            return None
        
        # Handle mouse interactions for hover and click states
        for button in self.buttons:
            if button.rect.collidepoint(mouse_pos):
                if button.state != "hover" and button.state != "clicked":
                    button.state = "hover"
                if mouse_pressed and button.state == "hover":
                    button.state = "clicked"
            else:
                button.state = "normal"
        
        return None
    
    def update(self):
        for button in self.buttons:
            button.update()
    
    def render(self):
        """Render the current menu"""
        # Render scrolling background
        self.render_background()
        
        # Title
        title_text = self.title_font.render("Platformer Game", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.game.width // 2, 60))
        self.game.display.blit(title_text, title_rect)
        
        # Render buttons
        for button in self.buttons:
            button.render(self.font)
        
        # Render naming dialog input if in naming_dialog state
        if self.current_menu == "naming_dialog":
            self.render_naming_input()
        
        # Instructions
        if self.current_menu == "main":
            instruction_text = self.font.render("Use mouse to navigate, ESC to go back", True, (200, 200, 200))
        elif self.current_menu == "level_select":
            instruction_text = self.font.render("Click a level to start, use Previous/Next to navigate pages", True, (200, 200, 200))
        elif self.current_menu == "naming_dialog":
            instruction_text = self.font.render("Enter level name, ESC to cancel", True, (200, 200, 200))
        else:
            instruction_text = self.font.render("", True, (200, 200, 200)) # No specific instructions for other menus
        instruction_rect = instruction_text.get_rect(center=(self.game.width // 2, self.game.height - 40))
        self.game.display.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
    
    def render_naming_input(self):
        """Render the naming input box for the naming_dialog state"""
        # Title for naming dialog
        title_text = self.title_font.render("Enter Level Name", True, (250, 250, 250))
        title_rect = title_text.get_rect(center=(self.game.width // 2, 200))
        self.game.display.blit(title_text, title_rect)
        
        # Input box
        input_rect = pygame.Rect(
            (self.game.width - self.button_width) // 2,
            300,
            self.button_width,
            self.button_height
        )
        
        # Create semi-transparent surface for input box background
        input_surface = pygame.Surface((input_rect.width, input_rect.height))
        input_surface.set_alpha(180)  # Semi-transparent (180/255 = ~70% opacity)
        input_surface.fill((100, 100, 100))  # Same as MenuButton.normal_color
        
        # Draw input box
        self.game.display.blit(input_surface, input_rect)
        pygame.draw.rect(self.game.display, (255, 255, 255), input_rect, 2)
        
        # Input text with cursor
        input_text = self.font.render(self.dialog_text + "|", True, (255, 255, 255))
        input_text_rect = input_text.get_rect(midleft=(input_rect.x + 15, input_rect.centery))
        self.game.display.blit(input_text, input_text_rect)
        
        # Instructions
        instruction_text = self.font.render(f"Max {self.max_name_length} characters", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(self.game.width // 2, 380))
        self.game.display.blit(instruction_text, instruction_rect)
        
        instruction_text2 = self.font.render("Press ENTER to create", True, (200, 200, 200))
        instruction_rect2 = instruction_text2.get_rect(center=(self.game.width // 2, 410))
        self.game.display.blit(instruction_text2, instruction_rect2)
    
    def run(self):
        while True:
            self.game.clock.tick(60)
            
            # Update background
            self.update_background()
            
            # Handle events
            result = self.handle_events()
            if result:
                return result
            
            # Update
            self.update()
            
            # Render
            self.render() 