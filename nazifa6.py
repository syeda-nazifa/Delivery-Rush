from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import sys

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Game state variables
LANE_COUNT = 4
lane_width = SCREEN_WIDTH // LANE_COUNT

player_radius = 20
player_x = lane_width // 2
player_y = SCREEN_HEIGHT // 4
current_lane = 1

obstacles = []
bonus_balls = []
obstacle_speed = 2
obstacle_spawn_interval = 2000  # Spawn obstacle every 2000 ms
bonus_ball_spawn_interval = 5000  # Spawn bonus ball every 5000 ms
last_spawn_time = 0
last_bonus_spawn_time = 0
score = 0
running = True
is_in_menu = True
last_score = 0

# Drawing functions
def draw_circle_midpoint(x_center, y_center, radius):
    x = 0
    y = radius
    d = 1 - radius

    glBegin(GL_POINTS)
    while x <= y:
        glVertex2f(x_center + x, y_center + y)
        glVertex2f(x_center - x, y_center + y)
        glVertex2f(x_center + x, y_center - y)
        glVertex2f(x_center - x, y_center - y)
        glVertex2f(x_center + y, y_center + x)
        glVertex2f(x_center - y, y_center + x)
        glVertex2f(x_center + y, y_center - x)
        glVertex2f(x_center - y, y_center - x)
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
    glEnd()

def draw_line(x0, y0, x1, y1):
    glBegin(GL_LINES)
    glVertex2f(x0, y0)
    glVertex2f(x1, y1)
    glEnd()

def draw_stickman(x, y, size):
    """Draw a stickman at (x, y) with a given size."""
    # Head
    glColor3f(0, 1, 0)  # Green
    draw_circle_midpoint(x, y + size, size // 2)

    # Body
    glColor3f(1, 1, 1)  # White
    draw_line(x, y + size // 2, x, y - size // 2)

    # Arms
    draw_line(x - size // 2, y + size // 4, x + size // 2, y + size // 4)

    # Legs
    draw_line(x, y - size // 2, x - size // 3, y - size)
    draw_line(x, y - size // 2, x + size // 3, y - size)

def draw_rectangle(x, y, width, height):
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

def draw_text(x, y, text):
    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

# Game logic
def move_player(direction):
    """Move player based on direction ('left', 'right', 'up', 'down')."""
    global current_lane, player_x, player_y

    movement_distance = 40  # Increased vertical movement
    if direction == "left" and current_lane > 0:
        current_lane -= 1
        player_x = current_lane * lane_width + lane_width // 2
    elif direction == "right" and current_lane < LANE_COUNT - 1:
        current_lane += 1
        player_x = current_lane * lane_width + lane_width // 2
    elif direction == "up" and player_y < SCREEN_HEIGHT - player_radius * 2:
        player_y += movement_distance
    elif direction == "down" and player_y > player_radius * 2:
        player_y -= movement_distance

def update_obstacles():
    global obstacles, bonus_balls, running, score

    # Update obstacles
    for i in range(len(obstacles) - 1, -1, -1):
        ox, oy, oradius = obstacles[i]
        oy -= obstacle_speed
        if oy + oradius < 0:
            obstacles.pop(i)
            score += 1
        else:
            obstacles[i] = (ox, oy, oradius)

        # Check collision with player
        if math.sqrt((player_x - ox) ** 2 + (player_y - oy) ** 2) < player_radius + oradius:
            print("Game Over!")
            print(f"Final Score: {score}")
            running = False
            reset_game()

    # Update bonus balls
    for i in range(len(bonus_balls) - 1, -1, -1):
        bx, by, bradius = bonus_balls[i]
        by -= obstacle_speed
        if by + bradius < 0:
            bonus_balls.pop(i)
        else:
            bonus_balls[i] = (bx, by, bradius)

        # Check collision with player
        if math.sqrt((player_x - bx) ** 2 + (player_y - by) ** 2) < player_radius + bradius:
            score += 10
            bonus_balls.pop(i)

def spawn_obstacle():
    """Spawn a new obstacle at a random lane."""
    global last_spawn_time

    current_time = glutGet(GLUT_ELAPSED_TIME)
    if current_time - last_spawn_time >= obstacle_spawn_interval:
        lane = random.randint(0, LANE_COUNT - 1)
        ox = lane * lane_width + lane_width // 2
        oy = SCREEN_HEIGHT + 20  # Start just above the screen
        oradius = random.randint(10, 30)
        obstacles.append((ox, oy, oradius))
        last_spawn_time = current_time

def spawn_bonus_ball():
    """Spawn a new bonus ball at a random lane."""
    global last_bonus_spawn_time

    current_time = glutGet(GLUT_ELAPSED_TIME)
    if current_time - last_bonus_spawn_time >= bonus_ball_spawn_interval:
        lane = random.randint(0, LANE_COUNT - 1)
        bx = lane * lane_width + lane_width // 2
        by = SCREEN_HEIGHT + 20  # Start just above the screen
        bradius = random.randint(10, 20)
        bonus_balls.append((bx, by, bradius))
        last_bonus_spawn_time = current_time

def reset_game():
    global obstacles, bonus_balls, score, running, is_in_menu, player_x, player_y, last_score

    last_score = score
    obstacles = []
    bonus_balls = []
    score = 0
    running = False
    is_in_menu = True
    player_x = lane_width // 2
    player_y = SCREEN_HEIGHT // 4
    glutPostRedisplay()
def draw_car(x, y, width, height):
    """Draw a car using GL_POINTS at (x, y) with given width and height."""
    # Car body (rectangle shape using points)
    glColor3f(0.8, 0.2, 0.2)  # Red color for the car body
    for dx in range(-width // 2, width // 2 + 1):
        for dy in range(-height // 2, height // 2 + 1):
            glVertex2f(x + dx, y + dy)

    # Windshield (trapezoid using points)
    glColor3f(0.1, 0.6, 1)  # Light blue color for the windshield
    for dx in range(-width // 4, width // 4 + 1):
        for dy in range(height // 4, height // 2 + 1):
            if abs(dx) <= width // 8:
                glVertex2f(x + dx, y + dy)

    # Car wheels (circles using points)
    wheel_radius = height // 5
    glColor3f(0, 0, 0)  # Black color for the wheels
    for angle in range(0, 360, 5):  # Create a circle with points
        rad = math.radians(angle)
        lx = wheel_radius * math.cos(rad)
        ly = wheel_radius * math.sin(rad)
        glVertex2f(x - width // 4 + lx, y - height // 2 - wheel_radius + ly)  # Left wheel
        glVertex2f(x + width // 4 + lx, y - height // 2 - wheel_radius + ly)  # Right wheel

# Menu and game screens
def draw_menu():
    glClear(GL_COLOR_BUFFER_BIT)
    glColor3f(0, 1, 0)
    draw_rectangle(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)
    draw_text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 70, "START")

    glColor3f(1, 0, 0)
    draw_rectangle(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50)
    draw_text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 - 30, "EXIT")

    glColor3f(1, 1, 1)
    draw_text(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 100, f"Last Score: {last_score}")
    glutSwapBuffers()

def draw_bonus_ball_with_plus(x, y, radius):
    glColor3f(0, 1, 0)  # Green color for the bonus ball
    draw_circle_midpoint(x, y, radius)  # Draw the bonus ball
    glColor3f(1, 1, 1)  # White color for the "+" sign
    # Draw the "+" sign in the center of the bonus ball
    draw_text(x - 6, y - 6, "+")  # Adjust the position for the "+" sign to be centered

def draw_game():
    global player_x, player_y, obstacles, bonus_balls, score

    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(0.5, 0.5, 0.5)
    for i in range(1, LANE_COUNT):
        draw_line(i * lane_width, 0, i * lane_width, SCREEN_HEIGHT)

    draw_stickman(player_x, player_y, player_radius)

    # Draw car obstacles using GL_POINTS
    for ox, oy, oradius in obstacles:
        car_width = oradius * 2  # Use radius to define car width
        car_height = oradius  # Use radius to define car height
        glBegin(GL_POINTS)
        draw_car(ox, oy, car_width, car_height)  # Draw the detailed car as obstacle
        glEnd()

    glColor3f(0, 1, 0)  # Green for bonus balls
    for bx, by, bradius in bonus_balls:
        draw_bonus_ball_with_plus(bx, by, bradius)

    glColor3f(1, 1, 1)
    draw_text(10, SCREEN_HEIGHT - 30, f"Score: {score}")
    glutSwapBuffers()

def display():
    if is_in_menu:
        draw_menu()
    else:
        draw_game()

# Timer function for game updates
def update(value):
    if running:
        update_obstacles()
        spawn_obstacle()
        spawn_bonus_ball()
        glutPostRedisplay()
        glutTimerFunc(16, update, 0)  # Call update every ~16ms (60 FPS)

# Input handling
def keyboard(key, x, y):
    global is_in_menu, running

    if key == b'a':  # Move left
        move_player("left")
    elif key == b'd':  # Move right
        move_player("right")
    elif key == b'w':  # Move up
        move_player("up")
    elif key == b's':  # Move down
        move_player("down")
    elif key == b'q':  # Quit
        reset_game()
    glutPostRedisplay()

def mouse(button, state, x, y):
    global is_in_menu, running

    # Convert GLUT Y-coordinate to OpenGL Y-coordinate
    ogl_y = SCREEN_HEIGHT - y

    if is_in_menu and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Check if the "START" button was clicked
        if SCREEN_WIDTH // 2 - 100 <= x <= SCREEN_WIDTH // 2 + 100:
            if SCREEN_HEIGHT // 2 + 50 <= ogl_y <= SCREEN_HEIGHT // 2 + 100:
                is_in_menu = False
                running = True
                glutTimerFunc(0, update, 0)
                glutPostRedisplay()

            # Check if the "EXIT" button was clicked
            elif SCREEN_HEIGHT // 2 - 50 <= ogl_y <= SCREEN_HEIGHT // 2:
                glutLeaveMainLoop()

# Initialization
def init():
    glClearColor(0, 0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, -1, 1)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(SCREEN_WIDTH, SCREEN_HEIGHT)
    glutCreateWindow(b"Stickman Game")
    init()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    glutMainLoop()

if __name__ == "__main__":
    main()
