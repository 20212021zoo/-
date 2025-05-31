import pygame
import math

# 初始化
pygame.init()
width, height = 1200, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
pygame.display.set_caption("Floating Bio-CAD Organism with Separated Tentacles")

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 坐标转换函数
def transform(x, y):
    screen_x = int(width / 2 + x * 40)
    screen_y = int(height / 2 - y * 40)
    return screen_x, screen_y

# 帆状结构（顶部振动）
def draw_sail(x_offset, t):
    h = 5 + 0.5 * math.sin(t + x_offset)
    points = []
    for i in range(4):
        angle = math.pi / 2 + i * math.pi / 1.5
        r = 0.6 if i % 2 == 0 else 0.3
        dx = r * math.cos(angle)
        dy = r * math.sin(angle)
        px, py = transform(x_offset + dx, 2.2 + h * dy)
        points.append((px, py))
    pygame.draw.polygon(screen, BLACK, points, 1)

# 弯曲触手（偏下、避免遮挡）
def draw_soft_tentacle(base_x, offset, t, dy_float):
    tx = base_x + offset
    y_offset = -2.60  # ✅ 让弯曲触手整体下移，避免遮挡
    points = []
    for k in range(20):
        angle = k / 5.0
        y = y_offset - 0.1 * k + dy_float
        x_wiggle = 0.5 * math.sin(angle + t + base_x)
        sx, sy = transform(tx + x_wiggle, y)
        points.append((sx, sy))
    pygame.draw.lines(screen, BLACK, False, points, 1)
    pygame.draw.circle(screen, BLACK, points[-1], 4, 1)

# 主循环
running = True
time = 0
bubble_count = 13
sail_positions = [-6.6, -4.4, -2.2, 0, 2.2, 4.4, 6.6]

while running:
    clock.tick(30)
    screen.fill(WHITE)

    # 泡状基座
    for i in range(bubble_count):
        x = (i - bubble_count // 2) * 2.2
        bubble_rect = pygame.Rect(0, 0, 80, 48)
        bubble_rect.center = transform(x, 0)
        pygame.draw.ellipse(screen, BLACK, bubble_rect, 1)

    # 帆结构 + 中段连接体
    for x in sail_positions:
        draw_sail(x, time)
        rect = pygame.Rect(0, 0, 40, 48)
        rect.center = transform(x, 1.2)
        pygame.draw.rect(screen, BLACK, rect, 1)

    # 主触手 + 弯曲触手（动态同步，但位置下移）
    for i in range(bubble_count):
        x_base = (i - bubble_count // 2) * 2.2
        for j in range(2):
            offset = (j - 0.5) * 0.6
            tx = x_base + offset
            dy_float = -0.2 * math.sin(time + j)

            # 主触手（弯曲 + 上下浮动）
            points = []
            for k in range(20):
                theta = k / 19 * math.pi
                ty = -0.6 * math.sin(theta) - 1.2 + dy_float
                dx = 0.5 * math.sin(2 * theta)
                points.append(transform(tx + dx, ty))
            pygame.draw.lines(screen, BLACK, False, points, 1)
            pygame.draw.circle(screen, BLACK, transform(tx, -2.5 + dy_float), 4, 1)

            # 弯曲触手（整体位置偏下）
            draw_soft_tentacle(x_base, offset + 0.3, time, dy_float)

    # 尾巴结构（随时间波动）
    tail_points = []
    for i in range(100):
        x_tail = 7.5 + i * 0.055
        y_tail = -0.2 * math.sin(0.3 * x_tail + time)
        tail_points.append(transform(x_tail, y_tail))

    # 尾巴线
    pygame.draw.lines(screen, BLACK, False, tail_points, 2)

    # 尾巴圆：取尾巴最后一个点作为中心
    tail_end_pos = tail_points[-1]
    pygame.draw.ellipse(screen, BLACK, pygame.Rect(
        tail_end_pos[0] - 30, tail_end_pos[1] - 12, 60, 24), 1)

    pygame.display.flip()
    time += 0.05

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
