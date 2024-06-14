import pygame
import sys
import os
from PIL import Image

# Configuration
WIDTH = 1280
HEIGHT = 720
FPS = 33  # Synchronisation avec le GIF

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Choisissez le niveau")
clock = pygame.time.Clock()

# Chemin vers le répertoire du script
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Chemins vers les ressources
gif_path = os.path.join(BASE_PATH, "explo.gif")
title_font_path = os.path.join(BASE_PATH, "APOCALYPSE.ttf")
music_path = os.path.join(BASE_PATH, "bo.mp3")
facile_script_path = os.path.join(BASE_PATH, "facile.py")
moyen_script_path = os.path.join(BASE_PATH, "moyen.py")
difficile_script_path = os.path.join(BASE_PATH, "difficile.py")

# Charger le GIF et extraire les frames
gif = Image.open(gif_path)
frames = []
for frame in range(gif.n_frames):
    gif.seek(frame)
    frame_image = gif.copy()
    frame_image = frame_image.convert("RGBA")
    frame_image = frame_image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    frame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode).convert_alpha()
    frames.append(frame_surface)

# Chargement de la police APOCALYPSE pour le titre
title_font = pygame.font.Font(title_font_path, 80)

# Charger l'audio et le jouer en boucle
pygame.mixer.music.load(music_path)
pygame.mixer.music.play(-1)  # -1 indique la lecture en boucle

# Création des boutons
font = pygame.font.SysFont(None, 50)

def create_button(text, position):
    text_surface = font.render(text, True, WHITE)
    rect = text_surface.get_rect(center=position)
    return text_surface, rect

buttons = {
    "Facile": create_button("Facile", (WIDTH // 2, HEIGHT // 3)),
    "Moyen": create_button("Moyen", (WIDTH // 2, HEIGHT // 2)),
    "Difficile": create_button("Difficile", (WIDTH // 2, HEIGHT * 2 // 3)),
    "Quitter": create_button("Quitter", (WIDTH // 2, HEIGHT * 5 // 6))
}

# Créer le titre
title_text = title_font.render("DEMINEUR", True, WHITE)
title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 8))

# Boucle principale
frame_index = 0
running = True
frame_delay = 1000 // FPS  # Temps d'affichage de chaque frame (ms)

while running:
    start_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for level, (text_surface, rect) in buttons.items():
                if rect.collidepoint(event.pos):
                    if level == "Facile":
                        pygame.quit()
                        os.execl(sys.executable, sys.executable, facile_script_path)
                    elif level == "Moyen":
                        pygame.quit()
                        os.execl(sys.executable, sys.executable, moyen_script_path)
                    elif level == "Difficile":
                        pygame.quit()
                        os.execl(sys.executable, sys.executable, difficile_script_path)
                    elif level == "Quitter":
                        pygame.quit()
                        sys.exit()

    # Afficher la frame courante du GIF
    screen.blit(frames[frame_index], (0, 0))
    frame_index = (frame_index + 1) % len(frames)

    # Afficher le titre
    screen.blit(title_text, title_rect)

    # Dessiner les boutons
    for text_surface, rect in buttons.values():
        pygame.draw.rect(screen, DARK_GRAY, rect.inflate(10, 10))
        pygame.draw.rect(screen, LIGHT_GRAY, rect.inflate(5, 5))
        pygame.draw.rect(screen, BLACK, rect)
        screen.blit(text_surface, rect.topleft)

    pygame.display.flip()
    clock.tick(FPS)

    # Attendre pour maintenir la fréquence d'images
    elapsed_time = pygame.time.get_ticks() - start_time
    pygame.time.delay(max(frame_delay - elapsed_time, 0))

# Arrêter la musique et quitter proprement
pygame.mixer.music.stop()
pygame.quit()
sys.exit()
