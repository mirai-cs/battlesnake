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
from turtle import distance
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
        self._init_grid()

    def _init_grid(self):
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
    
    def get_food_id(self,x,y):
        for i,food in enumerate(self.foods):
            if food['x'] == x and food['y'] == y:
                return i
        return None
    
class Evaluator:
    def __init__(self,board,my_snake):
        self.board = board
        self.my_snake = my_snake
        self.grid_copy = copy.deepcopy(board.grid)
        self.grid_copy_fill = None
        self.food_candidates = [
            {'id':0,'move':None,'distant':0,'max_depth':0},
            {'id':1,'move':None,'distant':0,'max_depth':0},
            {'id':2,'move':None,'distant':0,'max_depth':0}
        ]
        self.MAX_DEPTH = 8
        if my_snake.length >= 8:
            self.MAX_DEPTH = 12
        if my_snake.length >= 15:
            self.MAX_DEPTH = 14
        if my_snake.length >= 30:
            self.MAX_DEPTH = my_snake.length - 15

        self.food_counts = {"up": 3, "down": 3, "left": 3, "right": 3}
        self.explored_counts = {"up": 0, "down": 0, "left": 0, "right": 0}
        self.APPROACH_SAFE_SCOPE = 0
        if my_snake.length >= 20:
            self.APPROACH_SAFE_SCOPE = my_snake.length / 8
        

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

    def asess_tail_distances(self):
        tail_distances = {"up": 0, "down": 0, "left": 0, "right": 0}
        vectors = {"up": [0,1], "down": [0,-1], "left": [-1,0], "right": [1,0]}

        my_length = self.my_snake.length
        next_my_tail_x = self.my_snake.body[my_length - 2]['x']
        next_my_tail_y = self.my_snake.body[my_length - 2]['y']
        my_head_x = self.my_snake.head['x']
        my_head_y = self.my_snake.head['y']

        for move in ["up","down","left","right"]:
            distance = abs(my_head_x + vectors[move][0] - next_my_tail_x) + abs(my_head_y + vectors[move][1] - next_my_tail_y)
            if distance <= 4:
                tail_distances[move] = distance - 1
            else:
                tail_distances[move] = 4
        return tail_distances
    
    def count_explored(self):
        explored_count = 0
        for x in range(self.board.width):
            for y in range(self.board.height):
                if self.grid_copy_fill[x][y] == EXPLORED:
                    explored_count += 1
        return explored_count
            
    def asess_reachble_counts(self):
        reachble_counts = {"up": 0, "down": 0, "left": 0, "right": 0}
        for move in ["up", "down", "left", "right"]:
            current_x,current_y = self.my_snake.head['x'],self.my_snake.head['y']
            next_x,next_y = current_x,current_y
            self.grid_copy_fill = copy.deepcopy(self.board.grid)
            if move == 'up':
                next_y += 1
            elif move == 'down':
                next_y -= 1
            elif move == 'left':
                next_x -= 1
            elif move == 'right':
                next_x += 1
            first_depth = 0
            food_count = 0
            tail_stop = False
            if self.board.is_food(current_x,current_y) == True:
                food_count = 1
                tail_stop = True
                food_id = self.board.get_food_id(current_x,current_y)
                self.food_candidates[food_id]['move'] = move
                self.food_candidates[food_id]['distant'] = 0
                reachble_counts[move] = self._count_reachble_ways(next_x,next_y,first_depth,move,food_count,tail_stop)
                self.food_candidates[food_id]['max_depth'] = reachble_counts[move]
            else:
                reachble_counts[move] = self._count_reachble_ways(next_x,next_y,first_depth,move,food_count,tail_stop)
            self.explored_counts[move] = self.count_explored()
        return reachble_counts

    def _count_reachble_ways(self,current_x,current_y,depth,first_move,food_count,tail_stop):
        if self.is_empty(current_x,current_y,tail_stop) == False or self.grid_copy[current_x][current_y] == EXPLORED:
            if depth == self.MAX_DEPTH and self.food_counts[first_move] > food_count:
                self.food_counts[first_move] = food_count
            return depth
        max_depth = depth
        current_cell = self.grid_copy[current_x][current_y]
        self.grid_copy[current_x][current_y] = EXPLORED
        self.grid_copy_fill[current_x][current_y] = EXPLORED
        tail_index = self.my_snake.length + food_count - depth - 2
        tail_x,tail_y = None,None

        tail_cell = None
        if tail_index >= 0:
            tail_x = self.my_snake.body[tail_index]['x']
            tail_y = self.my_snake.body[tail_index]['y']
            tail_cell = self.grid_copy[tail_x][tail_y]
            self.grid_copy[tail_x][tail_y] = MY_TAIL
        
        next_food_count = food_count
        next_tail_stop = False
        if self.board.grid[current_x][current_y] == FOOD:
            food_distant = depth
            next_food_count += 1
            next_tail_stop = True

        if depth < self.MAX_DEPTH:
            max_depth = max(self._count_reachble_ways(current_x + 1,current_y,depth + 1,first_move,next_food_count,next_tail_stop),
                            self._count_reachble_ways(current_x - 1,current_y,depth + 1,first_move,next_food_count,next_tail_stop), 
                            self._count_reachble_ways(current_x,current_y + 1,depth + 1,first_move,next_food_count,next_tail_stop),
                            self._count_reachble_ways(current_x,current_y - 1,depth + 1,first_move,next_food_count,next_tail_stop)) 
            
        if next_tail_stop == True and next_food_count == 1:  #if self.board.grid[current_x][current_y] == FOOD:
            food_id = self.board.get_food_id(current_x,current_y)
            if self.my_snake.health - food_distant > self.APPROACH_SAFE_SCOPE and max_depth == self.MAX_DEPTH and self.food_candidates[food_id]['distant'] <= food_distant and food_distant <= (self.MAX_DEPTH / 1.5):
                self.food_candidates[food_id]['move'] = first_move
                self.food_candidates[food_id]['distant'] = food_distant
                self.food_candidates[food_id]['max_depth'] = max_depth                    
        self.grid_copy[current_x][current_y] = current_cell
        if tail_index >= 0:
            self.grid_copy[tail_x][tail_y] = tail_cell
        return max_depth
    
    def is_empty(self,x,y,tail_stop):
        if x < 0 or y < 0 or x >= self.board.width or y >= self.board.height:
            return False
        if self.grid_copy[x][y] == SPACE or self.grid_copy[x][y] == FOOD or (self.grid_copy[x][y] == MY_TAIL and tail_stop == False and self.board.turn > 3):   #empty,food,tail
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
    HEALTH_LEVEL = max(12,my_snake.length)
    MAX_DEPTH = 8
    if my_snake.length >= 8:
        MAX_DEPTH = 12
    if my_snake.length >= 15:
        MAX_DEPTH = 14
    if my_snake.length >= 30:
        MAX_DEPTH = my_snake.length - 15
    TAIL_W = 2
    FOOD_W = 15
    if my_snake.length > 20:
        TAIL_W = 10
    #W_F,W_R,W_T = 1,1,1
    safe_moves = evaluater.get_safe_moves()
    if len(safe_moves) == 0:
        return None
    
    super_safe_moves = []
    best_move = None
    reachble_counts = evaluater.asess_reachble_counts()
    move_scores = {"up": 0, "down": 0, "left": 0, "right": 0}
    food_counts = evaluater.food_counts
    explored_counts = evaluater.explored_counts
    tail_distances = evaluater.asess_tail_distances()

    if my_snake.health > HEALTH_LEVEL:
        for move in safe_moves:
            if reachble_counts[move] == MAX_DEPTH:
                super_safe_moves.append(move)
                move_scores[move] = explored_counts[move] + (3 - food_counts[move]) * FOOD_W + tail_distances[move] * TAIL_W
        if len(super_safe_moves) == 0:
            move_scores = reachble_counts
        best_move = max(safe_moves, key=lambda move: move_scores[move])
        print_scores(reachble_counts,food_counts,explored_counts,tail_distances,move_scores)
    else:
        food_candidates = evaluater.food_candidates
        move_scores_sum = 0
        for food_candidate in food_candidates:
            print(food_candidate)
            move = food_candidate['move']
            if move != None and reachble_counts[move] == MAX_DEPTH:
                move_scores[move] = (4 - food_counts[move])*10 + (4 - tail_distances[move])*10
                move_scores_sum += move_scores[move]
        best_move = max(safe_moves, key=lambda move: move_scores[move])
        print_scores(reachble_counts,food_counts,explored_counts,tail_distances,move_scores)
        if move_scores_sum == 0:
            best_move = max(safe_moves, key=lambda move: reachble_counts[move])
    return best_move

def print_scores(reachble_counts,food_counts,explored_counts,tail_distances,move_scores):
    print(f"reachble count:\n{reachble_counts}")
    print(f"food counts:\n{food_counts}")
    print(f"explored counts:\n{explored_counts}")
    print(f"tail distances:\n{tail_distances}")
    print(f"move scores:\n{move_scores}")

# Start server when `python main.py` is run
if __name__ == "__main__":
    os.system('cls')
    from server import run_server
    run_server({"info": info, "start": start, "move": move, "end": end})