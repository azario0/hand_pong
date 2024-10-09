import cv2
import mediapipe as mp
import pygame
import sys
import random

# Initialize Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand Pong")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Paddle
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 20
paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - PADDLE_HEIGHT - 10, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball
BALL_SIZE = 20
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
ball_speed_x = 5 * random.choice((1, -1))
ball_speed_y = -5

# Bricks
BRICK_WIDTH, BRICK_HEIGHT = 80, 30
BRICK_ROWS, BRICK_COLS = 5, 8
bricks = []

# Game variables
lives = 3
font = pygame.font.Font(None, 36)
game_state = "playing"  # Can be "playing", "won", or "game_over"

def reset_game():
    global ball, ball_speed_x, ball_speed_y, bricks, lives, game_state
    ball.center = (WIDTH // 2, HEIGHT // 2)
    ball_speed_x = 5 * random.choice((1, -1))
    ball_speed_y = -5
    bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            brick = pygame.Rect(col * (BRICK_WIDTH + 5) + 30, row * (BRICK_HEIGHT + 5) + 30, BRICK_WIDTH, BRICK_HEIGHT)
            bricks.append(brick)
    lives = 3
    game_state = "playing"

def draw_text(text, x, y):
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (x, y))

# Main game loop
cap = cv2.VideoCapture(0)
clock = pygame.time.Clock()

reset_game()  # Initialize the game state

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_q:  # Add quit functionality for 'Q' key
                running = False

    if game_state == "playing":
        # Process hand detection
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get the x-coordinate of the index finger tip
                x = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * WIDTH)
                paddle.centerx = x

        # Move the ball
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Ball collision with walls
        if ball.left <= 0 or ball.right >= WIDTH:
            ball_speed_x *= -1
        if ball.top <= 0:
            ball_speed_y *= -1

        # Ball collision with paddle
        if ball.colliderect(paddle) and ball_speed_y > 0:
            ball_speed_y *= -1
            # Adjust x speed based on where the ball hits the paddle
            ball_speed_x += (ball.centerx - paddle.centerx) / 10

        # Ball collision with bricks
        for brick in bricks[:]:
            if ball.colliderect(brick):
                bricks.remove(brick)
                ball_speed_y *= -1
                break

        # Check for lost ball
        if ball.bottom >= HEIGHT:
            lives -= 1
            if lives > 0:
                ball.center = (WIDTH // 2, HEIGHT // 2)
                ball_speed_x = 5 * random.choice((1, -1))
                ball_speed_y = -5
            else:
                game_state = "game_over"

        # Check for win condition
        if len(bricks) == 0:
            game_state = "won"

    # Draw everything
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    for brick in bricks:
        pygame.draw.rect(screen, RED, brick)

    # Draw lives and score
    draw_text(f"Lives: {lives}", 10, 10)
    draw_text(f"Bricks: {len(bricks)}", WIDTH - 120, 10)

    # Display messages based on game state
    if game_state == "won":
        draw_text("You Won! Press 'R' to restart or 'Q' to quit", WIDTH // 2 - 220, HEIGHT // 2)
    elif game_state == "game_over":
        draw_text("Game Over! Press 'R' to restart or 'Q' to quit", WIDTH // 2 - 250, HEIGHT // 2)
    else:
        draw_text("Press 'Q' to quit", WIDTH // 2 - 70, HEIGHT - 30)

    pygame.display.flip()
    clock.tick(60)

# Clean up
pygame.quit()
cap.release()
cv2.destroyAllWindows()
sys.exit()