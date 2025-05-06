"""
Created and modified by Matthew Bigotta
Minesweeper Legacy: Used the original Minesweeper game from Github library and add some modifications of my own such as difficulty selection, pause menu, best-time tracking, and smooth animations
Use hints from numbers on box that will tell you the surrounding amount of bombs on 8 spaces around that box and avoid them!
"""

import random, pygame, sys, json, os
from pygame.locals import QUIT, MOUSEBUTTONDOWN, KEYDOWN, K_ESCAPE, K_SPACE

# ====================== Setting up window constraints ======================

FPS = 30
WINDOWWIDTH = 800
WINDOWHEIGHT = 800
BOXSIZE = 30
GAPSIZE = 5
FIELDWIDTH = 20
FIELDHEIGHT = 20
XMARGIN = int((WINDOWWIDTH - (FIELDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (FIELDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

# =============== Setting up difficulty settings and initial value  ===============

VERY_EASY_MINES = 10
EASY_MINES = 30
NORMAL_MINES = 50
HARD_MINES = 70
currentDifficulty = 'NORMAL'
MINESTOTAL = NORMAL_MINES

# =============================== Assertions ===============================

assert BOXSIZE/2 > 5, 'Bounding errors when drawing rectangle'

# ============ Setting up specific colors to their own variable ============

LIGHTGRAY = (225, 225, 225)
DARKGRAY = (160, 160, 160)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
BGCOLOR = WHITE
FIELDCOLOR = BLACK
BOXCOLOR_COV = DARKGRAY
BOXCOLOR_REV = LIGHTGRAY
MINECOLOR = BLACK
TEXTCOLOR_3 = BLACK
HILITECOLOR = GREEN
RESETBGCOLOR = LIGHTGRAY
MINEMARK_COV = RED

# ================================= Font ================================= 

FONTTYPE = 'Courier New'
FONTSIZE = 20

# =========================== Utility Functions ===========================

def terminate():
    # Safely quit the game and close the program
    pygame.quit()
    sys.exit()

def drawText(text, font, color, surface, x, y):
    # Render and draw centered text on a given surface
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def drawButton(text, color, bgcolor, center_x, center_y):
    # Create a surface and rect for a button with centered text
    butSurf = BASICFONT.render(text, True, color, bgcolor)
    butRect = butSurf.get_rect(center=(center_x, center_y))
    return (butSurf, butRect)

def getLeftTopXY(box_x, box_y):
    # Get top-left pixel coordinates of the given box
    left = XMARGIN + box_x * (BOXSIZE + GAPSIZE)
    top = YMARGIN + box_y * (BOXSIZE + GAPSIZE)
    return left, top

def getCenterXY(box_x, box_y):
    # Get center pixel coordinates of the given box
    center_x = XMARGIN + BOXSIZE // 2 + box_x * (BOXSIZE + GAPSIZE)
    center_y = YMARGIN + BOXSIZE // 2 + box_y * (BOXSIZE + GAPSIZE)
    return center_x, center_y

def getBoxAtPixel(x, y):
    # Convert mouse pixel position to grid box coordinates
    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            if pygame.Rect(left, top, BOXSIZE, BOXSIZE).collidepoint(x, y):
                return box_x, box_y
    return None, None

def highlightBox(box_x, box_y):
    # Draw a green outline around a box to indicate hover
    left, top = getLeftTopXY(box_x, box_y)
    pygame.draw.rect(DISPLAYSURFACE, HILITECOLOR, (left, top, BOXSIZE, BOXSIZE), 4)

def highlightButton(butRect):
    # Draw a green border around a button to indicate hover
    pygame.draw.rect(DISPLAYSURFACE, HILITECOLOR, butRect.inflate(8, 8), 4)

# ===================== Draw the empty field (boxes only) =====================

def drawField():
    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            pygame.draw.rect(DISPLAYSURFACE, BOXCOLOR_REV, (left, top, BOXSIZE, BOXSIZE))

# ===================== Draw mines and number clues =====================

def drawMinesNumbers(field):
    half = int(BOXSIZE*0.5) 
    quarter = int(BOXSIZE*0.25)
    eighth = int(BOXSIZE*0.125)
    
    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            center_x, center_y = getCenterXY(box_x, box_y)
            if field[box_x][box_y] == '[X]':
                pygame.draw.circle(DISPLAYSURFACE, MINECOLOR, (left+half, top+half), quarter)
                pygame.draw.circle(DISPLAYSURFACE, WHITE, (left+half, top+half), eighth)
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+eighth, top+half), (left+half+quarter+eighth, top+half))
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+half, top+eighth), (left+half, top+half+quarter+eighth))
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+quarter, top+quarter), (left+half+quarter, top+half+quarter))
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+quarter, top+half+quarter), (left+half+quarter, top+quarter))
            else: 
                for i in range(1, 9):
                    if field[box_x][box_y] == '[' + str(i) + ']':
                        if i == 1:
                            textColor = BLUE
                        elif i == 2:
                            textColor = GREEN
                        elif i == 3:
                            textColor = RED
                        else:
                            textColor = TEXTCOLOR_3
                        drawText(str(i), BASICFONT, textColor, DISPLAYSURFACE, center_x, center_y)


# ===================== Draw box covers (gray for unrevealed box and red for marked mines) =====================

def drawCovers(revealedBoxes, markedMines):
    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            if not revealedBoxes[box_x][box_y]:
                left, top = getLeftTopXY(box_x, box_y)
                if [box_x, box_y] in markedMines:
                    pygame.draw.rect(DISPLAYSURFACE, MINEMARK_COV, (left, top, BOXSIZE, BOXSIZE))
                else:
                    pygame.draw.rect(DISPLAYSURFACE, BOXCOLOR_COV, (left, top, BOXSIZE, BOXSIZE))

# ===================== Define pause menu overlay and best time drawing =====================

def drawPauseMenu(paused_elapsed_seconds, score_manager):
    overlay = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
    overlay.set_alpha(220)
    overlay.fill((50, 50, 50))
    DISPLAYSURFACE.blit(overlay, (0, 0))

    # Format pause time
    paused_minutes = paused_elapsed_seconds // 60
    paused_seconds = paused_elapsed_seconds % 60

    # Menu lines (with your original \n kept intact)
    lines = [
        "PAUSED",
        "Press ESC to resume",
        f"Current Difficulty: {currentDifficulty}",
        f"Paused at: {paused_minutes:02}:{paused_seconds:02}",
        "Controls:",
        "Left click: reveal box",
        "Spacebar: mark/unmark box",
        "Tip:",
        "Pay close attention to the numbers, they're your guide.",
        "Use number clues to safely uncover \nthe board and avoid hidden mines!",
        "Best Times:"
    ]

    # Layout: higher start, wider spacing
    top_padding = 30
    line_spacing = 50  # more space between lines
    current_y = top_padding

    for line in lines:
        if '\n' in line:
            for subline in line.split('\n'):
                drawText(subline, BASICFONT, WHITE, DISPLAYSURFACE, WINDOWWIDTH / 2, current_y)
                current_y += line_spacing
        else:
            drawText(line, BASICFONT, WHITE, DISPLAYSURFACE, WINDOWWIDTH / 2, current_y)
            current_y += line_spacing

    # Display the best recorded times for each difficulty
    best_times = score_manager.get_all_best_times()
    for difficulty, time in best_times.items():
        time_text = f"{difficulty}: {time}s" if time is not None else f"{difficulty}: --"
        drawText(time_text, BASICFONT, WHITE, DISPLAYSURFACE, WINDOWWIDTH / 2, current_y)
        current_y += line_spacing

# ===================== ScoreManager: Tracks and saves best times =====================

class ScoreManager:
    def __init__(self, filename='wins.json'):
        # Initialize ScoreManager with a file to load/save best times
        self._filename = filename
        self._cache = self.load_scores()

    def load_scores(self):
        # Load score data from JSON file if it exists
        if os.path.exists(self._filename):
            with open(self._filename, 'r') as f:
                return json.load(f)
        return []

    def save_score(self, difficulty, time_seconds):
        # Save a new time for the given difficulty and write to file
        self._cache.append({'difficulty': difficulty, 'time': time_seconds})
        with open(self._filename, 'w') as f:
            json.dump(self._cache, f)

    def get_best_time(self, difficulty):
        # Return the best (lowest) time for the given difficulty
        times = [entry['time'] for entry in self._cache if entry['difficulty'] == difficulty]
        return min(times) if times else None

    def get_all_best_times(self):
        # Return best times for all difficulties as a dictionary
        difficulties = ['VERY EASY', 'EASY', 'NORMAL', 'HARD']
        return {d: self.get_best_time(d) for d in difficulties}

# ===================== Minefield logic and operations =====================

class Minefield:
    def __init__(self, width, height, mine_count):
        # Initialize minefield dimensions and mine count
        self._width = width
        self._height = height
        self._mine_count = mine_count
        self._field = self.create_blank_field()
        self._revealed = [[False] * height for _ in range(width)] # Tracking revealed boxes
        self._marked = [] # List of marked boxes
        self._zero_reveal_queue = [] # Queue for recursive zero reveals
        # Generate the field
        self.place_mines()
        self.place_numbers()

    def create_blank_field(self):
        # Create a blank field with placeholder values
        return [['[ ]' for _ in range(self._height)] for _ in range(self._width)]

    def place_mines(self):
        # Randomly place mines in the field
        placed = 0
        while placed < self._mine_count:
            x = random.randint(0, self._width - 1)
            y = random.randint(0, self._height - 1)
            if self._field[x][y] != '[X]':
                self._field[x][y] = '[X]'
                placed += 1

    def place_numbers(self):
        # Add number hints based on nearby mines
        for x in range(self._width):
            for y in range(self._height):
                if self._field[x][y] != '[X]':
                    count = sum(1 for nx, ny in self.get_neighbors(x, y)
                                if self._field[nx][ny] == '[X]')
                    self._field[x][y] = f'[{count}]'

    def get_neighbors(self, x, y):
        # Get all valid neighboring box coordinates (8 directions)
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self._width and 0 <= ny < self._height:
                    neighbors.append((nx, ny))
        return neighbors

    def reveal(self, x, y):
        # Reveal a box, and recursively reveal zeros if needed
        if self._revealed[x][y]:
            return
        self._revealed[x][y] = True
        if self._field[x][y] == '[0]':
            self.reveal_zeros(x, y)

    def reveal_zeros(self, x, y):
        # Recursive reveal for blank areas
        self._zero_reveal_queue.append((x, y))
        seen = set(self._zero_reveal_queue)
        while self._zero_reveal_queue:
            cx, cy = self._zero_reveal_queue.pop(0)
            for nx, ny in self.get_neighbors(cx, cy):
                if not self._revealed[nx][ny]:
                    self._revealed[nx][ny] = True
                    if self._field[nx][ny] == '[0]' and (nx, ny) not in seen:
                        self._zero_reveal_queue.append((nx, ny))
                        seen.add((nx, ny))

    def all_safe_revealed(self):
        # Check if all non-mine tiles are revealed
        safe = self._width * self._height - self._mine_count
        count = sum(1 for x in range(self._width)
                    for y in range(self._height)
                    if self._revealed[x][y] and self._field[x][y] != '[X]')
        return count == safe

    def is_mine(self, x, y):
        # Check if a tile is a mine
        return self._field[x][y] == '[X]'

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_field(self):
        return self._field

    def get_revealed(self):
        return self._revealed

    def get_marked(self):
        return self._marked

# ===================== Game class manages game state and logic =====================

class Game:
    def __init__(self, width, height, mine_count, score_manager):
        # Create the minefield with specified parameters
        self.minefield = Minefield(width, height, mine_count)
        #Set score manager
        self.score_manager = score_manager
        # Track game timing and pause status
        self.start_time = pygame.time.get_ticks()
        self.paused = False
        self.pause_time = 0
        self.final_time = None
        self.total_pause_duration = 0
        # Track game result
        self.game_over = False
        self.win = False
        self.started = False  # Timer doesn't start until first click


    def update_timer(self):
        # Returns 0 if game hasn't started
        if not self.started:
            return 0
        if self.final_time is not None:
            return self.final_time  # Freeze timer on win/loss
        if self.paused:
            return self.pause_time  # Freeze timer while paused
        return pygame.time.get_ticks() - self.start_time - self.total_pause_duration

    def toggle_pause(self):
        # Pause/unpause the game and track pause time
        if not self.paused:
            self.paused = True
            # Store the elapsed time up to this moment
            self.pause_time = pygame.time.get_ticks() - self.start_time - self.total_pause_duration
        else:
            self.paused = False
            # Add the time spent paused to total pause duration
            paused_duration = pygame.time.get_ticks() - (self.start_time + self.pause_time + self.total_pause_duration)
            self.total_pause_duration += paused_duration

    def handle_click(self, x, y, right_click=False):
        # Handle left and right mouse clicks
        if self.game_over:
            return
        if not self.started:
            self.started = True
            self.start_time = pygame.time.get_ticks()

        if right_click:
            pos = [x, y]
            if pos in self.minefield.get_marked():
                self.minefield.get_marked().remove(pos)
            else:
                self.minefield.get_marked().append(pos)
        else:
            self.minefield.reveal(x, y)
            # Trigger game over sequence if player clicked on a bomb
            if self.minefield.is_mine(x, y):
                self.game_over = True
                self.win = False
                self.final_time = self.update_timer()
                for i in range(self.minefield.get_width()):
                    for j in range(self.minefield.get_height()):
                        if self.minefield.get_field()[i][j] == '[X]':
                            self.minefield.get_revealed()[i][j] = True
                            
            # All safe tiles revealed, player wins the game
            elif self.minefield.all_safe_revealed():
                self.game_over = True
                self.win = True
                self.final_time = self.update_timer()
                self.score_manager.save_score(currentDifficulty, self.get_elapsed_seconds())
                for i in range(self.minefield.get_width()):
                    for j in range(self.minefield.get_height()):
                        if self.minefield.get_field()[i][j] != '[X]':
                            self.minefield.get_revealed()[i][j] = True

    def get_elapsed_seconds(self):
        # Return how many seconds have passed since game start
        return self.update_timer() // 1000

    def reset(self, width, height, mine_count):
        # Reset the game using new parameters
        self.__init__(width, height, mine_count)

# ===================== Main game loop and event handling =====================

def main():
    # Global variables used for rendering and tracking
    global DISPLAYSURFACE, BASICFONT, RESET_SURF, RESET_RECT
    global VERY_EASY_RECT, EASY_RECT, NORMAL_RECT, HARD_RECT, currentDifficulty, MINESTOTAL
    # Create a ScoreManager instance to track and retrieve best completion times
    score_manager = ScoreManager()
    # Initialize Pygame and set up display
    pygame.init()
    pygame.display.set_caption("Minesweeper Legacy")
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURFACE = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.SysFont(FONTTYPE, FONTSIZE, bold=True)
    # Create reset and difficulty buttons
    RESET_SURF, RESET_RECT = drawButton("RESET", TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH / 2 - 300, WINDOWHEIGHT - 50)
    VERY_EASY_SURF, VERY_EASY_RECT = drawButton("VERY EASY", TEXTCOLOR_3, RESETBGCOLOR, 110, 30)
    EASY_SURF, EASY_RECT = drawButton("EASY", TEXTCOLOR_3, RESETBGCOLOR, 310, 30)
    NORMAL_SURF, NORMAL_RECT = drawButton("NORMAL", TEXTCOLOR_3, RESETBGCOLOR, 510, 30)
    HARD_SURF, HARD_RECT = drawButton("HARD", TEXTCOLOR_3, RESETBGCOLOR, 710, 30)
    # Create initial game state
    currentDifficulty = 'NORMAL'
    MINESTOTAL = NORMAL_MINES
    game = Game(FIELDWIDTH, FIELDHEIGHT, MINESTOTAL, score_manager)
    # Flash effect state (used to flash screen color on game over)
    flash_alpha = 0
    flash_direction = 20
    flash_started = False

    # ========================= Main game loop =========================

    while True:
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouseClicked = False
        rightClicked = False
        
        # Event processing
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            # Detect mouse click and check if it's a right-click
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                mouseClicked = True
                if event.button == 3: \
                    rightClicked = True
            # Handle keyboard shortcuts: pause with ESC, flag with SPACE
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    game.toggle_pause()
                elif event.key == K_SPACE: 
                    box_x, box_y = getBoxAtPixel(mouse_x, mouse_y)
                    if box_x is not None and box_y is not None:
                        game.handle_click(box_x, box_y, right_click=True)

        # Pause screen rendering
        if game.paused:
            drawPauseMenu(game.get_elapsed_seconds(), score_manager)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
            continue

        # Clear screen for new frame
        DISPLAYSURFACE.fill(BGCOLOR)

        # Flashing screen if game is over
        if game.game_over:
            if not flash_started:
                flash_alpha = 0
                flash_direction = 20
                flash_started = True  # ✅ Only initialize once

            flash_alpha += flash_direction
            if flash_alpha >= 255:
                flash_alpha = 255
                flash_direction = -20
            elif flash_alpha <= 0:
                flash_alpha = 0
                flash_direction = 20
                
            # Create color flash overlay (blue if win, red if loss)
            flash_color = BLUE if game.win else RED
            flash_surf = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT), pygame.SRCALPHA)
            flash_surf.fill((*flash_color, flash_alpha))
            
            # Leave game grid visible
            grid_rect = pygame.Rect(
                XMARGIN,
                YMARGIN,
                (BOXSIZE + GAPSIZE) * FIELDWIDTH,
                (BOXSIZE + GAPSIZE) * FIELDHEIGHT
            )
            flash_surf.fill((0, 0, 0, 0), rect=grid_rect)
            
            DISPLAYSURFACE.blit(flash_surf, (0, 0))

        # Draw the game field background
        pygame.draw.rect(DISPLAYSURFACE, FIELDCOLOR, (
            XMARGIN - 5,
            YMARGIN - 5,
            (BOXSIZE + GAPSIZE) * FIELDWIDTH + 5,
            (BOXSIZE + GAPSIZE) * FIELDHEIGHT + 5
        ))

        drawField() # Draw empty boxes

        # ===================== Difficulty switching logic =====================

        if not game.game_over:
            for rect, mines, label in [
                (VERY_EASY_RECT, VERY_EASY_MINES, 'VERY EASY'),
                (EASY_RECT, EASY_MINES, 'EASY'),
                (NORMAL_RECT, NORMAL_MINES, 'NORMAL'),
                (HARD_RECT, HARD_MINES, 'HARD')
            ]:
                if rect.collidepoint(mouse_x, mouse_y):
                    highlightButton(rect)
                    if mouseClicked:
                        MINESTOTAL = mines
                        currentDifficulty = label
                        game = Game(FIELDWIDTH, FIELDHEIGHT, MINESTOTAL, score_manager)
                        flash_alpha = 0
                        flash_direction = 20
                        flash_started = False

                drawText(label, BASICFONT, GREEN if label == currentDifficulty else RED, DISPLAYSURFACE, rect.centerx, rect.centery)

        # ===================== Reset button =====================

        # Restart the game when the reset button is clicked
        if RESET_RECT.collidepoint(mouse_x, mouse_y):
            highlightButton(RESET_RECT)
            if mouseClicked:
                game = Game(FIELDWIDTH, FIELDHEIGHT, MINESTOTAL, score_manager)
                
        DISPLAYSURFACE.blit(RESET_SURF, RESET_RECT)

        # ===================== Mouse hover + click on boxes =====================

        box_x, box_y = getBoxAtPixel(mouse_x, mouse_y)
        if box_x is not None and box_y is not None:
            if not game.minefield.get_revealed()[box_x][box_y]:
                highlightBox(box_x, box_y)

            # Reveal or mark box when clicked
            if mouseClicked and not game.game_over:
                game.handle_click(box_x, box_y, right_click=rightClicked)

        # ===================== Draw field and cover =====================

        drawMinesNumbers(game.minefield.get_field())
        drawCovers(game.minefield.get_revealed(), game.minefield.get_marked())

        # ===================== Display time, bombs, and flags =====================

        elapsed = game.get_elapsed_seconds()
        flags_used = len(game.minefield.get_marked())
        start_x = WINDOWWIDTH // 2 - 300
        y_pos = YMARGIN + FIELDHEIGHT * (BOXSIZE + GAPSIZE) + 20
        spacing = 190
        
        RESET_RECT.centerx = start_x
        RESET_RECT.centery = y_pos

        drawText(f"Time: {elapsed // 60:02}:{elapsed % 60:02}", BASICFONT, BLACK, DISPLAYSURFACE, start_x + spacing, y_pos)
        drawText(f"Bombs: {MINESTOTAL}", BASICFONT, BLACK, DISPLAYSURFACE, start_x + spacing * 2, y_pos)
        drawText(f"Flags: {flags_used}", BASICFONT, BLACK, DISPLAYSURFACE, start_x + spacing * 3, y_pos)

        # ===================== Refresh screen and control FPS =====================

        pygame.display.update()
        FPSCLOCK.tick(FPS)

# =========================== Run the code ===========================

if __name__ == '__main__':
    main()
