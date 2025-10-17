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
    #food_points : tendency to approach foods
    food_points = {"up": 1, "down": 1, "left": 1, "right": 1}
    #reachble_counts : to assess the size of the space
    reachble_counts = {"up": 0, "down": 0, "left": 0, "right": 0}
    #tail_points : tendency to approach my tail
    tail_points = {"up": 1, "down": 1, "left": 1, "right": 1}

    # We've included code to prevent your Battlesnake from moving backwards
    my_body = game_state["you"]["body"]
    body_length = game_state["you"]["length"]
    foods = game_state["board"]["food"]
    my_health = game_state["you"]["health"]

    my_head = my_body[0]
    my_neck = my_body[1]
    my_tail = my_body[body_length - 1]

    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    #board[x][y] :: my_body -> 1,my_neck -> 2,my_tail -> 3,food -> -1,empty -> 0 
    board = [[0 for j in range(board_width)] for i in range(board_height)]

    for food in foods:
        board[food['x']][food['y']] = -1
    board[my_head['x']][my_head['y']] = 1
    for i in range(1,body_length - 1):
        board[my_body[i]['x']][my_body[i]['y']] = 2
    board[my_tail['x']][my_tail['y']] = 3

    #FOOD_PENALTY : tendency to avoid foods
    FOOD_PENALTY = -1
    if(body_length >= 12):
        FOOD_PENALTY = 0.4
    if(body_length >= 16):
        FOOD_PENALTY = 0.95
    
    # TAIL_BOUNAUS : tendency to approach my tail
    TAIL_BOUNAUS = 1.2
    if(body_length >= 12):
        TAIL_BOUNAUS = 10
    if(body_length >=18):
        TAIL_BOUNAUS = 60
    
    #TODO : Prevent your Battlesnake from moving out of bounds and colliding with itself(TODO 1 and 2)
    if is_empty(my_head['x'] + 1,my_head['y'],board,my_health) == False:
        is_move_safe['right'] = False
    if is_empty(my_head['x'] - 1,my_head['y'],board,my_health) == False:
        is_move_safe['left'] = False
    if is_empty(my_head['x'],my_head['y'] + 1,board,my_health) == False:
        is_move_safe['up'] = False    
    if is_empty(my_head['x'],my_head['y'] - 1,board,my_health) == False:
        is_move_safe['down'] = False

    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)
    
    #TODO : Count available moves
    for move in safe_moves:
        next_x,next_y = my_head['x'],my_head['y']
        if move == 'up':
            next_y += 1
        elif move == 'down':
            next_y -= 1
        elif move == 'left':
            next_x -= 1
        elif move == 'right':
            next_x += 1
        reachble_counts[move] = count_reachble_ways(next_x,next_y,0,board,my_health)

    # TODO : Prevent food if health is above health_level
    health_level = 20
    if my_health > health_level :   #when snake avoid foods
        if my_head['x'] < board_width - 1 and board[my_head['x'] + 1][my_head['y']] == -1:
            food_points['right'] = FOOD_PENALTY
        if my_head['x'] > 0 and board[my_head['x'] - 1][my_head['y']] == -1:
            food_points['left'] = FOOD_PENALTY
        if my_head['y'] < board_height - 1 and board[my_head['x']][my_head['y'] + 1] == -1:
            food_points['up'] = FOOD_PENALTY
        if my_head['y'] > 0 and board[my_head['x']][my_head['y'] - 1] == -1:
            food_points['down'] = FOOD_PENALTY      
    else:   #when snake aproach foods
        min_food = {"x": 0, "y": 0}
        min_distance = 12
        TAIL_BOUNAUS = 2
        # set min_food and min_disatance
        for food in foods: 
            distance = abs(my_head['x'] - food['x']) + abs(my_head['y'] - food['y'])
            if distance <= min_distance:
                min_food = food
                min_distance = distance
        if min_food['x'] > my_head['x']:
            food_points["right"] += (min_food['x'] - my_head['x']) * (health_level - my_health)
        else:
            food_points["left"] += (my_head['x'] - min_food['x']) * (health_level - my_health)
        if min_food['y'] > my_head['y']:
            food_points["up"] += (min_food['y'] - my_head['y']) * (health_level - my_health)
        else:
            food_points["down"] += (my_head['y'] - min_food['y']) * (health_level - my_health)

    if my_tail['y'] > my_head['y']:
        tail_points['up'] = TAIL_BOUNAUS
    elif my_tail['y'] < my_head['y']:
        tail_points['down'] = TAIL_BOUNAUS
    if my_tail['x'] > my_head['x']:
        tail_points['right'] = TAIL_BOUNAUS
    elif my_tail['x'] < my_head['x']:
        tail_points['left'] = TAIL_BOUNAUS

    # TODO : Decide next move
    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}
    else:
        #next_move is high scoring move in safe_moves 
        next_move = max(safe_moves, key=lambda move: food_points[move] * reachble_counts[move] * tail_points[move])
        print("safe_moves:")
        print(safe_moves)
        print("food_points:")
        print(food_points)
        print("reachble_counts:")
        print(reachble_counts)
        print("tail_point")
        print(tail_points)

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}

def count_reachble_ways(next_x,next_y,depth,board,my_health):
    if is_empty(next_x,next_y,board,my_health) == False:
        return depth
    else:
        if depth == 7:
            return depth
        else:
            return count_reachble_ways(next_x + 1,next_y,depth + 1,board,my_health) + count_reachble_ways(next_x - 1,next_y,depth + 1,board,my_health) + count_reachble_ways(next_x,next_y + 1,depth + 1,board,my_health) + count_reachble_ways(next_x,next_y - 1,depth + 1,board,my_health)  

# return True if board[x][y] is food(-1)
def is_food(x,y,board):
    if x < 0 or y < 0 or x >= 6 or y >= 6:
        return False
    if board[x][y] == -1:
        return True
    return False

# return True if board[x][y] is empty(0,-1,3)
def is_empty(x,y,board,my_health):
    if x < 0 or y < 0 or x >= 6 or y >= 6:
        return False
    if board[x][y] == 0 or board[x][y] == -1 or (board[x][y] == 3 and  my_health != 100 ):   #empty,food,tail
        return True
    else:
        return False

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
