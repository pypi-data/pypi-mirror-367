import pygame
import random
import math
import os

swoosh_played = False

pygame.init()
pygame.mixer.init()

try:
    swoosh = pygame.mixer.Sound("src/mohamedboualamallah/fruit_ninja/assets/swoosh.mp3")
    cut = pygame.mixer.Sound("src/mohamedboualamallah/fruit_ninja/assets/fruit_cut.mp3")
except pygame.error as e:
    print(f"Error loading sound files: {e}")
    swoosh = None
    cut = None

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Ninja")
bg_image = pygame.image.load(os.path.join("src/mohamedboualamallah/fruit_ninja/assets", "woodbg.jpg"))
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
vignette = pygame.image.load(os.path.join("src/mohamedboualamallah/fruit_ninja/assets", "vignette.png")).convert_alpha()
vignette = pygame.transform.scale(vignette, (WIDTH, HEIGHT))

bomb_image = pygame.image.load(os.path.join("src/mohamedboualamallah/fruit_ninja/assets", "bomb.png"))
bomb_image = pygame.transform.scale(bomb_image, (96, 96))

heart_image = pygame.image.load(os.path.join("src/mohamedboualamallah/fruit_ninja/assets", "heart.png"))
heart_image = pygame.transform.scale(heart_image, (32, 32))  # Resize heart icon

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (30, 30, 30)
RED = (255, 50, 50)

# Fonts
title_font = pygame.font.SysFont("Poppins", 72)
menu_font = pygame.font.SysFont("Poppins", 36)
score_font = pygame.font.SysFont("Poppins", 36)
combo_font = pygame.font.SysFont("Poppins", 48)
floating_text_font = pygame.font.SysFont("Poppins", 28)

# Load fruit images (make sure your fruit images are named fruit1.png ... fruit9.png)
fruit_images = [pygame.image.load(os.path.join("src/mohamedboualamallah/fruit_ninja/assets/fruits", f"fruit{i}.png")) for i in range(1, 10)]
fruit_images = [pygame.transform.scale(img, (96, 96)) for img in fruit_images]





# Slash trail settings
MAX_TRAIL = 12
trail = []

# Screen shake variables
shake_magnitude = 0
shake_duration = 0

def get_shake_offset():
    if shake_duration > 0:
        return (random.randint(-shake_magnitude, shake_magnitude), random.randint(-shake_magnitude, shake_magnitude))
    return (0, 0)

class Particle:
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.radius = random.randint(2, 5)
        self.color = color if color else random.choice([(255, 50, 50), (255, 100, 0), (255, 200, 0)])
        self.vel_x = random.uniform(-5, 5)
        self.vel_y = random.uniform(-5, 5)
        self.life = random.randint(20, 40)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# Floating text for +x points
class FloatingText:
    def __init__(self, text, x, y, color=WHITE, lifetime=60):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.alpha = 255
        self.dy = -1  # floats upward

    def update(self):
        self.y += self.dy
        self.lifetime -= 1
        self.alpha = max(0, int(255 * (self.lifetime / 60)))

    def draw(self, surface):
        text_surf = floating_text_font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        surface.blit(text_surf, (self.x, self.y))

# Fruit class
class Fruit:
    def __init__(self):
        self.is_bomb = random.random() < 0.1  # 10% chance
        self.image = bomb_image if self.is_bomb else random.choice(fruit_images)
        self.x = random.randint(100, WIDTH - 100)
        self.y = HEIGHT + random.randint(50, 150)
        self.speed_y = random.uniform(-18, -24)
        self.speed_x = random.uniform(-4, 4)
        self.gravity = 0.6
        self.sliced = False
        self.has_entered_screen = False  # New flag

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity

        # Mark as entered screen if crossed top 80% height
        if not self.has_entered_screen and self.y <= 0.8 * HEIGHT:
            self.has_entered_screen = True

    def draw(self, surface):
        shadow_color = (0, 0, 0, 120)
        shadow_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, shadow_color, [10, 48, 44, 16])
        screen.blit(shadow_surface, (int(self.x), int(self.y)))
        surface.blit(self.image, (int(self.x), int(self.y)))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 64, 64)

# Fruit halves for animation
class FruitHalf:
    def __init__(self, image, x, y, dx, dy, angle_speed):
        self.original_image = pygame.transform.scale(image, (32, 64))
        self.image = self.original_image
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.angle = 0
        self.angle_speed = angle_speed
        self.gravity = 0.6

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity
        self.angle += self.angle_speed
        self.image = pygame.transform.rotate(self.original_image, self.angle)

    def draw(self, surface):
        shadow_color = (0, 0, 0, 120)
        shadow_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, shadow_color, [10, 48, 44, 16])
        screen.blit(shadow_surface, (int(self.x), int(self.y)))
        rect = self.image.get_rect(center=(self.x, self.y))
        surface.blit(self.image, rect)

# Main menu with better visuals
def main_menu():
    menu = True
    angle = 0
    while menu:
        screen.fill(BLACK)
        # Rotating title effect
        rotated_title = pygame.transform.rotate(title_font.render("Fruit Ninja", True, WHITE), angle)
        rect = rotated_title.get_rect(center=(WIDTH // 2, 150))
        screen.blit(rotated_title, rect)

        play_text = menu_font.render("Press SPACE to Play", True, WHITE)
        screen.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2, 300))

        # Simple glowing effect for play text
        glow_alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.005))
        glow_surface = menu_font.render("Press SPACE to Play", True, (255, 255, 255, glow_alpha))
        glow_surface.set_alpha(glow_alpha)
        screen.blit(glow_surface, (WIDTH // 2 - glow_surface.get_width() // 2, 300))

        angle = (angle + 1) % 360

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                menu = False

# Line-fruit collision
def line_intersects_fruit(p1, p2, fruit_rect):
    return fruit_rect.clipline(p1, p2)

# Draw slash trail
def draw_trail(trail):
    if len(trail) < 2:
        return
    for i in range(len(trail) - 1):
        alpha = int(255 * (1 - i / len(trail)))
        color = (255, 255, 255, alpha)
        pygame.draw.line(screen, color[:3], trail[i], trail[i + 1], 4)

particles = []

def draw_lives(lives):
    for i in range(lives):
        x = WIDTH - (i + 1) * (heart_image.get_width() + 10) - 10
        y = 10
        screen.blit(heart_image, (x, y))

# Game loop


def game_loop():
    fruit_particle_colors = [
        (220, 20, 60),    # Fruit 1: red apple - crimson red
        (255, 255, 102),  # Fruit 2: banana - bright yellow
        (50, 205, 50),    # Fruit 3: lime - lime green
        (255, 20, 147),   # Fruit 4: dragonfruit - deep pink
        (255, 255, 153),  # Fruit 5: lemon - pale yellow
        (255, 140, 0),    # Fruit 6: orange - dark orange
        (144, 238, 144),  # Fruit 7: pear - light green
        (199, 21, 133),   # Fruit 8: raspberry - medium violet red
        (255, 215, 0),    # Fruit 9: pineapple - gold
    ]

    global swoosh_played, shake_magnitude, shake_duration

    clock = pygame.time.Clock()
    fruits = []
    halves = []
    floating_texts = []

    score = 0
    lives = 5  # Added 5 lives
    spawn_timer = 0
    running = True

    combo_count = 0
    combo_timer = 0
    COMBO_RESET_TIME = 60  # 1 second at 60fps

    while running:
        clock.tick(60)

        # Update screen shake timer
        if shake_duration > 0:
            shake_duration -= 1
        else:
            shake_magnitude = 0

        shake_offset = get_shake_offset()

        screen.blit(bg_image, shake_offset)

        # Spawn fruits more often
        spawn_timer += 1
        if spawn_timer > 15:
            fruits.append(Fruit())
            spawn_timer = 0

        # Move and draw fruits
        for fruit in fruits[:]:
            fruit.move()
            fruit.draw(screen)

            if fruit.y > HEIGHT + 50:
                if not fruit.sliced and not fruit.is_bomb and fruit.has_entered_screen:
                    lives -= 1
                    if lives <= 0:
                        main_menu()
                        # reset game state as needed here
                        score = 0
                        lives = 5
                        fruits.clear()
                        halves.clear()
                        floating_texts.clear()
                        trail.clear()
                        combo_count = 0
                        combo_timer = 0
                fruits.remove(fruit)
            elif fruit.sliced:
                fruits.remove(fruit)

        # Update and draw particles
        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.life <= 0:
                particles.remove(particle)

        # Slash trail update with swoosh control
        mouse_held = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()

        if mouse_held:
            trail.append(mouse_pos)
            if len(trail) > MAX_TRAIL:
                trail.pop(0)
            if not swoosh_played:
                swoosh_played = True
                if swoosh:
                    swoosh.play()
        else:
            trail.clear()
            swoosh_played = False

        # Slash collision
        if len(trail) >= 2:
            for fruit in fruits:
                if not fruit.sliced:
                    for i in range(len(trail) - 1):
                        if line_intersects_fruit(trail[i], trail[i + 1], fruit.get_rect()):
                            fruit.sliced = True
                            if cut:
                                cut.play(0)  # play cut sound

                            if fruit.is_bomb:
                                floating_texts.append(FloatingText("BOOM!", fruit.x, fruit.y, RED))
                                lives -= 1
                                shake_magnitude = 20
                                shake_duration = 30

                                # Add explosion particles (default color)
                                for _ in range(60):
                                    particles.append(Particle(fruit.x + 32, fruit.y + 32))

                                lives -= 1
                                if lives <= 0:
                                    main_menu()
                                    score = 0
                                    lives = 5
                                    fruits.clear()
                                    halves.clear()
                                    floating_texts.clear()
                                    trail.clear()
                                    combo_count = 0
                                    combo_timer = 0
                                break  # Stop checking other fruits this frame

                            else:
                                # Find index of fruit image
                                try:
                                    fruit_index = fruit_images.index(fruit.image)
                                except ValueError:
                                    fruit_index = 0

                                color = fruit_particle_colors[fruit_index]

                                # Create colored particles based on fruit
                                for _ in range(20):
                                    particles.append(Particle(fruit.x + 32, fruit.y + 32, color))

                            # Combo logic
                            if combo_timer > 0:
                                combo_count += 1
                            else:
                                combo_count = 1  # start combo

                            combo_timer = COMBO_RESET_TIME

                            # Update score and floating text
                            points = 3 * combo_count
                            score += points
                            floating_texts.append(FloatingText(f"+{points}", fruit.x, fruit.y, WHITE))

                            # Screen shake on slice
                            shake_magnitude = 5
                            shake_duration = 10

                            # Create fruit halves animation
                            img = fruit.image
                            halves.append(FruitHalf(img, fruit.x + 16, fruit.y + 32, -3, -5, -5))
                            halves.append(FruitHalf(img, fruit.x + 48, fruit.y + 32, 3, -5, 5))
                            break

        # Update and draw fruit halves
        for half in halves[:]:
            half.update()
            half.draw(screen)
            if half.y > HEIGHT:
                halves.remove(half)

        # Update combo timer
        if combo_timer > 0:
            combo_timer -= 1
        else:
            combo_count = 0  # reset combo

        # Update and draw floating texts
        for text in floating_texts[:]:
            text.update()
            if text.lifetime <= 0:
                floating_texts.remove(text)

        for text in floating_texts:
            text.draw(screen)

        # Draw slash trail
        draw_trail(trail)

        # Draw combo counter with shake effect
        if combo_count > 1:
            shake_x = random.randint(-3, 3)
            shake_y = random.randint(-3, 3)
            combo_render = combo_font.render(f"Combo x{combo_count}", True, RED)
            screen.blit(combo_render, (WIDTH - combo_render.get_width() - 30 + shake_x, 30 + shake_y))

        # Draw score
        score_text = score_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Draw lives hearts
        draw_lives(lives)

        # Vignette overlay (optional)
        # screen.blit(vignette, (0, 0))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()

    pygame.quit()

# Run the game

def main():

    main_menu()
    game_loop()


main()