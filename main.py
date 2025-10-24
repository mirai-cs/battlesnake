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

import os
from tarfile import NUL
import typing
import copy

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

# Constant values
SPACE = 0
FOOD = -1
EXPLORED = -2
MY_HEAD = 1
MY_BODY = 2
MY_TAIL = 3
MAX_HEALTH = 100

class Snake:
    def __init__(self,game_state,snake_name):
        self.body = game_state[snake_name]["body"]
        self.length = game_state[snake_name]["length"]
        self.health =  game_state[snake_name]["health"]
        self.head = self.body[0]
        self.tail = self.body[-1]

class Board:
    def __init__(self,game_state,my_snake):
        self.width = game_state['board']['width']
        self.height = game_state['board']['height']
        self.foods = game_state["board"]["food"]
        self.turn = game_state['turn']
        self.grid = [[0 for j in range(self.width)] for i in range(self.height)]
        self.my_snake = my_snake
        self.grid_copy = copy.deepcopy(self.grid)
        self.init_grid()

    def init_grid(self):
        for food in self.foods:
            self.grid[food['x']][food['y']] = FOOD
        self.grid[self.my_snake.head['x']][self.my_snake.head['y']] = MY_HEAD
        self.grid[self.my_snake.tail['x']][self.my_snake.tail['y']] = MY_TAIL
        for i in range(1,self.my_snake.length - 1):
            self.grid[self.my_snake.body[i]['x']][self.my_snake.body[i]['y']] = MY_BODY

    def is_empty(self,x,y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        if self.grid[x][y] == SPACE or self.grid[x][y] == FOOD or (self.grid[x][y] == MY_TAIL and  self.my_snake.health < MAX_HEALTH and self.turn > 3):
            return True
        else:
            return False      
        
    def is_food(self,x,y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        if self.grid[x][y] == FOOD:
            return True
        else:
            return False       
        
    def get_closest_food(self):
        my_head_x = self.my_snake.head['x']
        my_head_y = self.my_snake.head['y']
        min_distance = self.width + self.height
        closest_food = self.foods[0]
        for food in self.foods: 
            distance = abs(my_head_x - food['x']) + abs(my_head_y - food['y'])
            if distance <= min_distance:
                closest_food = food
                min_distance = distance
        return closest_food
    
class Evaluator:
    def __init__(self,board,my_snake):
        self.board = board
        self.my_snake = my_snake
        self.grid_copy = copy.deepcopy(board.grid)

    def get_safe_moves(self):
        is_move_safe = {"up": True, "down": True, "left": True, "right": True}
        if self.board.is_empty(self.my_snake.head['x'] + 1,self.my_snake.head['y']) == False:
            is_move_safe['right'] = False
        if self.board.is_empty(self.my_snake.head['x'] - 1,self.my_snake.head['y']) == False:
            is_move_safe['left'] = False
        if self.board.is_empty(self.my_snake.head['x'],self.my_snake.head['y'] + 1) == False:
            is_move_safe['up'] = False        
        if self.board.is_empty(self.my_snake.head['x'],self.my_snake.head['y'] - 1) == False:
            is_move_safe['down'] = False
        safe_moves = []
        for move, isSafe in is_move_safe.items():
            if isSafe:
                safe_moves.append(move)
        return safe_moves
    
    def asess_food_points_avoid(self):
        food_points = {"up": 1, "down": 1, "left": 1, "right": 1}
        FOOD_PENALTY = 0.5
        my_head_x = self.my_snake.head['x']
        my_head_y = self.my_snake.head['y']

        if self.board.is_food(my_head_x + 1,my_head_y):
            food_points['right'] = FOOD_PENALTY
        if self.board.is_food(my_head_x - 1,my_head_y):
            food_points['left'] = FOOD_PENALTY
        if self.board.is_food(my_head_x,my_head_y + 1):
            food_points['up'] = FOOD_PENALTY
        if self.board.is_food(my_head_x,my_head_y - 1):
            food_points['down'] = FOOD_PENALTY    
        return food_points  
    
    def asess_food_points_approach(self):
        food_points = {"up": 1, "down": 1, "left": 1, "right": 1}
        closest_food = self.board.get_closest_food()
        my_head_x = self.my_snake.head['x']
        my_head_y = self.my_snake.head['y']
        HEALTH_LEVEL = 15
        if closest_food['x'] > my_head_x:
            food_points["right"] = (closest_food['x'] - my_head_x) * (HEALTH_LEVEL - self.my_snake.health)
        else:
            food_points["left"] += (my_head_x - closest_food['x']) * (HEALTH_LEVEL - self.my_snake.health)
        if closest_food['y'] > my_head_y:
            food_points["up"] += (closest_food['y'] - my_head_y) * (HEALTH_LEVEL - self.my_snake.health)
        else:
            food_points["down"] += (my_head_y - closest_food['y']) * (HEALTH_LEVEL - self.my_snake.health)
        return food_points

    def asess_tail_points(self):
        TAIL_BOUNAUS = 1.5
        tail_points = {"up": 1, "down": 1, "left": 1, "right": 1}
        my_tail_x = self.my_snake.tail['x']
        my_tail_y = self.my_snake.tail['y']
        my_head_x = self.my_snake.head['x']
        my_head_y = self.my_snake.head['y']
        if my_tail_y > my_head_y:
            tail_points['up'] = TAIL_BOUNAUS
        elif my_tail_y < my_head_y:
            tail_points['down'] = TAIL_BOUNAUS
        if my_tail_x > my_head_x:
            tail_points['right'] = TAIL_BOUNAUS
        elif my_tail_x < my_head_x:
            tail_points['left'] = TAIL_BOUNAUS
        return tail_points
            
    def asess_reachble_counts(self):
        reachble_counts = {"up": 0, "down": 0, "left": 0, "right": 0}
        for move in ["up", "down", "left", "right"]:
            next_x,next_y = self.my_snake.head['x'],self.my_snake.head['y']
            if move == 'up':
                next_y += 1
            elif move == 'down':
                next_y -= 1
            elif move == 'left':
                next_x -= 1
            elif move == 'right':
                next_x += 1
            current_depth = 0
            reachble_counts[move] = self.count_reachble_ways(next_x,next_y,current_depth)
        return reachble_counts

    def count_reachble_ways(self,next_x,next_y,depth):
        if self.is_empty(next_x,next_y) == False or self.grid_copy[next_x][next_y] == EXPLORED:
            return depth
        max_depth = depth
        self.grid_copy[next_x][next_y] = EXPLORED
        tail_index = self.my_snake.length - depth - 1
        tail_x,tail_y = None,None

        if tail_index >= 0:
            tail_x = self.my_snake.body[tail_index]['x']
            tail_y = self.my_snake.body[tail_index]['y']
            self.grid_copy[tail_x][tail_y] = SPACE

        MAX_DEPTH = 12
        if depth < MAX_DEPTH:
            max_depth = max(self.count_reachble_ways(next_x + 1,next_y,depth + 1),
                            self.count_reachble_ways(next_x - 1,next_y,depth + 1), 
                            self.count_reachble_ways(next_x,next_y + 1,depth + 1),
                            self.count_reachble_ways(next_x,next_y - 1,depth + 1)) 
        self.grid_copy[next_x][next_y] = self.board.grid[next_x][next_y]
        if tail_index >= 0:
            self.grid_copy[tail_x][tail_y] = self.board.grid[tail_x][tail_y]
        return max_depth
    
    def is_empty(self,x,y):
        if x < 0 or y < 0 or x >= self.board.width or y >= self.board.height:
            return False
        if self.grid_copy[x][y] == SPACE or self.grid_copy[x][y] == FOOD or (self.grid_copy[x][y] == MY_TAIL and  self.my_snake.health < MAX_HEALTH and self.board.turn > 3):   #empty,food,tail
            return True
        else:
            return False   

# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    my_snake = Snake(game_state,"you")
    board = Board(game_state,my_snake)
    evaluator = Evaluator(board,my_snake)

    next_move = choose_best_move(my_snake,evaluator)

    if next_move == None:
        print(f"There is no safe moves!")
        print(f"MOVE {game_state['turn']}: {next_move}\n")
        return {"move": "down"}
    else:
        print(f"MOVE {game_state['turn']}: {next_move}\n")
        return {"move": next_move}

def choose_best_move(my_snake,evaluater):
    HEALTH_LEVEL = 15
    #W_F,W_R,W_T = 1,1,1
    safe_moves = evaluater.get_safe_moves()
    move_scores = {"up": 0, "down": 0, "left": 0, "right": 0}
    food_points = {"up": 0, "down": 0, "left": 0, "right": 0}

    if my_snake.health > HEALTH_LEVEL:
        food_points = evaluater.asess_food_points_avoid()
    else:
        food_points = evaluater.asess_food_points_approach()
    tail_points = evaluater.asess_tail_points()
    reachble_counts = evaluater.asess_reachble_counts()

    for move in safe_moves:
        move_scores[move] = food_points[move] * reachble_counts[move] * tail_points[move]
        #move_scores[move] = W_F*food_points[move] + W_R*reachble_counts[move] + W_T*tail_points[move]
    
    print_scores(reachble_counts,food_points,tail_points,move_scores)
    
    if len(safe_moves) == 0:
        return None
    best_move = max(safe_moves, key=lambda move: move_scores[move])
    return best_move

def print_scores(reachble_counts,food_points,tail_points,move_scores):
    print(f"reachble count:\n{reachble_counts}")
    print(f"food points:\n{food_points}")
    print(f"tail points:\n{tail_points}")
    print(f"move scores:\n{move_scores}")

# Start server when `python main.py` is run
if __name__ == "__main__":
    os.system('cls')
    from server import run_server
    run_server({"info": info, "start": start, "move": move, "end": end})