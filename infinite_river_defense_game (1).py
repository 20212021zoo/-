import pygame
import random
import math

pygame.init()

# Screen settings
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Infinite River Defense Game")

# Colors
BLACK = (0, 0, 0)
RED = (200, 0, 0)
LIGHT_BLUE = (100, 100, 255)  # 河流浅蓝
background_color = (255, 0, 255)
MOUNTAIN_COLOR = (90, 70, 60)
background_color = DIGITAL_PINK

# Fonts
font_big = pygame.font.SysFont(None, 72)

# Settings
player_radius = 5
breathing_speed = 0.02
grid_size = 40
river_width = 20
max_distance_from_river = 100
max_time_away = 5.0
max_tributary_level = 2

class Mountain:
    def __init__(self, start_pos):
        self.points = [start_pos]
        self.generate_path()

    def generate_path(self):
        length = random.randint(40, 80)
        angle = random.uniform(0, 2 * math.pi)
        segments = random.randint(4, 7)
        for _ in range(segments):
            last_x, last_y = self.points[-1]
            dx = length / segments * math.cos(angle + random.uniform(-0.3, 0.3))
            dy = length / segments * math.sin(angle + random.uniform(-0.3, 0.3))
            self.points.append((last_x + dx, last_y + dy))

    def draw(self, surface, offset_x, offset_y):
        for i in range(1, len(self.points)):
            start = (self.points[i-1][0] - offset_x, self.points[i-1][1] - offset_y)
            end = (self.points[i][0] - offset_x, self.points[i][1] - offset_y)
            pygame.draw.line(surface, MOUNTAIN_COLOR, start, end, 3)

class River:
    def __init__(self, start_pos, angle, level=0):
        self.points = [start_pos]
        self.angle = angle
        self.level = level
        self.generate_points()
        self.tributaries = self.generate_tributaries()

    def generate_points(self, num_points=100):
        for _ in range(num_points):
            x, y = self.points[-1]
            x += grid_size // 2 * math.cos(self.angle)
            y += grid_size // 2 * math.sin(self.angle)
            self.angle += random.uniform(-0.3, 0.3)
            self.points.append((x, y))

    def generate_tributaries(self):
        tributaries = []
        if self.level < max_tributary_level:
            for i in range(10, len(self.points), 25):
                if random.random() < 0.3:
                    angle = random.uniform(0, 2 * math.pi)
                    tributaries.append(River(self.points[i], angle, self.level + 1))
        return tributaries

    def extend_river(self, offset_x, screen_width):
        while self.points[-1][0] - offset_x < screen_width + grid_size:
            self.generate_points(10)

    def draw(self, offset_x, offset_y):
        for i in range(1, len(self.points)):
            start_pos = (self.points[i - 1][0] - offset_x, self.points[i - 1][1] - offset_y)
            end_pos = (self.points[i][0] - offset_x, self.points[i][1] - offset_y)
            pygame.draw.line(screen, LIGHT_BLUE, start_pos, end_pos, river_width // (self.level + 1))
        for tributary in self.tributaries:
            tributary.extend_river(offset_x, screen_width)
            tributary.draw(offset_x, offset_y)

def collect_all_river_points(river):
    all_points = list(river.points)
    for t in river.tributaries:
        all_points.extend(collect_all_river_points(t))
    return all_points

def get_distance_to_closest_river_point(player_pos, river_points, offset_x, offset_y):
    min_dist = float('inf')
    for point in river_points:
        dx = point[0] - (offset_x + player_pos[0])
        dy = point[1] - (offset_y + player_pos[1])
        dist = math.hypot(dx, dy)
        if dist < min_dist:
            min_dist = dist
    return min_dist

def draw_player(breath_phase, player_pos):
    radius = player_radius + 2 * math.sin(breath_phase)
    pygame.draw.circle(screen, BLACK, player_pos, int(radius))

def draw_background(offset_x, offset_y, main_river):
    for x in range(-offset_x % grid_size, screen_width, grid_size):
        pygame.draw.line(screen, BLACK, (x, 0), (x, screen_height))
    for y in range(-offset_y % grid_size, screen_height, grid_size):
        pygame.draw.line(screen, BLACK, (0, y), (screen_width, y))
    main_river.extend_river(offset_x, screen_width)
    main_river.draw(offset_x, offset_y)

def draw_game_over():
    text = font_big.render("GAME OVER", True, RED)
    rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(text, rect)

def generate_mountains_around(offset_x, offset_y, seen_chunks, mountain_list):
    chunk_range = 3
    for i in range(-chunk_range, chunk_range + 1):
        for j in range(-chunk_range, chunk_range + 1):
            cx = (offset_x // 200) + i
            cy = (offset_y // 200) + j
            key = (cx, cy)
            if key not in seen_chunks:
                seen_chunks.add(key)
                for _ in range(random.randint(1, 3)):
                    mx = cx * 200 + random.randint(-50, 50)
                    my = cy * 200 + random.randint(-50, 50)
                    mountain_list.append(Mountain((mx, my)))

def reset_game():
    return {
        "offset_x": 0,
        "offset_y": 0,
        "breath_phase": 0,
        "time_away": 0,
        "main_river": River((0, screen_height // 2), 0),
        "game_over": False,
        "mountains": [],
        "seen_chunks": set(),
    }

# Main
player_pos = [screen_width // 2, screen_height // 2]
game = reset_game()
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(30) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game["game_over"] and event.type == pygame.KEYDOWN:
            game = reset_game()

    keys = pygame.key.get_pressed()
    if not game["game_over"]:
        if keys[pygame.K_LEFT]: game["offset_x"] -= 5
        if keys[pygame.K_RIGHT]: game["offset_x"] += 5
        if keys[pygame.K_UP]: game["offset_y"] -= 5
        if keys[pygame.K_DOWN]: game["offset_y"] += 5

    game["breath_phase"] += breathing_speed
    screen.fill(background_color)

    if not game["game_over"]:
        draw_background(game["offset_x"], game["offset_y"], game["main_river"])

        generate_mountains_around(game["offset_x"], game["offset_y"], game["seen_chunks"], game["mountains"])
        for m in game["mountains"]:
            m.draw(screen, game["offset_x"], game["offset_y"])

        draw_player(game["breath_phase"], player_pos)

        all_points = collect_all_river_points(game["main_river"])
        distance = get_distance_to_closest_river_point(player_pos, all_points, game["offset_x"], game["offset_y"])
        game["time_away"] = game["time_away"] + dt if distance > max_distance_from_river else 0
        if game["time_away"] > max_time_away:
            game["game_over"] = True
    else:
        draw_game_over()

    pygame.display.flip()

pygame.quit()