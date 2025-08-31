import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Car Racing Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Game variables
clock = pygame.time.Clock()
FPS = 60
score = 0
high_score = 0
game_over = False
game_started = False
road_speed = 5
road_w = 400
road_x = (WIDTH - road_w) // 2
roadmark_w = 10
left_edge = road_x
right_edge = road_x + road_w

# Load sounds
try:
    engine_sound = pygame.mixer.Sound("engine.wav")
    crash_sound = pygame.mixer.Sound("crash.wav")
    collect_sound = pygame.mixer.Sound("collect.wav")
    # Set volume for sounds
    engine_sound.set_volume(0.5)
    crash_sound.set_volume(0.7)
    collect_sound.set_volume(0.5)
except:
    # Create placeholder sounds if files aren't available
    engine_sound = pygame.mixer.Sound(pygame.sndarray.array([0] * 44100))
    crash_sound = pygame.mixer.Sound(pygame.sndarray.array([0] * 44100))
    collect_sound = pygame.mixer.Sound(pygame.sndarray.array([0] * 44100))

# Player car
class Car:
    def __init__(self):
        self.width = 50
        self.height = 80
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 100
        self.speed = 8
        self.color = RED
        self.shield_active = False
        self.shield_time = 0
        self.boost_active = False
        self.boost_time = 0
        self.slow_active = False
        self.slow_time = 0
        
    def draw(self):
        # Draw shield if active
        if self.shield_active:
            shield_radius = max(self.width, self.height) + 10
            current_time = pygame.time.get_ticks()
            pulse = math.sin(current_time * 0.01) * 3 + shield_radius
            pygame.draw.circle(screen, CYAN, (self.x + self.width//2, self.y + self.height//2), int(pulse), 3)
        
        # Car body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Windows
        pygame.draw.rect(screen, BLUE, (self.x + 5, self.y + 5, self.width - 10, 15))
        pygame.draw.rect(screen, BLUE, (self.x + 5, self.y + 30, self.width - 10, 15))
        # Wheels
        pygame.draw.rect(screen, BLACK, (self.x - 5, self.y + 10, 5, 15))
        pygame.draw.rect(screen, BLACK, (self.x + self.width, self.y + 10, 5, 15))
        pygame.draw.rect(screen, BLACK, (self.x - 5, self.y + self.height - 25, 5, 15))
        pygame.draw.rect(screen, BLACK, (self.x + self.width, self.y + self.height - 25, 5, 15))
        
        # Draw boost effect if active
        if self.boost_active:
            for i in range(5):
                pygame.draw.rect(screen, ORANGE, 
                                (self.x + self.width//2 - 2, 
                                 self.y + self.height + i*5, 
                                 4, 10))
    
    def move(self, direction):
        if direction == "left" and self.x > left_edge + 10:
            self.x -= self.speed
        if direction == "right" and self.x < right_edge - self.width - 10:
            self.x += self.speed
            
    def update_powerups(self):
        current_time = pygame.time.get_ticks()
        if self.shield_active and current_time - self.shield_time > 5000:  # 5 seconds
            self.shield_active = False
        if self.boost_active and current_time - self.boost_time > 3000:  # 3 seconds
            self.boost_active = False
            self.speed = 8
        if self.slow_active and current_time - self.slow_time > 4000:  # 4 seconds
            self.slow_active = False

# Obstacle cars
class Obstacle:
    def __init__(self):
        self.width = 50
        self.height = 80
        self.x = random.randint(left_edge + 10, right_edge - self.width - 10)
        self.y = -self.height
        self.speed = random.randint(3, 7)
        self.color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Windows
        pygame.draw.rect(screen, BLUE, (self.x + 5, self.y + 5, self.width - 10, 15))
        pygame.draw.rect(screen, BLUE, (self.x + 5, self.y + 30, self.width - 10, 15))
        # Wheels
        pygame.draw.rect(screen, BLACK, (self.x - 5, self.y + 10, 5, 15))
        pygame.draw.rect(screen, BLACK, (self.x + self.width, self.y + 10, 5, 15))
        pygame.draw.rect(screen, BLACK, (self.x - 5, self.y + self.height - 25, 5, 15))
        pygame.draw.rect(screen, BLACK, (self.x + self.width, self.y + self.height - 25, 5, 15))
    
    def move(self, slow_mode=False):
        actual_speed = self.speed * 0.5 if slow_mode else self.speed
        self.y += actual_speed
        return self.y > HEIGHT

# Power-up class
class PowerUp:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = random.randint(left_edge + 10, right_edge - self.width - 10)
        self.y = -self.height
        self.speed = 5
        self.type = random.choice(["shield", "boost", "slow"])
        self.colors = {"shield": CYAN, "boost": ORANGE, "slow": PURPLE}
        
    def draw(self):
        pygame.draw.rect(screen, self.colors[self.type], (self.x, self.y, self.width, self.height))
        # Draw symbol based on type
        if self.type == "shield":
            pygame.draw.circle(screen, WHITE, (self.x + self.width//2, self.y + self.height//2), 10, 2)
        elif self.type == "boost":
            points = [(self.x + 5, self.y + 20), (self.x + self.width//2, self.y + 5), 
                     (self.x + self.width - 5, self.y + 20)]
            pygame.draw.polygon(screen, WHITE, points)
        else:  # slow
            pygame.draw.circle(screen, WHITE, (self.x + self.width//2, self.y + self.height//2), 12, 2)
            pygame.draw.line(screen, WHITE, (self.x + 5, self.y + self.height//2), 
                            (self.x + self.width - 5, self.y + self.height//2), 2)
    
    def move(self):
        self.y += self.speed
        return self.y > HEIGHT

# Road marks
class RoadMark:
    def __init__(self, y):
        self.x = road_x + road_w // 2 - roadmark_w // 2
        self.y = y
        self.width = roadmark_w
        self.height = 50
    
    def draw(self):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
    
    def move(self, boost_mode=False):
        actual_speed = road_speed * 2 if boost_mode else road_speed
        self.y += actual_speed
        if self.y > HEIGHT:
            self.y = -self.height
            return True
        return False

# Particle effect system
class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_explosion(self, x, y):
        for i in range(20):
            self.particles.append({
                "x": x, 
                "y": y,
                "vx": random.uniform(-3, 3),
                "vy": random.uniform(-3, 3),
                "life": random.uniform(0.5, 1.5),
                "color": random.choice([RED, ORANGE, YELLOW])
            })
            
    def update(self):
        for particle in self.particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["life"] -= 0.016  # Subtract frame time
            
        self.particles = [p for p in self.particles if p["life"] > 0]
        
    def draw(self):
        for particle in self.particles:
            alpha = int(255 * (particle["life"] / 1.5))
            color = list(particle["color"])
            if len(color) == 3:
                color.append(alpha)
            pygame.draw.circle(screen, color, (int(particle["x"]), int(particle["y"])), 3)

# Create game objects
player = Car()
obstacles = []
power_ups = []
road_marks = []
particle_system = ParticleSystem()

for i in range(5):
    road_marks.append(RoadMark(i * 100))

# Game state variables
obstacle_timer = 0
power_up_timer = 0
level = 1
score_to_next_level = 20
game_paused = False

# Font setup
font_small = pygame.font.SysFont(None, 28)
font_medium = pygame.font.SysFont(None, 36)
font_large = pygame.font.SysFont(None, 72)

# Draw button function
def draw_button(x, y, width, height, text, color, hover_color, action=None):
    mouse_pos = pygame.mouse.get_pos()
    clicked = pygame.mouse.get_pressed()[0]
    
    if x < mouse_pos[0] < x + width and y < mouse_pos[1] < y + height:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))
        if clicked and action is not None:
            action()
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))
        
    pygame.draw.rect(screen, WHITE, (x, y, width, height), 2)
    text_surf = font_medium.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(x + width/2, y + height/2))
    screen.blit(text_surf, text_rect)

# Menu functions
def start_game():
    global game_started, game_over, score, obstacles, power_ups, level, score_to_next_level
    game_started = True
    game_over = False
    score = 0
    obstacles = []
    power_ups = []
    level = 1
    score_to_next_level = 20
    player.x = WIDTH // 2 - player.width // 2
    player.y = HEIGHT - 100
    player.shield_active = False
    player.boost_active = False
    player.slow_active = False

def quit_game():
    pygame.quit()
    sys.exit()

# Main game loop
running = True
while running:
    clock.tick(FPS)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                start_game()
            if event.key == pygame.K_p and game_started and not game_over:
                game_paused = not game_paused
            if event.key == pygame.K_ESCAPE:
                if game_paused or game_over:
                    game_started = False
                    game_paused = False
                else:
                    game_paused = True
    
    if not game_started:
        # Main menu screen
        screen.fill(DARK_GRAY)
        
        # Title
        title_text = font_large.render("RACING EXTREME", True, RED)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
        
        # Buttons
        draw_button(WIDTH//2 - 100, 250, 200, 50, "Start Game", GREEN, (0, 150, 0), start_game)
        draw_button(WIDTH//2 - 100, 320, 200, 50, "Quit", RED, (150, 0, 0), quit_game)
        
        # Instructions
        instr_text = font_small.render("Use arrow keys to control the car. Avoid obstacles and collect power-ups!", True, WHITE)
        screen.blit(instr_text, (WIDTH//2 - instr_text.get_width()//2, 400))
        
        powerup_text = font_small.render("Power-ups: Cyan=Shield, Orange=Boost, Purple=Slow", True, WHITE)
        screen.blit(powerup_text, (WIDTH//2 - powerup_text.get_width()//2, 430))
        
        # High score
        high_score_text = font_medium.render(f"High Score: {high_score}", True, YELLOW)
        screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, 480))
        
        pygame.display.update()
        continue
        
    if game_paused:
        # Pause screen
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        pause_text = font_large.render("GAME PAUSED", True, WHITE)
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
        
        continue_text = font_medium.render("Press P to continue or ESC for main menu", True, WHITE)
        screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 20))
        
        pygame.display.update()
        continue
    
    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move("left")
        if keys[pygame.K_RIGHT]:
            player.move("right")
        
        # Update power-up timers
        player.update_powerups()
        
        # Create new obstacles
        obstacle_timer += 1
        if obstacle_timer > 60 - min(level * 5, 40):  # Faster spawning with higher levels
            obstacles.append(Obstacle())
            obstacle_timer = 0
        
        # Create power-ups
        power_up_timer += 1
        if power_up_timer > 300:  # Every 5 seconds at 60 FPS
            if random.random() < 0.3:  # 30% chance to spawn a power-up
                power_ups.append(PowerUp())
            power_up_timer = 0
        
        # Move obstacles
        for obstacle in obstacles[:]:
            if obstacle.move(player.slow_active):
                obstacles.remove(obstacle)
                score += 1
        
        # Move power-ups
        for power_up in power_ups[:]:
            if power_up.move():
                power_ups.remove(power_up)
        
        # Move road marks
        for mark in road_marks:
            mark.move(player.boost_active)
        
        # Check for level up
        if score >= score_to_next_level:
            level += 1
            score_to_next_level += level * 15
            road_speed += 0.5  # Increase difficulty
        
        # Collision detection with obstacles
        for obstacle in obstacles[:]:
            if (player.x < obstacle.x + obstacle.width and
                player.x + player.width > obstacle.x and
                player.y < obstacle.y + obstacle.height and
                player.y + player.height > obstacle.y):
                
                if player.shield_active:
                    obstacles.remove(obstacle)
                    particle_system.add_explosion(obstacle.x + obstacle.width//2, 
                                                 obstacle.y + obstacle.height//2)
                    collect_sound.play()
                else:
                    crash_sound.play()
                    game_over = True
                    if score > high_score:
                        high_score = score
                    break
        
        # Collision detection with power-ups
        for power_up in power_ups[:]:
            if (player.x < power_up.x + power_up.width and
                player.x + player.width > power_up.x and
                player.y < power_up.y + power_up.height and
                player.y + player.height > power_up.y):
                
                collect_sound.play()
                if power_up.type == "shield":
                    player.shield_active = True
                    player.shield_time = pygame.time.get_ticks()
                elif power_up.type == "boost":
                    player.boost_active = True
                    player.boost_time = pygame.time.get_ticks()
                    player.speed = 12
                elif power_up.type == "slow":
                    player.slow_active = True
                    player.slow_time = pygame.time.get_ticks()
                
                power_ups.remove(power_up)
    
    # Drawing
    screen.fill(GREEN)  # Grass
    
    # Road
    pygame.draw.rect(screen, GRAY, (road_x, 0, road_w, HEIGHT))
    
    # Road edges
    pygame.draw.rect(screen, YELLOW, (road_x, 0, roadmark_w, HEIGHT))
    pygame.draw.rect(screen, YELLOW, (road_x + road_w - roadmark_w, 0, roadmark_w, HEIGHT))
    
    # Road marks
    for mark in road_marks:
        mark.draw()
    
    # Draw player, obstacles, and power-ups
    for obstacle in obstacles:
        obstacle.draw()
    
    for power_up in power_ups:
        power_up.draw()
    
    player.draw()
    
    # Draw particles
    particle_system.update()
    particle_system.draw()
    
    # Score and level display
    score_text = font_medium.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    level_text = font_medium.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (10, 50))
    
    # Next level progress
    progress_width = 200
    progress_fill = (score / score_to_next_level) * progress_width
    pygame.draw.rect(screen, DARK_GRAY, (WIDTH - progress_width - 10, 10, progress_width, 20))
    pygame.draw.rect(screen, BLUE, (WIDTH - progress_width - 10, 10, progress_fill, 20))
    pygame.draw.rect(screen, WHITE, (WIDTH - progress_width - 10, 10, progress_width, 20), 2)
    
    next_level_text = font_small.render(f"Next: {score_to_next_level}", True, WHITE)
    screen.blit(next_level_text, (WIDTH - progress_width - 10, 35))
    
    # Active power-ups display
    powerup_y = 90
    if player.shield_active:
        shield_text = font_small.render("Shield Active", True, CYAN)
        screen.blit(shield_text, (10, powerup_y))
        powerup_y += 25
    
    if player.boost_active:
        boost_text = font_small.render("Boost Active", True, ORANGE)
        screen.blit(boost_text, (10, powerup_y))
        powerup_y += 25
    
    if player.slow_active:
        slow_text = font_small.render("Slow Active", True, PURPLE)
        screen.blit(slow_text, (10, powerup_y))
    
    # Game over display
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        game_over_text = font_large.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        
        final_score_text = font_medium.render(f"Score: {score}", True, WHITE)
        screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2 + 10))
        
        high_score_text = font_medium.render(f"High Score: {high_score}", True, YELLOW)
        screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 50))
        
        restart_text = font_medium.render("Press R to restart or ESC for main menu", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 100))
    
    pygame.display.update()

pygame.quit()
sys.exit()