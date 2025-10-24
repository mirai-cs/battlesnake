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
        if self.grid[x][y] == SPACE or self.grid[x][y] == FOOD or (self.grid[x][y] == MY_TAIL and  self.my_snake.health < MAX_HEALTH and self.turn > 3):   #empty,food,tail
            return True
        else:
            return False      
        
    def is_food(self,x,y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        if self.grid[x][y] == FOOD:   #empty,food,tail
            return True
        else:
            return False       

class Evaluator:
    def __init__(self,board,my_snake):
        self.is_move_safe = {"up": True, "down": True, "left": True, "right": True}
        self.safe_moves = []
        #food_points : tendency to approach foods
        self.food_points = {"up": 1, "down": 1, "left": 1, "right": 1}
        #reachble_counts : to assess the size of the space
        self.reachble_counts = {"up": 0, "down": 0, "left": 0, "right": 0}
        #tail_points : tendency to approach my tail
        self.tail_points = {"up": 1, "down": 1, "left": 1, "right": 1}

        self.move_scores = {"up": 0, "down": 0, "left": 0, "right": 0}
        self.board = board
        self.my_snake = my_snake
        self.grid_copy = copy.deepcopy(self.board.grid)

    def asess_safety(self):
        if self.board.is_empty(self.my_snake.head['x'] + 1,self.my_snake.head['y']) == False:
            self.is_move_safe['right'] = False
        if self.board.is_empty(self.my_snake.head['x'] - 1,self.my_snake.head['y']) == False:
            self.is_move_safe['left'] = False
        if self.board.is_empty(self.my_snake.head['x'],self.my_snake.head['y'] + 1) == False:
            self.is_move_safe['up'] = False        
        if self.board.is_empty(self.my_snake.head['x'],self.my_snake.head['y'] - 1) == False:
            self.is_move_safe['down'] = False

    def set_move_safes(self):
        for move, isSafe in self.is_move_safe.items():
            if isSafe:
                self.safe_moves.append(move)

    def asess_food_points(self):
        health_level = 20
        FOOD_PENALTY = -1
        if(self.my_snake.length >= 12):
            FOOD_PENALTY = 0.1
        if(self.my_snake.length >= 16):
            FOOD_PENALTY = 0.3
        my_head_x = self.my_snake.head['x']
        my_head_y = self.my_snake.head['y']
        if self.my_snake.health > health_level :   #when snake avoid foods
            if self.board.is_food(my_head_x + 1,my_head_y):
                self.food_points['right'] = FOOD_PENALTY
            if self.board.is_food(my_head_x - 1,my_head_y):
                self.food_points['left'] = FOOD_PENALTY
            if self.board.is_food(my_head_x,my_head_y + 1):
                self.food_points['up'] = FOOD_PENALTY
            if self.board.is_food(my_head_x,my_head_y - 1):
                self.food_points['down'] = FOOD_PENALTY      
        else:   #when snake aproach foods
            min_food = {"x": 0, "y": 0}
            min_distance = 12
            # set min_food and min_disatance
            for food in self.board.foods: 
                distance = abs(my_head_x - food['x']) + abs(my_head_y - food['y'])
                if distance <= min_distance:
                    min_food = food
                    min_distance = distance
            if min_food['x'] > my_head_x:
                self.food_points["right"] += (min_food['x'] - my_head_x) * (health_level - self.my_snake.health)
            else:
                self.food_points["left"] += (my_head_x - min_food['x']) * (health_level - self.my_snake.health)
            if min_food['y'] > my_head_y:
                self.food_points["up"] += (min_food['y'] - my_head_y) * (health_level - self.my_snake.health)
            else:
                self.food_points["down"] += (my_head_y - min_food['y']) * (health_level - self.my_snake.health)

    def asess_tail_points(self):
        TAIL_BOUNAUS = 1.5
        if self.my_snake.tail['y'] > self.my_snake.head['y']:
            self.tail_points['up'] = TAIL_BOUNAUS
        elif self.my_snake.tail['y'] < self.my_snake.head['y']:
            self.tail_points['down'] = TAIL_BOUNAUS
        if self.my_snake.tail['x'] > self.my_snake.head['x']:
            self.tail_points['right'] = TAIL_BOUNAUS
        elif self.my_snake.tail['x'] < self.my_snake.head['x']:
            self.tail_points['left'] = TAIL_BOUNAUS
            
    def asess_reachble_counts(self):
        for move in self.safe_moves:
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
            self.reachble_counts[move] = self.count_reachble_ways(next_x,next_y,current_depth)

    def count_reachble_ways(self,next_x,next_y,depth):
        if self.is_empty(next_x,next_y) == False or self.grid_copy[next_x][next_y] == EXPLORED:
            return depth
        self.grid_copy[next_x][next_y] = EXPLORED
        tail_index = self.my_snake.length - depth - 1
        tail_x,tail_y = None,None
        if tail_index >= 0:
            tail_x = self.my_snake.body[tail_index]['x']
            tail_y = self.my_snake.body[tail_index]['y']
            self.grid_copy[tail_x][tail_y] = SPACE
        if depth == 10:
            self.grid_copy[next_x][next_y] = self.board.grid[next_x][next_y]
            if tail_x is not None:
                self.grid_copy[tail_x][tail_y] = self.board.grid[tail_x][tail_y]
            return depth
        else: 
            max_depth = depth
            max_depth =  max(self.count_reachble_ways(next_x + 1,next_y,depth + 1), self.count_reachble_ways(next_x - 1,next_y,depth + 1) , self.count_reachble_ways(next_x,next_y + 1,depth + 1) , self.count_reachble_ways(next_x,next_y - 1,depth + 1) ) 
            self.grid_copy[next_x][next_y] = self.board.grid[next_x][next_y]
            if tail_x is not None:
                self.grid_copy[tail_x][tail_y] = self.board.grid[tail_x][tail_y]
            return max_depth
            
    def calculate_scores(self):
        self.asess_safety()
        self.set_move_safes()
        self.asess_food_points()
        self.asess_reachble_counts()
        self.asess_tail_points()
        for move in self.safe_moves:
            self.move_scores[move] = self.food_points[move] * self.reachble_counts[move] * self.tail_points[move]

    def get_next_move(self):
        if len(self.safe_moves) == 0:
            return None
        next_move = max(self.safe_moves, key=lambda move: self.move_scores[move])
        return next_move
    
    def print_scores(self,reachble_counts_flag,food_points_flag,tail_points_flag,move_scores_flag):
        print(self.is_move_safe)
        if(reachble_counts_flag == 1):
            print("reachble count:")
            print(self.reachble_counts)
        if(food_points_flag == 1):
            print("food points:")
            print(self.food_points)
        if(tail_points_flag == 1):
            print("tail points:")
            print(self.tail_points)
        if(move_scores_flag == 1):
            print("move scores:")
            print(self.move_scores)

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

    evaluator.calculate_scores()
    evaluator.print_scores(1,1,1,1)
    next_move = evaluator.get_next_move()

    if next_move == None:
        print(f"There is no safe moves!")
        print(f"MOVE {game_state['turn']}: {next_move}\n")
        return {"move": "down"}
    else:
        print(f"MOVE {game_state['turn']}: {next_move}\n")
        return {"move": next_move}

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server
    run_server({"info": info, "start": start, "move": move, "end": end})