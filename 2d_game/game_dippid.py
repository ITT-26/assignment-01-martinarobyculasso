import pyglet
from pyglet import window
import os
import random
from DIPPID import SensorUDP

# dippid config.
PORT = 5700
sensor = SensorUDP(PORT)

# constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
SAND_HEIGHT = 140
BOUNDING_BOX_MARGIN = 5
FISH_INIT_X = 50
FISH_INIT_Y = 250

# global variables
game_state = "start_screen"    # "start_screen", "playing", "game_over", "freeze"
obstacle_list = []
obs_keep = []
coin_list = []
coin_keep = []
points = 0
lives = 3
blink = False
accel_y = 0

# dippid callbacks
def handle_accelerometer(data):
    global accel_y
    accel_y = float(data['y'])

sensor.register_callback('accelerometer', handle_accelerometer)

# game window
win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, caption="Fishy")

# keyboard input to start/restart game
keys = pyglet.window.key.KeyStateHandler()
win.push_handlers(keys)

# ======= ASSETS =======

# path for assets (background, game objects, sprite)
assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
pyglet.resource.path = [assets_dir]
pyglet.resource.reindex()

# font
pyglet.font.add_file(os.path.join(assets_dir, 'Fredoka-VariableFont_wdth,wght.ttf'))

# static background
background_img = pyglet.resource.image('background.png')
background = pyglet.sprite.Sprite(background_img, x=0, y=0)

# player sprite - fishy!
fish_img = pyglet.resource.image('fish_red.png')
fish_skeleton_img = pyglet.resource.image('fish_red_skeleton.png')
fish = pyglet.sprite.Sprite(fish_img, x=FISH_INIT_X, y=FISH_INIT_Y)      # initial position
fish.scale = 0.6

# obstacles
puffer_img = pyglet.resource.image('fish_brown.png')
puffer_img = puffer_img.get_transform(flip_x=True)
eel_img = pyglet.resource.image('fish_grey.png')
eel_img = eel_img.get_transform(flip_x=True)

# coins
coin_img = pyglet.resource.image('coin.png')

# lives
heart_full_img = pyglet.resource.image('heart_full.png')
heart_empty_img = pyglet.resource.image('heart_empty.png')
heart_1 = pyglet.sprite.Sprite(heart_full_img, x=WINDOW_WIDTH-100, y=WINDOW_HEIGHT-40)
heart_1.scale = 1.2
heart_2 = pyglet.sprite.Sprite(heart_full_img, x=WINDOW_WIDTH-70, y=WINDOW_HEIGHT-40)
heart_2.scale = 1.2
heart_3 = pyglet.sprite.Sprite(heart_full_img, x=WINDOW_WIDTH-40, y=WINDOW_HEIGHT-40)
heart_3.scale = 1.2

# ======= LABELS =======

# score label
score_label_points = pyglet.text.Label(
    '0',
    font_size = 14,
    font_name='Fredoka',
    color = (0, 0, 0, 255),
    x=WINDOW_WIDTH - 20,
    y=WINDOW_HEIGHT - 70,
    anchor_x='right'
)

score_label_text = pyglet.text.Label(
    'Score: ',
    font_name='Fredoka',
    font_size = 14,
    color = (0, 0, 0, 255),
    x=WINDOW_WIDTH - 50,
    y=WINDOW_HEIGHT - 70,
    anchor_x='right'
)

# game title and instructions
game_title_label = pyglet.text.Label(
    'Fishy',
    font_name='Fredoka',
    font_size = 50,
    color = (0, 0, 0, 255),
    x=WINDOW_WIDTH//2,
    y=WINDOW_HEIGHT//2 + 100,
    anchor_x='center',
    anchor_y='center'
)

instructions_label_1 = pyglet.text.Label(
    'Tilt the device up and down to move the fish.\nAvoid the obstacles and collect coins!',
    font_name='Fredoka',
    font_size=18,
    color=(0, 0, 0, 255),
    x=WINDOW_WIDTH//2,
    y=WINDOW_HEIGHT//2 - 10,
    anchor_x='center',
    anchor_y='center',
    multiline=True,
    width=600,
    align='center'
)

instructions_label_2 = pyglet.text.Label(
    'Press SPACE to start',
    font_name='Fredoka',
    font_size=18,
    color=(0, 153, 0, 255),
    x=WINDOW_WIDTH//2,
    y=WINDOW_HEIGHT//2 - 70,
    anchor_x='center',
    anchor_y='center'
)

# game over label
game_over_label = pyglet.text.Label(
    'Game Over',
    font_name='Fredoka',
    font_size = 50,
    color = (204, 0, 0, 255),
    x=WINDOW_WIDTH//2,
    y=WINDOW_HEIGHT//2 + 50,
    anchor_x='center',
    anchor_y='center'
)

# restart instructions
restart_label = pyglet.text.Label(
    'Press R to restart',
    font_name='Fredoka',
    font_size=18,
    color=(0, 0, 0, 255),
    x=WINDOW_WIDTH//2,
    y=WINDOW_HEIGHT//2 - 20,
    anchor_x='center',
    anchor_y='center'
)

# ======= CLASSES =======

class Obstacle:
    def __init__(self, type, y_pos, speed):
        self.type = type
        self.y_pos = y_pos
        self.speed = speed

        # change image depending on type
        if type == "puffer":
            img = puffer_img
        elif type == "eel":
            img = eel_img
        self.sprite = pyglet.sprite.Sprite(img, x=WINDOW_WIDTH, y=y_pos)
        self.sprite.scale = 0.8
    
    def draw(self):
        self.sprite.draw()

    def update_pos(self, dt):
        self.sprite.x -= self.speed*dt

class Coin:
    def __init__(self, y_pos, speed):
        self.y_pos = y_pos
        self.speed = speed
        self.sprite = pyglet.sprite.Sprite(coin_img, x=WINDOW_WIDTH, y=y_pos)
        self.sprite.scale = 0.6

    def draw(self):
        self.sprite.draw()

    def update_pos(self, dt):
        self.sprite.x -= self.speed*dt

# ======= FUNCTIONS =======

def create_obstacle(dt):

    # avoid spawning obstacles when game is not active
    if game_state != "playing":
        return

    # random type
    rtype = random.randint(0, 1)
    if rtype == 0:
        obs_type = "puffer"
    else:
        obs_type = "eel"

    # random y_pos
    obs_y = random.randint(SAND_HEIGHT, WINDOW_HEIGHT - 50)
    
    # random speed
    obs_speed = random.randint(100, 300)

    obstacle = Obstacle(obs_type, obs_y, obs_speed)
    obstacle_list.append(obstacle) 

def create_coin(dt):

    # avoid spawning coins when game is not active
    if game_state != "playing":
        return
    
    # random y_pos
    coin_y = random.randint(SAND_HEIGHT, WINDOW_HEIGHT - 50)
    
    # random speed
    coin_speed = random.randint(100, 200)

    coin = Coin(coin_y, coin_speed)
    coin_list.append(coin) 

def check_collisions():
    global lives, game_state, blink

    if blink:
        return
    
    # smaller bounding box for the fish
    fish_left = fish.x + BOUNDING_BOX_MARGIN
    fish_right = fish.x + fish.width - BOUNDING_BOX_MARGIN
    fish_bottom = fish.y + BOUNDING_BOX_MARGIN
    fish_top = fish.y + fish.height - BOUNDING_BOX_MARGIN

    for obs in obstacle_list:

        # smaller bounding box for the obstacles
        obs_left = obs.sprite.x + BOUNDING_BOX_MARGIN
        obs_right = obs.sprite.x + obs.sprite.width - BOUNDING_BOX_MARGIN
        obs_bottom = obs.sprite.y + BOUNDING_BOX_MARGIN
        obs_top = obs.sprite.y + obs.sprite.height - BOUNDING_BOX_MARGIN

        if fish_right < obs_left or fish_left > obs_right or fish_top < obs_bottom or fish_bottom > obs_top:
            # collision = False
            pass
        else:
            # collision = True
            blink = True
            lives -= 1
            update_lives()
            if lives <= 0:
                fish.image = fish_skeleton_img
                game_state = "freeze"
                pyglet.clock.schedule_once(show_game_over, 1.5)
            else:
                pyglet.clock.schedule_interval(toggle_blink, 0.15) 
                pyglet.clock.schedule_once(blink_off, 2)
            break

def toggle_blink(dt):
    if fish.opacity == 0:
        fish.opacity = 255
    else:
        fish.opacity = 0

def blink_off(dt):
    global blink
    blink = False
    fish.opacity = 255
    pyglet.clock.unschedule(toggle_blink)

def show_game_over(dt):
    global game_state
    game_state = "game_over"

def reset():
    global lives, points, game_state, obstacle_list, coin_list, blink
    lives = 3               # reset lives
    points = 0              # reset points
    blink = False
    fish.opacity = 255 
    update_lives()
    update_score()
    obstacle_list = []
    coin_list = []
    # fish returns to starting position
    fish.x = FISH_INIT_X
    fish.y = FISH_INIT_Y
    fish.image = fish_img   # (alive fish)
    game_state = "playing"

def update_lives():
    if lives == 3:
        heart_3.image = heart_full_img
        heart_2.image = heart_full_img
        heart_1.image = heart_full_img   
    elif lives == 2:
        heart_3.image = heart_empty_img
    elif lives == 1:
        heart_3.image = heart_empty_img
        heart_2.image = heart_empty_img
    elif lives <= 0:
        heart_3.image = heart_empty_img
        heart_2.image = heart_empty_img
        heart_1.image = heart_empty_img        

def update_score():
    score_label_points.text = str(points)

def update(dt):
    global obstacle_list, obs_keep, coin_list, coin_keep, points, game_state
    obs_keep = []
    coin_keep = []

    if game_state == "start_screen":
        if keys[pyglet.window.key.SPACE]:
            game_state = "playing"

    elif game_state == "playing":
        # smaller bounding box for the fish
        fish_left = fish.x + BOUNDING_BOX_MARGIN
        fish_right = fish.x + fish.width - BOUNDING_BOX_MARGIN
        fish_bottom = fish.y + BOUNDING_BOX_MARGIN
        fish_top = fish.y + fish.height - BOUNDING_BOX_MARGIN   

        # handle fish movement
        if abs(accel_y) > 0.2:          # avoid small movements (noise)
            fish.y += (accel_y/2.0) * 100 * dt   
            # keep fish within window bounds
        if fish.y < SAND_HEIGHT:
            fish.y = SAND_HEIGHT
        elif fish.y > WINDOW_HEIGHT - (fish.height + 10):
            fish.y = WINDOW_HEIGHT - (fish.height + 10)
        
        # handle obstacles
        for obs in obstacle_list:
            obs.update_pos(dt)          # update obstacle position
        
        for obs in obstacle_list:
            if obs.sprite.x > -obs.sprite.width:
                obs_keep.append(obs)
        obstacle_list = obs_keep

        # handle coins
        for c in coin_list:
            c.update_pos(dt)            # update coin position
        
        for c in coin_list:
            # smaller bounding box for the coins
            c_left = c.sprite.x + BOUNDING_BOX_MARGIN
            c_right = c.sprite.x + c.sprite.width - BOUNDING_BOX_MARGIN
            c_bottom = c.sprite.y + BOUNDING_BOX_MARGIN
            c_top = c.sprite.y + c.sprite.height - BOUNDING_BOX_MARGIN

            if fish_right < c_left or fish_left > c_right or fish_top < c_bottom or fish_bottom > c_top:
                coin_keep.append(c)
            else:
                points += 1
                update_score()
        coin_list = coin_keep    

        # handle collisions & lives
        check_collisions()

    elif game_state == "freeze":
        pass

    elif game_state == "game_over":
        if keys[pyglet.window.key.R]:
            reset()


@win.event
def on_draw():
    win.clear()
    background.draw()
    if game_state == "playing" or game_state == "freeze":
        heart_1.draw()
        heart_2.draw()
        heart_3.draw()
        score_label_text.draw()
        score_label_points.draw()
        for obs in obstacle_list:
            obs.draw()
        for c in coin_list:
            c.draw()
        fish.draw()
    elif game_state == "start_screen":
        game_title_label.draw()
        instructions_label_1.draw()
        instructions_label_2.draw()
    elif game_state == "game_over":
        game_over_label.draw()
        restart_label.draw()


pyglet.clock.schedule_interval(update, 1/60)        # update game state at 60fps
pyglet.clock.schedule_interval(create_obstacle, 2)  # spawn obstacle every 2 seconds
pyglet.clock.schedule_interval(create_coin, 3)      # spawn coin every 3 seconds

pyglet.app.run()