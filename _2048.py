import random
import time
import uuid
import math  # For settings button
from typing import List, Tuple, Optional, Dict

# Constants

TILE_SIZE = 100
PADDING = 10
SCORE_HEIGHT = 50  # Space for score display
BOARD_SIZE = 4 # Default board size for 2048 game
GRID_AREA = BOARD_SIZE * (TILE_SIZE + PADDING) + PADDING
WINDOW_SIZE = (GRID_AREA, GRID_AREA + SCORE_HEIGHT)
BACKGROUND_COLOR = (187, 173, 160)
EMPTY_COLOR = (205, 193, 180)
TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (255, 60, 60), # New color for 4096
    8192: (255, 0, 0)    # New color for 8192
}

# Add language constants
LANGUAGES = {
    "EN": "English",
    "ZH": "中文"
}

class Game2048:
    def __init__(self, board_size: int = 4, target_tile_value: int = 2048):
        self.board_size = board_size
        self.target_tile_value = target_tile_value
        self.grid = [[{'value': 0, 'id': None} for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.score = 0
        self.animations: List[Dict] = []
        self.new_tiles = []  # Track newly created tiles
        self.add_random_tile()
        self.add_random_tile()
        self.won = False
        
    def add_random_tile(self):
        empty_cells = [(i, j) for i in range(self.board_size) for j in range(self.board_size) if self.grid[i][j]['value'] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            new_tile = {
                'value': 2 if random.random() < 0.9 else 4,
                'id': str(uuid.uuid4())
            }
            self.grid[i][j] = new_tile
            # Add to new tiles list with creation time
            self.new_tiles.append({
                'tile': new_tile,
                'position': (i, j),
                'start_time': time.time()
            })
            
    def get_state(self) -> dict:
        """Return complete game state for API"""
        return {
            'grid': self.grid,
            'score': self.score,
            'animations': self.animations,
            'game_over': self.is_game_over(),
            'won': self.won,
            'new_tiles': self.new_tiles # 添加新瓷砖列表
        }
        
    def move(self, direction: str) -> bool:
        old_grid = [[cell.copy() for cell in row] for row in self.grid]
        moved = False
        
        if direction == 'left':
            moved = self._move_left()
        elif direction == 'right':
            moved = self._move_right()
        elif direction == 'up':
            moved = self._move_up()
        elif direction == 'down':
            moved = self._move_down()
            
        if moved:
            self.new_tiles = [] # 清空之前的new_tiles
            self.add_random_tile()
            self._create_animations(old_grid)
            # Check for win condition after each move
            for r in range(self.board_size):
                for c in range(self.board_size):
                    if self.grid[r][c]['value'] == self.target_tile_value:
                        self.won = True
                        break
                if self.won:
                    break
            
        return moved
    
    def _move_left(self) -> bool:
        moved = False
        for i in range(self.board_size):
            # Remove zeros
            row = [cell for cell in self.grid[i] if cell['value'] != 0]
            # Merge tiles
            for j in range(len(row)-1):
                if row[j]['value'] == row[j+1]['value']:
                    row[j]['value'] *= 2
                    row[j+1]['value'] = 0
                    self.score += row[j]['value']
                    moved = True
            # Remove zeros again
            row = [cell for cell in row if cell['value'] != 0]
            # Pad with zeros
            row += [{'value': 0, 'id': None} for _ in range(self.board_size - len(row))]
            if row != self.grid[i]:
                moved = True
            self.grid[i] = row
        return moved
    
    def _move_right(self) -> bool:
        moved = False
        for i in range(self.board_size):
            # Remove zeros
            row = [cell for cell in self.grid[i] if cell['value'] != 0]
            # Merge tiles from right to left
            for j in range(len(row)-1, 0, -1):
                if row[j]['value'] == row[j-1]['value']:
                    row[j]['value'] *= 2
                    row[j-1]['value'] = 0
                    self.score += row[j]['value']
                    moved = True
            # Remove zeros again
            row = [cell for cell in row if cell['value'] != 0]
            # Pad with zeros at beginning
            row = [{'value': 0, 'id': None} for _ in range(self.board_size - len(row))] + row
            if row != self.grid[i]:
                moved = True
            self.grid[i] = row
        return moved
        
    def _move_up(self) -> bool:
        moved = False
        for j in range(self.board_size):
            # Remove zeros
            column = [self.grid[i][j] for i in range(self.board_size) if self.grid[i][j]['value'] != 0]
            # Merge tiles
            for i in range(len(column)-1):
                if column[i]['value'] == column[i+1]['value']:
                    column[i]['value'] *= 2
                    column[i+1]['value'] = 0
                    self.score += column[i]['value']
                    moved = True
            # Remove zeros again
            column = [cell for cell in column if cell['value'] != 0]
            # Pad with zeros at bottom
            column += [{'value': 0, 'id': None} for _ in range(self.board_size - len(column))]
            # Update column
            for i in range(self.board_size):
                if self.grid[i][j]['value'] != column[i]['value']:
                    moved = True
                self.grid[i][j] = column[i]
        return moved
        
    def _move_down(self) -> bool:
        moved = False
        for j in range(self.board_size):
            # Remove zeros
            column = [self.grid[i][j] for i in range(self.board_size) if self.grid[i][j]['value'] != 0]
            # Merge tiles from bottom to top
            for i in range(len(column)-1, 0, -1):
                if column[i]['value'] == column[i-1]['value']:
                    column[i]['value'] *= 2
                    column[i-1]['value'] = 0
                    self.score += column[i]['value']
                    moved = True
            # Remove zeros again
            column = [cell for cell in column if cell['value'] != 0]
            # Pad with zeros at top
            column = [{'value': 0, 'id': None} for _ in range(self.board_size - len(column))] + column
            # Update column
            for i in range(self.board_size):
                if self.grid[i][j]['value'] != column[i]['value']:
                    moved = True
                self.grid[i][j] = column[i]
        return moved

    def _create_animations(self, old_grid: List[List[Dict]]):
        """Create animations by comparing old and new grid states using tile IDs"""
        self.animations = []
        
        # Track which new positions have been claimed
        claimed_positions = set()
        
        # First pass: Create animations for simple moves using ID tracking
        for i in range(self.board_size):
            for j in range(self.board_size):
                old_tile = old_grid[i][j]
                if old_tile['value'] != 0:
                    # Find where this specific tile moved to by ID
                    for new_i in range(self.board_size):
                        for new_j in range(self.board_size):
                            new_tile = self.grid[new_i][new_j]
                            if new_tile['id'] == old_tile['id'] and \
                               ((i != new_i) or (j != new_j)) and \
                               (new_i, new_j) not in claimed_positions:
                                # Create animation
                                self.animations.append({
                                    'id': old_tile['id'],
                                    'value': old_tile['value'],
                                    'start_pos': (i, j),
                                    'end_pos': (new_i, new_j),
                                    'start_time': time.time(),
                                    'is_merge': False
                                })
                                claimed_positions.add((new_i, new_j))
                                break
                        else:
                            continue
                        break
        
        # Second pass: Create animations for merged tiles
        for i in range(self.board_size):
            for j in range(self.board_size):
                old_tile = old_grid[i][j]
                if old_tile['value'] != 0 and \
                   not any(a['id'] == old_tile['id'] for a in self.animations):
                    # This tile wasn't animated, likely merged
                    for new_i in range(self.board_size):
                        for new_j in range(self.board_size):
                            new_tile = self.grid[new_i][new_j]
                            if new_tile['value'] == 2 * old_tile['value'] and \
                               (new_i, new_j) not in claimed_positions:
                                # Create merge animation
                                self.animations.append({
                                    'id': old_tile['id'],
                                    'value': old_tile['value'],
                                    'start_pos': (i, j),
                                    'end_pos': (new_i, new_j),
                                    'start_time': time.time(),
                                    'is_merge': True
                                })
                                claimed_positions.add((new_i, new_j))
                                break
                        else:
                            continue
                        break

    def is_game_over(self) -> bool:
        """Check if no more moves are possible"""
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.grid[i][j]['value'] == 0:
                    return False
                if j < self.board_size-1 and self.grid[i][j]['value'] == self.grid[i][j+1]['value']:
                    return False
                if i < self.board_size-1 and self.grid[i][j]['value'] == self.grid[i+1][j]['value']:
                    return False
        return True

    def reset(self, board_size: int = 4, target_tile_value: int = 2048):
        self.board_size = board_size
        self.target_tile_value = target_tile_value
        self.grid = [[{'value': 0, 'id': None} for _ in range(board_size)] for _ in range(board_size)]
        self.score = 0
        self.add_random_tile()
        self.add_random_tile()
        self.won = False
        self.over = False
        self.animations = []
        self.new_tiles = []

class GameRenderer:
    def __init__(self, game: Game2048):
        self.game = game
        # 动态计算网格区域和窗口尺寸
        self.update_dimensions()
        
    def update_dimensions(self):
        """更新基于当前游戏棋盘尺寸的所有尺寸计算"""
        self.GRID_AREA = self.game.board_size * (TILE_SIZE + PADDING) + PADDING
        self.WINDOW_SIZE = (self.GRID_AREA, self.GRID_AREA + SCORE_HEIGHT)
        self.default_animation_duration = 0.2
        self.animation_duration = self.default_animation_duration
        self.pop_duration = 0.2
        
        # Settings panel state
        self.settings_visible = False
        self.settings_rect = (self.WINDOW_SIZE[0]//4, SCORE_HEIGHT, self.WINDOW_SIZE[0]//2, self.GRID_AREA - 100)
        self.settings_animation_progress = 0.0
        
        # Animation speed slider
        self.slider_x = self.settings_rect[0] + 20
        self.slider_y = self.settings_rect[1] + 100
        self.slider_width = self.settings_rect[2] - 40
        self.slider_height = 20
        self.slider_pos = 0.5  # Default position (50%)
        self.dragging_slider = False  # Add this line
        
        # Language settings
        self.current_language = "EN"
        self.language_buttons = []
        
    def toggle_settings(self):
        """Toggle settings panel visibility"""
        self.settings_visible = not self.settings_visible
        self.settings_animation_progress = 0.0
        
    def draw_settings_panel(self):
        """Draw the settings panel"""
        # Animate panel opening/closing
        if self.settings_visible:
            self.settings_animation_progress = min(self.settings_animation_progress + 0.15, 1.0)
        else:
            self.settings_animation_progress = max(self.settings_animation_progress - 0.15, 0.0)
        
        # Calculate animated panel height
        panel_height = int(self.settings_rect[3] * self.settings_animation_progress)
        
        # Draw panel background
        print(f"Draw panel background: {self.settings_rect[0]}, {self.settings_rect[1]}, {self.settings_rect[2]}, {panel_height}")
        print(f"Draw panel border: {self.settings_rect[0]}, {self.settings_rect[1]}, {self.settings_rect[2]}, {panel_height}")
        
        # Only draw content if panel is mostly open
        if self.settings_animation_progress > 0.7:
            # Draw title
            print(f"Draw title: SETTINGS")
            
            # Draw close button
            close_y = self.settings_rect[1] + 15 + (1 - self.settings_animation_progress) * 50
            print(f"Draw close button: {self.settings_rect[0] + self.settings_rect[2] - 40}, {close_y}, 25, 25")
            
            # Draw animation speed control
            print(f"Draw animation speed control: {self.settings_rect[0] + 20}, {self.settings_rect[1] + 70}, Animation Speed:")
            
            # Draw animation speed slider
            print(f"Draw animation speed slider: {self.slider_x}, {self.slider_y}, {self.slider_width}, {self.slider_height}")
            print(f"Draw slider thumb: {self.slider_x + int(self.slider_width * self.slider_pos) - 10}, {self.slider_y - 5}, 20, {self.slider_height + 10}")
            
            # Draw slider value
            speed_value = int(100 + (300 * (1 - self.slider_pos)))
            print(f"Draw slider value: {self.slider_x + self.slider_width - 40}, {self.slider_y - 30}, {speed_value}ms")
            
            # Draw reset button
            print(f"Draw reset button: {self.settings_rect[0] + self.settings_rect[2]//2 - 60}, {self.settings_rect[1] + 160}, 120, 40, Reset Game")
            
            # Draw language selection
            print(f"Draw language selection: {self.settings_rect[0] + 20}, {self.settings_rect[1] + 110}, Language:")
            
            # Draw language buttons
            button_x = self.settings_rect[0] + 120
            for i, (code, name) in enumerate(LANGUAGES.items()):
                btn_rect = (button_x, self.settings_rect[1] + 105, 80, 30)
                self.language_buttons.append((btn_rect, code))
                
                # Highlight current language
                if code == self.current_language:
                    print(f"Draw language button: {btn_rect[0]}, {btn_rect[1]}, {btn_rect[2]}, {btn_rect[3]}, {name}")
                else:
                    print(f"Draw language button: {btn_rect[0]}, {btn_rect[1]}, {btn_rect[2]}, {btn_rect[3]}, {name}")
                button_x += 90
        
    def handle_click(self, pos):
        """Handle mouse clicks"""
        # Check if settings button was clicked
        settings_btn_rect = (WINDOW_SIZE[0] - 45, 5, 40, 40)
        if (settings_btn_rect[0] <= pos[0] <= settings_btn_rect[0] + settings_btn_rect[2] and 
            settings_btn_rect[1] <= pos[1] <= settings_btn_rect[1] + settings_btn_rect[3]):
            self.toggle_settings()
            return True
            
        # Check if close button was clicked
        if self.settings_visible:
            close_rect = (self.settings_rect[0] + self.settings_rect[2] - 40, self.settings_rect[1] + 15, 25, 25)
            if (close_rect[0] <= pos[0] <= close_rect[0] + close_rect[2] and 
                close_rect[1] <= pos[1] <= close_rect[1] + close_rect[3]):
                self.settings_visible = False
                return True
                
            # Check if reset button was clicked
            reset_rect = (self.settings_rect[0] + self.settings_rect[2]//2 - 60, self.settings_rect[1] + 160, 120, 40)
            if (reset_rect[0] <= pos[0] <= reset_rect[0] + reset_rect[2] and 
                reset_rect[1] <= pos[1] <= reset_rect[1] + reset_rect[3]):
                self.game.reset()
                self.update_dimensions()  # 更新尺寸以适应新的棋盘大小
                self.settings_visible = False
                return True
                
            # Check if slider is being dragged
            slider_rect = (self.slider_x, self.slider_y, self.slider_width, self.slider_height)
            if (slider_rect[0] <= pos[0] <= slider_rect[0] + slider_rect[2] and 
                slider_rect[1] <= pos[1] <= slider_rect[1] + slider_rect[3]):
                self.dragging_slider = True  # Set dragging state
                # Calculate new slider position
                self.slider_pos = min(max((pos[0] - self.slider_x) / self.slider_width, 0), 1)
                # Update animation duration (100ms to 400ms)
                self.animation_duration = self.default_animation_duration * (1 + 3 * (1 - self.slider_pos))
                return True
                
            # Check language buttons
            for btn_rect, lang_code in self.language_buttons:
                if (btn_rect[0] <= pos[0] <= btn_rect[0] + btn_rect[2] and 
                    btn_rect[1] <= pos[1] <= btn_rect[1] + btn_rect[3]):
                    self.current_language = lang_code
                    return True
        
        return False

    def handle_mouse_move(self, pos):
        """Handle mouse movement for slider dragging"""
        if self.dragging_slider:
            # Calculate new slider position
            self.slider_pos = min(max((pos[0] - self.slider_x) / self.slider_width, 0), 1)
            # Update animation duration
            self.animation_duration = self.default_animation_duration * (1 + 3 * (1 - self.slider_pos))
            return True
        return False

    def draw(self):
        # 绘制背景
        print(f"Draw background: 0, 0, {self.WINDOW_SIZE[0]}, {self.WINDOW_SIZE[1]}, {BACKGROUND_COLOR}")
        
        # Draw score display
        self._draw_score()
        
        # Draw grid background
        print(f"Draw grid background: 0, {SCORE_HEIGHT}, {self.GRID_AREA}, {self.GRID_AREA}, {BACKGROUND_COLOR}")
        
        # Draw grid cells
        for i in range(self.game.board_size):
            for j in range(self.game.board_size):
                print(f"Draw grid cell: {j*(TILE_SIZE+PADDING)+PADDING}, {i*(TILE_SIZE+PADDING)+PADDING + SCORE_HEIGHT}, {TILE_SIZE}, {TILE_SIZE}, {EMPTY_COLOR}")
        
        # Draw animations using ID tracking
        current_time = time.time()
        for anim in self.game.animations[:]:
            elapsed = current_time - anim['start_time']
            progress = min(elapsed / self.animation_duration, 1.0)
            
            # Calculate current position
            start_i, start_j = anim['start_pos']
            end_i, end_j = anim['end_pos']
            
            # Linear interpolation (no easing)
            current_i = start_i + (end_i - start_i) * progress
            current_j = start_j + (end_j - start_j) * progress
            
            # Draw the tile at the interpolated position
            self._draw_tile(anim['value'], current_i, current_j, highlight=anim['is_merge'])
            
            # Remove finished animations
            if progress >= 1.0:
                self.game.animations.remove(anim)
        
        # Draw pop-in animations for new tiles
        current_time = time.time()
        for new_tile_info in self.game.new_tiles[:]:
            i, j = new_tile_info['position']
            elapsed = current_time - new_tile_info['start_time']
            
            if elapsed < self.pop_duration:
                # Calculate scale from 0.2 to 1.0
                progress = elapsed / self.pop_duration
                scale = 0.2 + 0.8 * progress
                
                # Draw scaled tile
                self._draw_scaled_tile(
                    new_tile_info['tile']['value'], 
                    i, j, 
                    scale
                )
            else:
                # Animation complete, remove from list
                self.game.new_tiles.remove(new_tile_info)
                # Draw tile at full size
                self._draw_tile(new_tile_info['tile']['value'], i, j)
        
        # Draw static tiles
        for i in range(self.game.board_size):
            for j in range(self.game.board_size):
                tile = self.game.grid[i][j]
                if tile['value'] != 0 and not any(
                    a['id'] == tile['id'] for a in self.game.animations
                ) and not any(
                    new_tile_info['tile']['id'] == tile['id'] for new_tile_info in self.game.new_tiles
                ):
                    self._draw_tile(tile['value'], i, j)
        
        # Draw settings panel if visible
        if self.settings_visible or self.settings_animation_progress > 0:
            self.draw_settings_panel()
        
    def _draw_score(self):
        """Draw the score at the top of the screen"""
        # Draw score background
        print(f"Draw score background: 0, 0, {self.WINDOW_SIZE[0]}, {SCORE_HEIGHT}, {BACKGROUND_COLOR}")
        
        # Draw score
        print(f"Draw score: SCORE: {self.game.score}")
        
        # Draw settings button (gear icon)
        print(f"Draw settings button: {self.WINDOW_SIZE[0] - 45}, 5, 40, 40")

    def _draw_tile(self, value, i, j, highlight=False):
        """Draw a tile at the given grid position"""
        color = TILE_COLORS.get(value, (0, 0, 0))
        
        # Adjust position for score area
        base_y = i*(TILE_SIZE+PADDING)+PADDING + SCORE_HEIGHT
        
        print(f"Draw tile: {j*(TILE_SIZE+PADDING)+PADDING}, {base_y}, {TILE_SIZE}, {TILE_SIZE}, {color}")
        
        if value != 0:
            print(f"Draw tile text: {j*(TILE_SIZE+PADDING)+PADDING + TILE_SIZE//2}, {base_y + TILE_SIZE//2}, {value}")

    def _draw_scaled_tile(self, value: int, i: float, j: float, scale: float):
        """Draw a tile with scaling effect"""
        color = TILE_COLORS.get(value, (0, 0, 0))
        scaled_size = int(TILE_SIZE * scale)
        offset = (TILE_SIZE - scaled_size) // 2
        
        # Adjust position for score area
        base_y = i*(TILE_SIZE+PADDING)+PADDING + SCORE_HEIGHT
        
        pos_x = j*(TILE_SIZE+PADDING)+PADDING + offset
        pos_y = base_y + offset
        
        print(f"Draw scaled tile: {pos_x}, {pos_y}, {scaled_size}, {scaled_size}, {color}")
        
        if value != 0:
            print(f"Draw scaled tile text: {j*(TILE_SIZE+PADDING)+PADDING + TILE_SIZE//2}, {base_y + TILE_SIZE//2}, {value}")

def main():
    game = Game2048()
    renderer = GameRenderer(game)
    running = True
    
    while running:
        renderer.draw()
        
        for event in ["MOUSEBUTTONDOWN", "KEYDOWN", "QUIT"]:
            if event == "QUIT":
                running = False
            elif event == "MOUSEBUTTONDOWN":  
                renderer.dragging_slider = False
            elif event == "KEYDOWN":
                moved = False
                if True:  # Replace with actual key press
                    moved = game.move('left')
                if moved and game.is_game_over():
                    print("Game Over! Score:", game.score)
                    running = False
            elif event == "MOUSEBUTTONDOWN":
                renderer.handle_click((0, 0))  # Replace with actual mouse position
    
    print("Game quit")

if __name__ == "__main__":
    main()
