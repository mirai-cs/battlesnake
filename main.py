# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import random
import typing


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#888888",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:

    is_move_safe = {"up": True, "down": True, "left": True, "right": True}
    move_points = {"up": 0, "down": 0, "left": 0, "right": 0}

    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

    if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
        is_move_safe["left"] = False

    elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
        is_move_safe["right"] = False

    elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
        is_move_safe["down"] = False

    elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
        is_move_safe["up"] = False

    # TODO: Step 1 - Prevent your Battlesnake from moving out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    body_length = game_state["you"]["length"]
    if my_head["x"] == 0:
        is_move_safe["left"] = False
    elif my_head["x"] == board_width-1:
        is_move_safe["right"] = False
    if my_head["y"] == board_height-1:
        is_move_safe["up"] = False
    elif my_head["y"] == 0:
        is_move_safe["down"] = False
    my_body_average = {"x": 0, "y": 0}
    # TODO: Step 2 - Prevent your Battlesnake from colliding with itself
    for i in range(2, body_length - 1):
        my_body = game_state["you"]["body"][i]
        my_body_average["x"] += my_body['x']
        my_body_average["y"] += my_body['y']
        if my_body['x'] == my_head['x'] and my_body['y'] == my_head['y'] + 1:
            is_move_safe['up'] = False
        if my_body['x'] == my_head['x'] and my_body['y'] == my_head['y'] - 1:
            is_move_safe['down'] = False
        if my_body['x'] == my_head['x'] + 1 and my_body['y'] == my_head['y']:
            is_move_safe['right'] = False
        if my_body['x'] == my_head['x'] - 1 and my_body['y'] == my_head['y']:
            is_move_safe['left'] = False
    my_body_average['x'] /= body_length
    my_body_average['y'] /= body_length
    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    # TODO: Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
    # opponents = game_state['board']['snakes']
    # TODO : Prevent food if health is above health_level
    health_level = 20
    foods = game_state["board"]["food"]
    my_health = game_state["you"]["health"]
    if my_health > health_level :
        for food in foods:
            if my_head['x'] == food['x'] and my_head['y'] + 1 == food['y']:
                move_points['up'] -= 20
            if my_head['x'] == food['x'] and my_head['y'] - 1 == food['y']:
                move_points['down'] -= 20
            if my_head['x'] == food['x'] + 1 and my_head['y'] == food['y']:
                move_points['left'] -= 20
            if my_head['x'] == food['x'] - 1 and my_head['y'] == food['y']:
                move_points['right'] -= 20             
    else:
        min_food = {"x": 0, "y": 0}
        min_distance = 12
        for food in foods: 
            distance = abs(my_head['x'] - food['x']) + abs(my_head['y'] - food['y'])
            if distance <= min_distance:
                min_food = food
                min_distance = distance
        if min_food['x'] > my_head['x']:
            move_points["right"] += 30
        else:
            move_points["left"] += 30
        if min_food['y'] > my_head['y']:
            move_points["up"] += 30
        else:
            move_points["down"] += 30

    # TODO : intend to approch center of the board
    '''    
    board_xplus = my_head['x'] - 2.5
    board_yplus = my_head['y'] - 2.5
    move_points['left'] += board_xplus*2
    move_points['right'] -= board_xplus*2

    move_points['down'] += board_yplus*2
    move_points['up'] -= board_yplus*2
    '''
    '''
    average_yplus = my_head['y'] - my_body_average["y"]
    average_xplus = my_head['x'] - my_body_average["x"]
    move_points['left'] -= 6/average_xplus
    move_points['right'] += 6/average_xplus

    move_points['down'] -= 6/average_yplus
    move_points['up'] += 6/average_yplus
    '''
    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}
    else:
        next_move = max(safe_moves, key=lambda move: move_points[move])
        print(safe_moves)
        print(move_points)

    # Choose a random move from the safe ones
    #next_move = random.choice(safe_moves)
    

    # TODO: Step 4 - Move towards food instead of random, to regain health and survive longer
    # food = game_state['board']['food']

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
