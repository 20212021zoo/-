import pygame
import random
import math

pygame.init()

# ---------------- Settings ----------------
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Infinite River Defense Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (200, 0, 0)


background_color = 	(255, 64, 255)
font_big = pygame.font.SysFont(None, 72)

player_radius = 5
breathing_speed = 0.02

river_width = 20
grid_size = 40
max_tributary_level = 2

max_distance_from_river = 100
max_time_away = 5.0

connection_chance = 0.04
path_length = 500
fade_time = 2.0

# ---------------- Classes ----------------
class LightPath:
    def __init__(self, start):
        self.start = start
        self.points = [start]
        self.time_alive = 0
        self.path_length = path_length  # ✅ 添加这行
        self.generate_path()

    def generate_path(self):
        current = self.start
        angle = random.uniform(0, 2 * math.pi)
        for _ in range(self.path_length):
            angle += random.uniform(-0.5, 0.5)  # 小范围偏移（越小越直）
            dx = math.cos(angle) * grid_size
            dy = math.sin(angle) * grid_size
            current = (current[0] + dx, current[1] + dy)
            self.points.append(current)

    def draw(self, surface, offset_x, offset_y, alpha):
        if len(self.points) < 2:
            return
        for i in range(1, len(self.points)):
            start = (self.points[i-1][0] - offset_x, self.points[i-1][1] - offset_y)
            end = (self.points[i][0] - offset_x, self.points[i][1] - offset_y)
            color = (BLUE[0], BLUE[1], BLUE[2], int(255 * alpha))
            pygame.draw.line(surface, color, start, end, 10)

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
            for i in range(10, len(self.points), 20):
                if random.random() < 0.3:
                    angle = random.uniform(0, 2 * math.pi)
                    tributary = River(self.points[i], angle, self.level + 1)
                    tributaries.append(tributary)
        return tributaries

    def extend_river(self, offset_x, screen_width):
        while self.points[-1][0] - offset_x < screen_width + grid_size:
            self.generate_points(10)

    def draw(self, offset_x, offset_y):
        for i in range(1, len(self.points)):
            start_pos = (self.points[i - 1][0] - offset_x, self.points[i - 1][1] - offset_y)
            end_pos = (self.points[i][0] - offset_x, self.points[i][1] - offset_y)
            pygame.draw.line(screen, BLUE, start_pos, end_pos, river_width // (self.level + 1))
        for tributary in self.tributaries:
            tributary.extend_river(offset_x, screen_width)
            tributary.draw(offset_x, offset_y)

# ---------------- Helper Functions ----------------
def collect_all_river_points(river):
    all_points = list(river.points)
    for tributary in river.tributaries:
        all_points.extend(collect_all_river_points(tributary))
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

def reset_game():
    return {
        "offset_x": 0,
        "offset_y": 0,
        "breath_phase": 0,
        "time_away": 0,
        "main_river": River((0, screen_height // 2), 0),
        "game_over": False,
        "paths": []
    }

# ---------------- Main Loop ----------------
game = reset_game()
player_pos = [screen_width // 2, screen_height // 2]
draw_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000.0
    game["breath_phase"] += breathing_speed

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

    screen.fill(background_color)
    draw_surface.fill((0, 0, 0, 0))  # Clear light path layer

    if not game["game_over"]:
        draw_background(game["offset_x"], game["offset_y"], game["main_river"])
        draw_player(game["breath_phase"], player_pos)

        # LightPath generation
        if random.random() < connection_chance:
            all_river_points = collect_all_river_points(game["main_river"])
            if all_river_points:
                spawn_point = random.choice(all_river_points)
                game["paths"].append(LightPath(spawn_point))

        # Draw & update LightPaths
        for path in game["paths"][:]:
            path.time_alive += dt
            if path.time_alive > fade_time:
                game["paths"].remove(path)
            else:
                alpha = max(0, 1 - path.time_alive / fade_time)
                path.draw(draw_surface, game["offset_x"], game["offset_y"], alpha)

        screen.blit(draw_surface, (0, 0))

        # 收集所有“河流 + 神经路径”点
        all_river_points = collect_all_river_points(game["main_river"])
        all_light_points = []
        for path in game["paths"]:
            all_light_points.extend(path.points)

        # 合并所有有效路径点
        all_points = all_river_points + all_light_points

        # 判断玩家是否离太远
        distance = get_distance_to_closest_river_point(
            player_pos, all_points, game["offset_x"], game["offset_y"]
        )

        if distance > max_distance_from_river:
            game["time_away"] += dt
        else:
            game["time_away"] = 0

        if game["time_away"] > max_time_away:
            game["game_over"] = True
    else:
        draw_game_over()

    pygame.display.flip()

pygame.quit()
