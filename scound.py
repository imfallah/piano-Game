#############################################################################
#
#                         PIANO GAME 
#
#############################################################################

#importing libraries
import json # Import the json module for working with JSON data
import random # Import the random module for using random functions
import pygame # Import the pygame module for game and animation programming
from threading import Thread # Import the Thread class from the threading module for using concurrent threads
from objects import Tile, Square, Text, Button, Counter

#***************************#****************************#
pygame.init() # Initialize the pygame module and prepare it for use

SCREEN = WIDTH, HEIGHT = 288, 512
TILE_WIDTH = WIDTH // 4
TILE_HEIGHT = 130
# Define the screen dimensions with a width of 288 and height of 512
info = pygame.display.Info()
width = info.current_w
height = info.current_h

if width >= height:
    win = pygame.display.set_mode(SCREEN, pygame.NOFRAME)
else:
    win = pygame.display.set_mode(SCREEN, pygame.NOFRAME | pygame.SCALED | pygame.FULLSCREEN)

clock = pygame.time.Clock()
FPS = 30
# COLORS *********************************************************************
WHITE = (255, 255, 255)  # Define the color white
GRAY = (75, 75, 75)  # Define the color gray
BLUE = (30, 144, 255)  # Define the color blue
RED = (255, 0, 0)  # Define the color red

# IMAGES *********************************************************************
bg_img = pygame.image.load('image/piano-til.png')
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
# Load and scale the background image

piano_img = pygame.image.load('image/piano.png')
piano_img = pygame.transform.scale(piano_img, (212, 212))
# Load and scale the piano image

title_img = pygame.image.load('image/title.png')
title_img = pygame.transform.scale(title_img, (200, 50))
# Load and scale the title image

overlay = pygame.image.load('image/red overlay.png')
overlay = pygame.transform.scale(overlay, (WIDTH, HEIGHT))
# Load and scale the overlay image

# MUSIC **********************************************************************
buzzer_fx = pygame.mixer.Sound('sound/Piano Tiles_Sounds_piano-buzzer.mp3')
# Load the buzzer sound effect

pygame.mixer.music.load('sound/Piano Tiles_Sounds_piano-bgmusic.mp3')
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play(loops=-1)
# Load the background music, set volume, and play in a loop

# FONTS **********************************************************************
score_font = pygame.font.Font('image/Alternity-8w7J.ttf', 32)
# Load the font for the score display

title_font = pygame.font.Font('image/god-of-war.ttf', 40)
# Load the font for the title display

gameover_font = pygame.font.Font('image/Alternity-8w7J.ttf', 40)
# Load the font for the game over message

title_img = title_font.render('Piano Tiles', True, WHITE)
# Render the title text using the loaded font and set it to white color

# BUTTONS ********************************************************************
close_img = pygame.image.load('image/closeBtn.png')
replay_img = pygame.image.load('image/replay.png')
sound_off_img = pygame.image.load("image/soundOffBtn.png")
sound_on_img = pygame.image.load("image/soundOnBtn.png")

close_btn = Button(close_img, (24, 24), WIDTH // 4 - 18, HEIGHT//2 + 120)
replay_btn = Button(replay_img, (36,36), WIDTH // 2  - 18, HEIGHT//2 + 115)
sound_btn = Button(sound_on_img, (24, 24), WIDTH - WIDTH // 4 - 18, HEIGHT//2 + 120)

# GROUPS & OBJECTS ***********************************************************
tile_group = pygame.sprite.Group()
square_group = pygame.sprite.Group()
text_group = pygame.sprite.Group()

time_counter = Counter(win, gameover_font)

# FUNCTIONS ******************************************************************
def get_speed(score):
    return 200 + 5 * score

def play_notes(notePath):
    pygame.mixer.Sound(notePath).play()

# NOTES **********************************************************************
with open('notes.json') as file:
    notes_dict = json.load(file)

# VARIABLES ******************************************************************
score = 0
high_score = 0
speed = 0
clicked = False
pos = None
home_page = True
game_page = False
game_over = False
sound_on = True
count = 0
overlay_index = 0
running = True
#----------------------------------------------------------------------------

while running:
    pos = None
    
    count += 1
    if count % 100 == 0:
            square = Square(win)
            square_group.add(square)
            counter = 0
    
    win.blit(bg_img, (0,0))
    square_group.update()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or \
                event.key == pygame.K_q:
                running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            pos = event.pos
    
    if home_page:
        win.blit(piano_img, (WIDTH//8, HEIGHT//8))
        win.blit(title_img, (WIDTH // 2 - title_img.get_width() / 2 + 10, 300))
        
        # Draw the start button as a rectangle and add text
        start_button_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT - 80, 120, 40)
        pygame.draw.rect(win, BLUE, start_button_rect)  # Draw the button
        start_text = score_font.render('Start', True, WHITE)  # Render the text
        win.blit(start_text, (start_button_rect.x + 30, start_button_rect.y + 5))  # Draw the text
        
        if pos and start_button_rect.collidepoint(pos):
            home_page = False
            game_page = True
            
            x = random.randint(0, 3)
            t = Tile(x * TILE_WIDTH, -TILE_HEIGHT, win)
            tile_group.add(t)
            
            pos = None
            
            notes_list = notes_dict['2']
            note_count = 0
            pygame.mixer.set_num_channels(len(notes_list))
            
    if game_page:
        time_counter.update()
        if time_counter.count <= 0:
            for tile in tile_group:
                tile.update(speed)
                
                if pos:
                    if tile.rect.collidepoint(pos):
                        if tile.alive:
                            tile.alive = False
                            score += 1
                            if score >= high_score:
                                high_score = score
                                
                            note = notes_list[note_count].strip()
                            th = Thread(target=play_notes, args=(f'Sound/{note}.ogg', ))
                            th.start()
                            th.join()
                            note_count = (note_count + 1) % len(notes_list)
                            
                            tpos = tile.rect.centerx - 10, tile.rect.y
                            text = Text('+1', score_font, tpos, win)
                            text_group.add(text)
                            
                        pos = None
                        
                if tile.rect.bottom >= HEIGHT and tile.alive:
                    if not game_over:
                        tile.color = (255, 0, 0)
                        buzzer_fx.play()
                        game_over = True
                        
            if pos:
                buzzer_fx.play()
                game_over = True
                
            if len(tile_group) > 0:
                t = tile_group.sprites()[-1]
                if t.rect.top + speed >= 0:
                    x = random.randint(0, 3)
                    y = -TILE_HEIGHT - (0 - t.rect.top)
                    t = Tile(x * TILE_WIDTH, y, win)
                    tile_group.add(t)
                    
            text_group.update(speed)
            img1 = score_font.render(f'Score : {score}', True, WHITE)
            win.blit(img1, (70 - img1.get_width() / 2, 10))
            img2 = score_font.render(f'High : {high_score}', True, WHITE)
            win.blit(img2, (200 - img2.get_width() / 2, 10))
            for i in range(4):
                pygame.draw.line(win, WHITE, (TILE_WIDTH * i, 0), (TILE_WIDTH*i, HEIGHT), 1)
                
            speed = int(get_speed(score) * (FPS / 1000))
            
            if game_over:
                speed = 0
                
                if overlay_index > 20:
                    win.blit(overlay, (0,0))
                    
                    img1 = gameover_font.render('Game over', True, WHITE)
                    img2 = score_font.render(f'Score : {score}', True, WHITE)
                    win.blit(img1, (WIDTH // 2 - img1.get_width() / 2, 180))
                    win.blit(img2, (WIDTH // 2 - img2.get_width() / 2, 250))
                    
                    if close_btn.draw(win):
                        running = False
                        
                    if replay_btn.draw(win):
                        index = random.randint(1, len(notes_dict))
                        notes_list = notes_dict[str(index)]
                        note_count = 0
                        pygame.mixer.set_num_channels(len(notes_list))
                        
                        text_group.empty()
                        tile_group.empty()
                        score = 0
                        game_over = False
                        pos = None
                        
                        overlay_index = 0

                overlay_index += 1
                
    text_group.draw(win)
    tile_group.draw(win)
    square_group.draw(win)

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
