import pygame
import random
import sys
import subprocess
import os
import time

# Configuration
WIDTH = 1280
HEIGHT = 720
GRID_SIZE = 20
CELL_SIZE = min(WIDTH, HEIGHT) // GRID_SIZE
NUM_MINES = 45  # Augmenter le nombre de bombes
FPS = 30

# Chemin vers le répertoire du script
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Chemins vers les ressources
boom_sound_path = os.path.join(BASE_PATH, "boom.mp3")
flag_image_path = os.path.join(BASE_PATH, "flag.png")
explo_gif_path = os.path.join(BASE_PATH, "explo.gif")
APOCALYPSE_FONT_PATH = os.path.join(BASE_PATH, "APOCALYPSE.ttf")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Démineur")
clock = pygame.time.Clock()

# Chargement de la police
font = pygame.font.SysFont(None, 30)
message_font = pygame.font.Font(APOCALYPSE_FONT_PATH, 80)
counter_font = pygame.font.SysFont(None, 50)

# Charger l'image de la bombe
bomb_image = pygame.image.load(flag_image_path)
bomb_image = pygame.transform.scale(bomb_image, (CELL_SIZE, CELL_SIZE))

# Calcul des décalages pour centrer la grille avec une marge de 2 cases en haut et en bas
x_offset = (WIDTH - (CELL_SIZE * GRID_SIZE)) // 2
y_offset = (HEIGHT - (CELL_SIZE * (GRID_SIZE + 4))) // 2 + 2 * CELL_SIZE

# Définir les dimensions et la position du bouton "Quitter"
quit_button_width = 100
quit_button_height = 40
quit_button_x = WIDTH - quit_button_width - 10
quit_button_y = HEIGHT - quit_button_height - 10
quit_button_rect = pygame.Rect(quit_button_x, quit_button_y, quit_button_width, quit_button_height)

# Définir les dimensions et la position du bouton "Menu"
menu_button_width = 100
menu_button_height = 40
menu_button_x = 10
menu_button_y = HEIGHT - menu_button_height - 10
menu_button_rect = pygame.Rect(menu_button_x, menu_button_y, menu_button_width, menu_button_height)

# Charger le GIF
gif = pygame.image.load(explo_gif_path)
frames = [pygame.transform.scale(gif.subsurface(frame), (WIDTH, HEIGHT)) for frame in range(gif.get_rect().w // WIDTH)]

# Charger la police Apocalypse
title_font = pygame.font.Font(APOCALYPSE_FONT_PATH, 80)

# Charger le son boom
boom_sound = pygame.mixer.Sound(boom_sound_path)

# Génération de la grille
def create_grid():
    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    mines = set()
    
    while len(mines) < NUM_MINES:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if (x, y) not in mines:
            mines.add((x, y))
            grid[y][x] = -1
    
    for x, y in mines:
        for i in range(max(0, x - 1), min(GRID_SIZE, x + 2)):
            for j in range(max(0, y - 1), min(GRID_SIZE, y + 2)):
                if grid[j][i] != -1:
                    grid[j][i] += 1

    return grid, mines

# Affichage de la grille
def draw_grid(grid, revealed, flags):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE + x_offset, y * CELL_SIZE + y_offset, CELL_SIZE, CELL_SIZE)
            if revealed[y][x]:
                if grid[y][x] == -1:
                    screen.blit(bomb_image, rect.topleft)
                else:
                    pygame.draw.rect(screen, WHITE, rect)
                    if grid[y][x] > 0:
                        text = font.render(str(grid[y][x]), True, BLACK)
                        screen.blit(text, (x * CELL_SIZE + 10 + x_offset, y * CELL_SIZE + 10 + y_offset))
            else:
                pygame.draw.rect(screen, GRAY, rect)
                if (x, y) in flags:
                    pygame.draw.rect(screen, RED, rect)  # Dessiner en rouge si le drapeau est posé
            pygame.draw.rect(screen, BLACK, rect, 1)

# Révéler les cellules
def reveal_cell(grid, revealed, x, y):
    if revealed[y][x]:
        return
    revealed[y][x] = True
    if grid[y][x] == 0:
        for i in range(max(0, x - 1), min(GRID_SIZE, x + 2)):
            for j in range(max(0, y - 1), min(GRID_SIZE, y + 2)):
                if not revealed[j][i]:
                    reveal_cell(grid, revealed, i, j)

# Affichage du bouton "Quitter"
def draw_quit_button():
    pygame.draw.rect(screen, RED, quit_button_rect)
    text = font.render("Quitter", True, WHITE)
    text_rect = text.get_rect(center=quit_button_rect.center)
    screen.blit(text, text_rect)

# Affichage du bouton "Menu"
def draw_menu_button():
    pygame.draw.rect(screen, GREEN, menu_button_rect)
    text = font.render("Menu", True, WHITE)
    text_rect = text.get_rect(center=menu_button_rect.center)
    screen.blit(text, text_rect)

# Affichage des compteurs
def draw_counters(win_count, lost_count):
    win_text = counter_font.render(f"WIN: {win_count}", True, GREEN)
    lost_text = counter_font.render(f"LOST: {lost_count}", True, RED)
    screen.blit(win_text, (10, 10))
    screen.blit(lost_text, (10, 60))

# Fonction pour ouvrir level.py
def open_level():
    subprocess.Popen(["python", os.path.join(BASE_PATH, "level.py")])

# Vérifier si le joueur a gagné
def check_win(grid, revealed):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x] != -1 and not revealed[y][x]:
                return False
    return True

# Boucle principale
def main():
    grid, mines = create_grid()
    revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    flags = set()
    game_over = False
    win = False
    win_count = 0
    lost_count = 0

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if quit_button_rect.collidepoint(x, y):
                    pygame.quit()
                    sys.exit()
                elif menu_button_rect.collidepoint(x, y):
                    open_level()
                    pygame.quit()
                    sys.exit()
                if not game_over and not win:
                    x = (x - x_offset) // CELL_SIZE
                    y = (y - y_offset) // CELL_SIZE
                    if x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE:
                        continue
                    if event.button == 1:  # Left click
                        if (x, y) in flags:
                            continue
                        if grid[y][x] == -1:
                            game_over = True
                            revealed = [[True for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
                            boom_sound.play()  # Jouer le son de l'explosion
                            lost_count += 1
                        else:
                            reveal_cell(grid, revealed, x, y)
                            if check_win(grid, revealed):
                                win = True
                                win_count += 1
                    elif event.button == 3:  # Right click
                        if (x, y) in flags:
                            flags.remove((x, y))
                        else:
                            flags.add((x, y))

        draw_grid(grid, revealed, flags)
        draw_quit_button()
        draw_menu_button()
        draw_counters(win_count, lost_count)

        if win:
            win_text = message_font.render("WIN", True, GREEN)
            win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(win_text, win_rect)
            pygame.display.flip()
            time.sleep(2)  # Attendre 2 secondes
            grid, mines = create_grid()  # Redémarrer le jeu
            revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
            flags = set()
            game_over = False
            win = False

        if game_over:
            game_over_text = message_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(game_over_text, game_over_rect)
            pygame.display.flip()
            time.sleep(2)  # Attendre 2 secondes
            grid, mines = create_grid()  # Redémarrer le jeu
            revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
            flags = set()
            game_over = False
            win = False

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
