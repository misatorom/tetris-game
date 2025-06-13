import pygame
import random
import sys

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),   # I - シアン
    (0, 0, 255),     # J - 青
    (255, 165, 0),   # L - オレンジ
    (255, 255, 0),   # O - 黄色
    (0, 255, 0),     # S - 緑
    (128, 0, 128),   # T - 紫
    (255, 0, 0)      # Z - 赤
]

# ゲーム設定
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30
SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE + 200
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

# テトリミノの形状
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]   # Z
]

class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = random.randint(0, len(COLORS) - 1)
        self.rotation = 0
        self.flower_type = shape  # 形状に応じて花の種類を決定

    def get_shape(self):
        return SHAPES[self.shape]

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4

    def get_rotated_shape(self):
        shape = self.get_shape()
        for _ in range(self.rotation):
            shape = [list(row) for row in zip(*shape[::-1])]
        return shape

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.fall_time = 0
        self.fall_speed = 1000
        self.game_over = False

    def new_piece(self):
        return Tetromino(GRID_WIDTH // 2 - 1, 0, random.randint(0, len(SHAPES) - 1))

    def valid_move(self, piece, x, y):
        shape = piece.get_rotated_shape()
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = piece.x + col_idx + x
                    new_y = piece.y + row_idx + y
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True

    def lock_piece(self):
        shape = self.current_piece.get_rotated_shape()
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    y = self.current_piece.y + row_idx
                    x = self.current_piece.x + col_idx
                    if y >= 0:
                        # 色情報と花の種類を保存（上位ビットに花の種類を格納）
                        self.grid[y][x] = (self.current_piece.flower_type << 4) | (self.current_piece.color + 1)

    def clear_lines(self):
        lines_cleared = 0
        new_grid = []
        for row in self.grid:
            if all(row):
                lines_cleared += 1
            else:
                new_grid.append(row)
        
        for _ in range(lines_cleared):
            new_grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        
        self.grid = new_grid
        self.lines += lines_cleared
        self.score += lines_cleared * 100 * self.level
        self.level = min(10, 1 + self.lines // 10)
        self.fall_speed = max(100, 1000 - (self.level - 1) * 100)

    def move_piece(self, dx, dy):
        if self.valid_move(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def rotate_piece(self):
        original_rotation = self.current_piece.rotation
        self.current_piece.rotate()
        if not self.valid_move(self.current_piece, 0, 0):
            self.current_piece.rotation = original_rotation

    def drop_piece(self):
        if not self.move_piece(0, 1):
            self.lock_piece()
            self.clear_lines()
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
            if not self.valid_move(self.current_piece, 0, 0):
                self.game_over = True

    def hard_drop(self):
        while self.move_piece(0, 1):
            pass
        self.drop_piece()

def draw_tulip(screen, x, y, color, size):
    # チューリップの花びら
    points = []
    for i in range(3):
        angle = -90 + i * 40 - 20
        petal_x = x + size * 0.8 * pygame.math.Vector2(1, 0).rotate(angle).x
        petal_y = y + size * 0.8 * pygame.math.Vector2(1, 0).rotate(angle).y
        pygame.draw.ellipse(screen, color, 
                          (petal_x - size//3, petal_y - size//2, size//1.5, size), 0)
    # 中心
    pygame.draw.circle(screen, (255, 255, 200), (x, y + size//4), size // 4)

def draw_rose(screen, x, y, color, size):
    # バラの渦巻き状の花びら
    for i in range(3):
        radius = size - i * size // 4
        pygame.draw.circle(screen, color, (x, y), radius, 2)
        # 内側の花びら
        for j in range(5):
            angle = 72 * j + i * 30
            petal_x = x + radius * 0.5 * pygame.math.Vector2(1, 0).rotate(angle).x
            petal_y = y + radius * 0.5 * pygame.math.Vector2(1, 0).rotate(angle).y
            pygame.draw.circle(screen, color, (int(petal_x), int(petal_y)), radius // 3)

def draw_daisy(screen, x, y, color, size):
    # ヒナギクの花びら（細長い）
    petal_count = 8
    for i in range(petal_count):
        angle = (360 / petal_count) * i
        petal_x = x + size * 0.7 * pygame.math.Vector2(1, 0).rotate(angle).x
        petal_y = y + size * 0.7 * pygame.math.Vector2(1, 0).rotate(angle).y
        pygame.draw.ellipse(screen, WHITE, 
                          (int(petal_x - size//6), int(petal_y - size//3), 
                           size//3, size//1.5), 0)
    # 黄色い中心
    pygame.draw.circle(screen, (255, 255, 0), (x, y), size // 3)

def draw_sunflower(screen, x, y, color, size):
    # ひまわりの花びら
    petal_count = 12
    for i in range(petal_count):
        angle = (360 / petal_count) * i
        petal_x = x + size * 0.6 * pygame.math.Vector2(1, 0).rotate(angle).x
        petal_y = y + size * 0.6 * pygame.math.Vector2(1, 0).rotate(angle).y
        pygame.draw.ellipse(screen, (255, 200, 0), 
                          (int(petal_x - size//4), int(petal_y - size//4), 
                           size//2, size//2), 0)
    # 茶色い中心
    pygame.draw.circle(screen, (139, 69, 19), (x, y), size // 2.5)

def draw_cherry_blossom(screen, x, y, color, size):
    # 桜の花（5枚の花びら）
    petal_count = 5
    for i in range(petal_count):
        angle = (360 / petal_count) * i - 90
        petal_x = x + size * 0.7 * pygame.math.Vector2(1, 0).rotate(angle).x
        petal_y = y + size * 0.7 * pygame.math.Vector2(1, 0).rotate(angle).y
        # ハート型の花びら
        pygame.draw.circle(screen, (255, 182, 193), (int(petal_x), int(petal_y)), size // 2)
    # ピンクの中心
    pygame.draw.circle(screen, (255, 105, 180), (x, y), size // 4)

def draw_cosmos(screen, x, y, color, size):
    # コスモスの花びら
    petal_count = 8
    for i in range(petal_count):
        angle = (360 / petal_count) * i
        petal_x = x + size * 0.6 * pygame.math.Vector2(1, 0).rotate(angle).x
        petal_y = y + size * 0.6 * pygame.math.Vector2(1, 0).rotate(angle).y
        pygame.draw.ellipse(screen, color, 
                          (int(petal_x - size//3), int(petal_y - size//4), 
                           size//1.5, size//2), 0)
    # 黄色い中心
    pygame.draw.circle(screen, (255, 255, 200), (x, y), size // 3)

def draw_pansy(screen, x, y, color, size):
    # パンジーの花びら（重なり合う）
    # 上の2枚
    pygame.draw.ellipse(screen, color, 
                      (x - size//2, y - size//2, size//2, size//1.5), 0)
    pygame.draw.ellipse(screen, color, 
                      (x, y - size//2, size//2, size//1.5), 0)
    # 横の2枚
    pygame.draw.ellipse(screen, color, 
                      (x - size//1.5, y - size//4, size//1.5, size//2), 0)
    pygame.draw.ellipse(screen, color, 
                      (x, y - size//4, size//1.5, size//2), 0)
    # 下の1枚
    pygame.draw.ellipse(screen, color, 
                      (x - size//4, y, size//2, size//2), 0)
    # 中心の模様
    pygame.draw.circle(screen, (0, 0, 0), (x, y), size // 5)

# 花の描画関数のリスト
flower_functions = [
    draw_tulip, draw_rose, draw_daisy, draw_sunflower,
    draw_cherry_blossom, draw_cosmos, draw_pansy
]

def draw_flower(screen, x, y, color, size, flower_type=None):
    if flower_type is None:
        flower_type = random.randint(0, len(flower_functions) - 1)
    flower_functions[flower_type % len(flower_functions)](screen, x, y, color, size)

def draw_grid(screen):
    for x in range(0, GRID_WIDTH * BLOCK_SIZE, BLOCK_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, GRID_HEIGHT * BLOCK_SIZE))
    for y in range(0, GRID_HEIGHT * BLOCK_SIZE, BLOCK_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (GRID_WIDTH * BLOCK_SIZE, y))

def draw_piece(screen, piece):
    shape = piece.get_rotated_shape()
    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if cell:
                x = (piece.x + col_idx) * BLOCK_SIZE
                y = (piece.y + row_idx) * BLOCK_SIZE
                draw_flower(screen, x + BLOCK_SIZE // 2, y + BLOCK_SIZE // 2, 
                          COLORS[piece.color], BLOCK_SIZE // 2 - 2, piece.flower_type)

def draw_grid_cells(screen, grid):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                # 色情報と花の種類を分離
                color_index = (cell & 0x0F) - 1
                flower_type = (cell >> 4) & 0x0F
                draw_flower(screen, x * BLOCK_SIZE + BLOCK_SIZE // 2, 
                          y * BLOCK_SIZE + BLOCK_SIZE // 2,
                          COLORS[color_index], BLOCK_SIZE // 2 - 2, flower_type)

def draw_next_piece(screen, piece):
    font = pygame.font.Font(None, 24)
    text = font.render("Next:", True, WHITE)
    screen.blit(text, (GRID_WIDTH * BLOCK_SIZE + 20, 20))
    
    shape = SHAPES[piece.shape]
    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if cell:
                x = GRID_WIDTH * BLOCK_SIZE + 20 + col_idx * 20 + 10
                y = 60 + row_idx * 20 + 10
                draw_flower(screen, x, y, COLORS[piece.color], 8, piece.flower_type)

def draw_info(screen, game):
    font = pygame.font.Font(None, 24)
    
    score_text = font.render(f"Score: {game.score}", True, WHITE)
    screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 20, 150))
    
    lines_text = font.render(f"Lines: {game.lines}", True, WHITE)
    screen.blit(lines_text, (GRID_WIDTH * BLOCK_SIZE + 20, 180))
    
    level_text = font.render(f"Level: {game.level}", True, WHITE)
    screen.blit(level_text, (GRID_WIDTH * BLOCK_SIZE + 20, 210))

def draw_game_over(screen):
    font = pygame.font.Font(None, 48)
    text = font.render("GAME OVER", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)
    
    font_small = pygame.font.Font(None, 24)
    restart_text = font_small.render("Press SPACE to restart", True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(restart_text, restart_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("テトリス")
    clock = pygame.time.Clock()
    
    game = Tetris()
    
    running = True
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game.game_over:
                    if event.key == pygame.K_SPACE:
                        game = Tetris()
                else:
                    if event.key == pygame.K_LEFT:
                        game.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        game.drop_piece()
                    elif event.key == pygame.K_UP:
                        game.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()
        
        if not game.game_over:
            game.fall_time += dt
            if game.fall_time >= game.fall_speed:
                game.drop_piece()
                game.fall_time = 0
        
        screen.fill(BLACK)
        draw_grid(screen)
        draw_grid_cells(screen, game.grid)
        if not game.game_over:
            draw_piece(screen, game.current_piece)
        draw_next_piece(screen, game.next_piece)
        draw_info(screen, game)
        
        if game.game_over:
            draw_game_over(screen)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()