from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

LANE_COUNT = 4
lane_width = SCREEN_WIDTH // LANE_COUNT

player_radius = 20
player_x = lane_width // 2
player_y = SCREEN_HEIGHT // 4
current_lane = 1
game_start_time = 0
target_score = 100
obstacles = []
bonus_balls = []
obstacle_speed = 2
obstacle_spawn_interval = 2000
bonus_ball_spawn_interval = 5000
last_spawn_time = 0
last_bonus_spawn_time = 0
score = 0
running = True
is_in_menu = True
last_score = 0
draw_game_won_screen = False
draw_game_over_screen = False
house_x = 0
house_y = SCREEN_HEIGHT
house_speed = 5
house_spawned = False
house_width = 50
house_height = 50
missed = False
target_time = 60000
elapsed_time = 0
remaining_time = target_time - elapsed_time

bubbles = []
bubble_spawn_interval = 4000
last_bubble_spawn_time = 0


# MID POINT CIRCLE
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


# MID POINT LINE
def midpoint_line(x0, y0, x1, y1):
    points = []
    dx = x1 - x0
    dy = y1 - y0

    if abs(dy) < abs(dx):
        if x0 > x1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        dx, dy = x1 - x0, y1 - y0
        d = 2 * dy - dx
        y = y0

        for x in range(x0, x1 + 1):
            points.append((x, y))
            if d > 0:
                y += 1 if dy > 0 else -1
                d -= 2 * dx
            d += 2 * dy
    else:
        if y0 > y1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        dx, dy = x1 - x0, y1 - y0
        d = 2 * dx - dy
        x = x0

        for y in range(y0, y1 + 1):
            points.append((x, y))
            if d > 0:
                x += 1 if dx > 0 else -1
                d -= 2 * dy
            d += 2 * dx

    return points


def draw_line(x0, y0, x1, y1):
    points = midpoint_line(int(x0), int(y0), int(x1), int(y1))
    glBegin(GL_POINTS)
    for x, y in points:
        glVertex2f(x, y)
    glEnd()


def draw_stickman(x, y, size):
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


def move_player(direction):
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
    global obstacles, bonus_balls, running, score, draw_game_over_screen

    # Update obstacles
    for i in range(len(obstacles) - 1, -1, -1):
        ox, oy, oradius = obstacles[i]
        oy -= obstacle_speed
        if oy + oradius < 0:
            obstacles.pop(i)
            score += 1
        else:
            obstacles[i] = (ox, oy, oradius)

        if math.sqrt((player_x - ox) ** 2 + (player_y - oy) ** 2) < player_radius + oradius:
            print("Game Over!")
            print(f"Final Score: {score}")
            running = False
            draw_game_over_screen = True

    for i in range(len(bonus_balls) - 1, -1, -1):
        bx, by, bradius = bonus_balls[i]
        by -= obstacle_speed
        if by + bradius < 0:
            bonus_balls.pop(i)
        else:
            bonus_balls[i] = (bx, by, bradius)

        if math.sqrt((player_x - bx) ** 2 + (player_y - by) ** 2) < player_radius + bradius:
            score += 10
            bonus_balls.pop(i)


def spawn_obstacle():
    global last_spawn_time

    current_time = glutGet(GLUT_ELAPSED_TIME)
    if current_time - last_spawn_time >= obstacle_spawn_interval:
        lane = random.randint(0, LANE_COUNT - 1)
        ox = lane * lane_width + lane_width // 2
        oy = SCREEN_HEIGHT + 20
        oradius = random.randint(10, 30)
        obstacles.append((ox, oy, oradius))
        last_spawn_time = current_time


def spawn_bonus_ball():
    global last_bonus_spawn_time

    current_time = glutGet(GLUT_ELAPSED_TIME)
    if current_time - last_bonus_spawn_time >= bonus_ball_spawn_interval:
        lane = random.randint(0, LANE_COUNT - 1)
        bx = lane * lane_width + lane_width // 2
        by = SCREEN_HEIGHT + 20
        bradius = random.randint(10, 20)
        bonus_balls.append((bx, by, bradius))
        last_bonus_spawn_time = current_time


def spawn_bubble():
    global last_bubble_spawn_time

    current_time = glutGet(GLUT_ELAPSED_TIME)
    if current_time - last_bubble_spawn_time >= bubble_spawn_interval:
        lane = random.randint(0, LANE_COUNT - 1)
        bx = lane * lane_width + lane_width // 2
        by = SCREEN_HEIGHT + 20  # Start just above the screen
        bradius = random.randint(10, 20)
        bubbles.append((bx, by, bradius))
        last_bubble_spawn_time = current_time


def update_bubbles():
    global bubbles, score

    for i in range(len(bubbles) - 1, -1, -1):
        bx, by, bradius = bubbles[i]
        by -= obstacle_speed
        if by + bradius < 0:
            bubbles.pop(i)
        else:
            bubbles[i] = (bx, by, bradius)

        if math.sqrt((player_x - bx) ** 2 + (player_y - by) ** 2) < player_radius + bradius:
            score -= 5
            print("Collision with bubble! Score decreased.")
            bubbles.pop(i)


def draw_red_bubble(x, y, radius):
    glColor3f(1, 0, 0)
    draw_circle_midpoint(x, y, radius)

    glColor3f(1, 1, 1)
    draw_text(x - radius // 3, y - radius // 3, "-")


def draw_game_won():
    global draw_game_won_screen
    glClear(GL_COLOR_BUFFER_BIT)
    glColor3f(0, 1, 0)
    draw_text(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, "GAME WON!")
    draw_text(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 30, f"Final Score: {score}")
    draw_text(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 60, "Returning to Home Screen...")
    glutSwapBuffers()
    draw_game_won_screen = False

    glutTimerFunc(2000, lambda _: reset_game(), 0)


def draw_game_over():
    glClear(GL_COLOR_BUFFER_BIT)
    glColor3f(0, 1, 0)
    draw_text(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, "GAME OVER!")
    draw_text(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 30, f"Final Score: {score}")
    draw_text(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 60, "Returning to Home Screen...")
    glutSwapBuffers()

    glutTimerFunc(2000, lambda _: reset_game(), 0)


def draw_time_over():
    glClear(GL_COLOR_BUFFER_BIT)
    glColor3f(1, 0, 0)
    draw_text(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2, "TIME OVER!")
    draw_text(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 30, f"Final Score: {score}")
    draw_text(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 60, "Returning to Home Screen...")
    glutSwapBuffers()

    glutTimerFunc(2000, lambda _: reset_game(), 0)


def reset_game():
    global obstacles, bonus_balls, score, running, is_in_menu, player_x, player_y, last_score, elapsed_time, house_spawned, draw_game_over_screen

    last_score = score
    obstacles = []
    bonus_balls = []
    score = 0
    elapsed_time = 0
    house_spawned = False
    draw_game_over_screen = False
    running = False
    is_in_menu = True
    player_x = lane_width // 2
    player_y = SCREEN_HEIGHT // 4
    glutPostRedisplay()


def draw_car(x, y, width, height):
    glColor3f(0.5, 0.2, 0.2)
    for dx in range(-width // 2, width // 2 + 1):
        for dy in range(-height // 2, height // 2 + 1):
            glVertex2f(x + dx, y + dy)

    # Windshield (trapezoid using points)
    glColor3f(0.1, 0.6, 1)
    for dx in range(-width // 4, width // 4 + 1):
        for dy in range(height // 4, height // 2 + 1):
            if abs(dx) <= width // 8:
                glVertex2f(x + dx, y + dy)

    wheel_radius = height // 5
    glColor3f(5, 8, 7)
    for angle in range(0, 360, 5):
        rad = math.radians(angle)
        lx = wheel_radius * math.cos(rad)
        ly = wheel_radius * math.sin(rad)
        glVertex2f(x - width // 4 + lx, y - height // 2 - wheel_radius + ly)
        glVertex2f(x + width // 4 + lx, y - height // 2 - wheel_radius + ly)


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
    glColor3f(0, 1, 0.2)
    draw_circle_midpoint(x, y, radius)
    glColor3f(1, 1, 1)

    draw_text(x - 6, y - 6, "+")


def draw_game():
    global player_x, player_y, obstacles, bonus_balls, score, elapsed_time, remaining_time, bubbles

    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(0.5, 0.5, 0.5)
    for i in range(1, LANE_COUNT):
        draw_line(i * lane_width, 0, i * lane_width, SCREEN_HEIGHT)

    draw_stickman(player_x, player_y, player_radius)

    for ox, oy, oradius in obstacles:
        glBegin(GL_POINTS)
        draw_car(ox, oy, oradius * 2, oradius)
        glEnd()

    # bonus balls
    for bx, by, bradius in bonus_balls:
        draw_bonus_ball_with_plus(bx, by, bradius)

    # red bubbles
    for bx, by, bradius in bubbles:
        draw_red_bubble(bx, by, bradius)

    # house
    if house_spawned:
        draw_house(house_x, house_y, house_width, house_height)

    glColor3f(1, 1, 1)
    draw_text(10, SCREEN_HEIGHT - 30, f"Score: {score}")
    draw_text(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 30, f"Time: {int(remaining_time / 1000)}s")
    draw_text(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 30, f"Target: {target_score}")

    glutSwapBuffers()


def display():
    if is_in_menu:
        draw_menu()
    elif draw_game_won_screen:
        draw_game_won()
    elif draw_game_over_screen:
        draw_game_over()
    elif missed == True or running == False:
        draw_game_over()
    else:
        draw_game()


# Timer
def draw_house(x, y, width, height):
    glColor3f(0.5, 0.4, 0.1)  # Brown color
    draw_rectangle(x - width // 2, y - height // 2, width, height)

    glColor3f(1, 0, 0.5)
    glBegin(GL_TRIANGLES)
    glVertex2f(x - width // 2, y + height // 2)
    glVertex2f(x + width // 2, y + height // 2)
    glVertex2f(x, y + height)
    glEnd()


def spawn_house():
    global house_x, house_y, house_spawned
    house_x = (random.randint(0, LANE_COUNT - 1) * lane_width) + (lane_width // 2)
    house_y = SCREEN_HEIGHT
    house_spawned = True
    print(f"House spawned at {house_x}, {house_y}")


def update_house():
    global house_y, house_spawned, running
    if house_spawned:
        house_y -= house_speed

        if house_y + house_height // 2 < 0:
            print("You missed the house. Game Over!")
            missed = True
            running = False

            draw_game_over()


def check_collision_with_house():
    global running, is_in_menu, draw_game_won_screen

    if (
            house_spawned and
            player_x + player_radius > house_x - house_width // 2 and
            player_x - player_radius < house_x + house_width // 2 and
            player_y + player_radius > house_y - house_height // 2 and
            player_y - player_radius < house_y + house_height // 2
    ):
        print("You Win! Collided with the house!")
        running = False
        draw_game_won_screen = True


def update(value):
    global obstacles, bonus_balls, running, score, elapsed_time, remaining_time, house_spawned, bubbles

    if not running:
        return

    current_time = glutGet(GLUT_ELAPSED_TIME)
    elapsed_time = current_time - game_start_time
    remaining_time = target_time - elapsed_time

    if not house_spawned:
        update_obstacles()
        spawn_obstacle()
        spawn_bonus_ball()
        spawn_bubble()
    else:
        update_house()
        check_collision_with_house()

    update_bubbles()

    if score >= target_score and not house_spawned:
        spawn_house()

    if draw_game_over_screen == True:
        draw_game_over()
    # time is up
    if remaining_time <= 0:
        print("Time Over! You didn't achieve the target.")
        print(f"Final Score: {score}")
        running = False
        draw_time_over()
        return

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)


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
    global is_in_menu, running, game_start_time

    ogl_y = SCREEN_HEIGHT - y

    if is_in_menu and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Start the game
        if SCREEN_WIDTH // 2 - 100 <= x <= SCREEN_WIDTH // 2 + 100:
            if SCREEN_HEIGHT // 2 + 50 <= ogl_y <= SCREEN_HEIGHT // 2 + 100:
                is_in_menu = False
                running = True
                game_start_time = glutGet(GLUT_ELAPSED_TIME)
                glutTimerFunc(0, update, 0)
                glutPostRedisplay()
            elif SCREEN_HEIGHT // 2 - 50 <= ogl_y <= SCREEN_HEIGHT // 2:
                glutLeaveMainLoop()


def init():
    glClearColor(0, 0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, -1, 1)
    glMatrixMode(GL_MODELVIEW)


glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(SCREEN_WIDTH, SCREEN_HEIGHT)
glutCreateWindow(b"Delivery Rush")
init()
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse)
glutMainLoop()