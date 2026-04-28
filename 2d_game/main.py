import pyglet
from pyglet import window
import os
import random

# constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
SAND_HEIGHT = 140
bounding_box_margin = 5

# global variables
game_state = "start_screen"    # "start_screen", "playing", "game_over", "freeze"
obstacle_list = []
obs_keep = []
coin_list = []
coin_keep = []
lives = 3
blink = False
points = 0

# game window
win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, caption="Fishy")

# keyboard input
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
fish = pyglet.sprite.Sprite(fish_img, x=20, y=250)      # initial position
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

# score label
score_label = pyglet.text.Label(
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
    # random y_pos
    coin_y = random.randint(SAND_HEIGHT, WINDOW_HEIGHT - 50)
    
    # random speed
    coin_speed = random.randint(100, 200)

    coin = Coin(coin_y, coin_speed)
    coin_list.append(coin) 

def check_collisions():
    global lives, game_state, blink

    # print(f"blink: {blink}, lives: {lives}")    # debug

    if blink:
        return
    
    # smaller bounding box for the fish
    fish_left = fish.x + bounding_box_margin
    fish_right = fish.x + fish.width - bounding_box_margin
    fish_bottom = fish.y + bounding_box_margin
    fish_top = fish.y + fish.height - bounding_box_margin

    for obs in obstacle_list:

        # smaller bounding box for the obstacles
        obs_left = obs.sprite.x + bounding_box_margin
        obs_right = obs.sprite.x + obs.sprite.width - bounding_box_margin
        obs_bottom = obs.sprite.y + bounding_box_margin
        obs_top = obs.sprite.y + obs.sprite.height - bounding_box_margin

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
                pyglet.clock.schedule_once(show_game_over, 2)
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

def update_lives():
    if lives == 3:
        pass
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
    score_label.text = str(points)

def update(dt):
    global obstacle_list, obs_keep, coin_list, coin_keep, points, game_state
    obs_keep = []
    coin_keep = []

    if game_state == "start_screen":
        if keys[pyglet.window.key.SPACE]:
            game_state = "playing"

    elif game_state == "playing":
        # smaller bounding box for the fish
        fish_left = fish.x + bounding_box_margin
        fish_right = fish.x + fish.width - bounding_box_margin
        fish_bottom = fish.y + bounding_box_margin
        fish_top = fish.y + fish.height - bounding_box_margin   

        # handle fish movement
        if keys[pyglet.window.key.UP]:
            if fish.y > WINDOW_HEIGHT - (fish.height + 10):
                fish.y += 0
            else:
                fish.y += 100*dt
        elif keys[pyglet.window.key.DOWN]:
            if fish.y < SAND_HEIGHT:
                fish.y += 0
            else:
                fish.y -= 100*dt
        
        # handle obstacles
        for obs in obstacle_list:
            obs.update_pos(dt)          # update obstacle position
        
        for obs in obstacle_list:
            if obs.sprite.x > -obs.sprite.width:
                obs_keep.append(obs)
        obstacle_list = obs_keep

        # handle coins
        for c in coin_list:
            c.update_pos(dt)          # update obstacle position
        
        for c in coin_list:
            # smaller bounding box for the coins
            c_left = c.sprite.x + bounding_box_margin
            c_right = c.sprite.x + c.sprite.width - bounding_box_margin
            c_bottom = c.sprite.y + bounding_box_margin
            c_top = c.sprite.y + c.sprite.height - bounding_box_margin

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
        pass


@win.event
def on_draw():
    win.clear()
    background.draw()
    if game_state == "playing" or game_state == "freeze":
        heart_1.draw()
        heart_2.draw()
        heart_3.draw()
        score_label_text.draw()
        score_label.draw()
        for obs in obstacle_list:
            obs.draw()
        for c in coin_list:
            c.draw()
        fish.draw()


pyglet.clock.schedule_interval(update, 1/60)        # update game state at 60fps
pyglet.clock.schedule_interval(create_obstacle, 2)  # spawn obstacle every 2 seconds
pyglet.clock.schedule_interval(create_coin, 3)      # spawn coin every 3 seconds

pyglet.app.run()