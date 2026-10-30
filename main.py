import pygame
import sys
import random
import math

pygame.init()

# ---------------- HIGH SCORE ----------------
def load_highscore():
    try:
        with open("highscore.txt", "r") as file:
            return int(file.read())
    except (FileNotFoundError, ValueError):
        return 0


def save_highscore(value):
    with open("highscore.txt", "w") as file:
        file.write(str(value))


high_score = load_highscore()

# ---------------- WINDOW ----------------
WIDTH = 600
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vampy")

clock = pygame.time.Clock()


# ---------------- ASSETS ----------------

background = pygame.image.load(
    "assets/background.png"
).convert()

background = pygame.transform.scale(
    background, (WIDTH, HEIGHT)
)

bg_x = 0
bg_y = 0


start_background = pygame.image.load(
    "assets/start_background.png"
).convert()

img_w, img_h = start_background.get_size()

scale = max(WIDTH / img_w, HEIGHT / img_h)

new_w = int(img_w * scale)
new_h = int(img_h * scale)

start_background = pygame.transform.smoothscale(
    start_background, (new_w, new_h)
)

start_bg_x = (WIDTH - new_w) // 2
start_bg_y = (HEIGHT - new_h) // 2


vampire = pygame.image.load("assets/vampire.png").convert_alpha()

vampire_width = 150
scale = vampire_width / vampire.get_width()

vampire = pygame.transform.smoothscale(
    vampire,
    (
        vampire_width,
        int(vampire.get_height() * scale)
    )
)


garlic = pygame.image.load(
    "assets/garlic.png"
).convert_alpha()

garlic = pygame.transform.smoothscale(
    garlic,
    (60, 60)
)

# Custom pixel-game font
font = pygame.font.Font("assets/HomeVideo-Bold.ttf", 28)
small_font = pygame.font.Font("assets/HomeVideo-Bold.ttf", 22)

# Pixel heart
heart = pygame.image.load("assets/heart.png").convert()
heart.set_colorkey((255, 255, 255))
heart = pygame.transform.smoothscale(heart, (28, 28))


# ---------------- VAMPIRE ----------------
vampire_rect = vampire.get_rect(
    center=(WIDTH // 2, HEIGHT // 2)
)

vampire_base_y = vampire_rect.centery


# ---------------- GARLIC ----------------
garlics = []

garlic_speed = 1
score = 0
lives = 3
game_over = False 
game_started = False  

# Clickable area over the PLAY button in your start image
play_button = pygame.Rect(200, 575, 200, 90)

spawn_timer = 0
spawn_delay = 65


def spawn_garlic():

    angle = random.uniform(0, 2 * math.pi)

    spawn_distance = max(WIDTH, HEIGHT) // 2 + 100

    x = vampire_rect.centerx + math.cos(angle) * spawn_distance
    y = vampire_rect.centery + math.sin(angle) * spawn_distance

    rect = garlic.get_rect(
        center=(round(x), round(y))
    )

    garlics.append({
        "x": float(x),
        "y": float(y),
        "rect": rect
    })
# ---------------- GAME LOOP ----------------
running = True

while running:

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

           mouse_pos = event.pos

           if not game_started:
               if play_button.collidepoint(mouse_pos):
                  game_started = True

           elif not game_over:
              for g in garlics[:]:
                   if g["rect"].inflate(20, 20).collidepoint(mouse_pos):
                       garlics.remove(g)
                       score += 1
                       break

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_r and game_over:
                score = 0
                lives = 3
                garlics.clear()
                spawn_timer = 0
                game_over = False

    # ---------------- TIME ----------------
    time = pygame.time.get_ticks()

    # ---------------- GAME UPDATE ----------------
    if game_started and not game_over:

        # Spawn garlics
        spawn_timer += 1

        if spawn_timer >= spawn_delay:
            spawn_garlic()
            spawn_timer = 0


        garlic_speed = min(1 + score * 0.05, 4)
        spawn_delay = max(75 - (score // 5) * 5, 30)

        # Move garlics
        for g in garlics[:]:

            dx = vampire_rect.centerx - g["x"]
            dy = vampire_rect.centery - g["y"]
            distance = math.hypot(dx, dy)

            if distance > 0:
                g["x"] += (dx / distance) * garlic_speed
                g["y"] += (dy / distance) * garlic_speed

            g["rect"].center = (round(g["x"]), round(g["y"]))

            # Garlic reaches vampire
            if g["rect"].colliderect(vampire_rect):
                garlics.remove(g)
                lives -= 1

                if lives <= 0:
                    lives = 0

                    if score > high_score:
                        high_score = score
                        save_highscore(high_score)

                    game_over = True
                    break

        # Vampire idle movement
        vampire_rect.centery = (
            vampire_base_y + int(math.sin(time * 0.003) * 5)
        )


    # ---------------- DRAW ----------------

    if not game_started:
        # Main menu
        screen.blit(
            start_background,
            (start_bg_x, start_bg_y)
        )

    else:
        # Gameplay background and vampire
        screen.blit(background, (bg_x, bg_y))
        screen.blit(vampire, vampire_rect)

        # HUD panel: keeps the score readable
        hud = pygame.Surface((190, 76), pygame.SRCALPHA)
        hud.fill((35, 12, 65, 190))
        screen.blit(hud, (12, 12))

        # Score is freshly rendered every frame
        score_text = font.render(
            f"SCORE: {score}",
            True,
            (255, 230, 245)
        )
        screen.blit(score_text, (22, 20))

        # Three heart slots; filled hearts represent remaining lives
        for i in range(3):
            heart_x = 22 + i * 34
            heart_y = 53

            if i < lives:
                screen.blit(heart, (heart_x, heart_y))
            else:
                # Darkened heart for a lost life
                lost_heart = heart.copy()
                lost_heart.fill(
                    (75, 45, 75),
                    special_flags=pygame.BLEND_RGB_MULT
                )
                screen.blit(lost_heart, (heart_x, heart_y))

        # Garlics
        for g in garlics:
            screen.blit(garlic, g["rect"])

        # ---------------- GAME OVER ----------------
        if game_over:
            overlay = pygame.Surface(
                (WIDTH, HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((35, 0, 60, 190))
            screen.blit(overlay, (0, 0))

            title_font = pygame.font.Font(
                "assets/HomeVideo-Bold.ttf", 38
            )

            title = title_font.render(
                "GAME OVER", True, (255, 220, 245)
            )
            final_score = small_font.render(
                f"Score: {score}", True, (255, 220, 245)
            )
            best_score = small_font.render(
                f"Best: {high_score}", True, (255, 220, 245)
            )
            restart_text = small_font.render(
                "Press R to Restart", True, (255, 255, 255)
            )
            quit_text = small_font.render(
                "ESC to Quit", True, (255, 255, 255)
            )

            screen.blit(
                title,
                title.get_rect(
                    center=(WIDTH // 2, HEIGHT // 2 - 75)
                )
            )
            screen.blit(
                final_score,
                final_score.get_rect(
                    center=(WIDTH // 2, HEIGHT // 2 - 25)
                )
            )
            screen.blit(
                best_score,
                best_score.get_rect(
                    center=(WIDTH // 2, HEIGHT // 2 + 10)
                )
            )
            screen.blit(
                restart_text,
                restart_text.get_rect(
                    center=(WIDTH // 2, HEIGHT // 2 + 55)
                )
            )
            screen.blit(
                quit_text,
                quit_text.get_rect(
                    center=(WIDTH // 2, HEIGHT // 2 + 90)
                )
            )


    

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
