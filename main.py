# Group14
# Python 3.12.3

from hmac import new
from tarfile import NUL
from tkinter import Grid
import typing
import copy
from enum import Enum
import time
import os
import random


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#4B89C8",  # TODO: Choose color
        "head": "missile",  # TODO: Choose head
        "tail": "missile",  # TODO: Choose tail
    }

# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")

# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")

# Constant values

MAX_HEALTH = 100
WIDTH = HEIGHT = 11

class Snake:
    def __init__(self, snake):
        self.id = snake["id"]
        self.name = snake["name"]
        self.body = snake["body"]
        self.length = snake["length"]
        self.health = snake["health"]
        self.head = self.body[0]
        self.neck = self.body[1] if len(self.body) > 1 else None
        self.tail = self.body[-1]
class Board:
    def __init__(self,game_state,my_snake,enemy_snake):
        self.width = game_state['board']['width']
        self.height = game_state['board']['height']
        self.foods = game_state["board"]["food"]
        self.turn = game_state['turn']
        self.grid = [[GridState.SPACE for j in range(self.width)] for i in range(self.height)]
        self.my_snake = my_snake
        self.enemy_snake = enemy_snake
        self.grid_copy = copy.deepcopy(self.grid)
        self._init_grid()

    def _init_grid(self):
        for food in self.foods:
            self.grid[food['x']][food['y']] = GridState.FOOD
        self.grid[self.my_snake.head['x']][self.my_snake.head['y']] = GridState.MY_HEAD
        self.grid[self.my_snake.tail['x']][self.my_snake.tail['y']] = GridState.MY_TAIL
        self.grid[self.enemy_snake.head['x']][self.enemy_snake.head['y']] = GridState.ENEMY_HEAD
        self.grid[self.enemy_snake.tail['x']][self.enemy_snake.tail['y']] = GridState.ENEMY_TAIL
        for i in range(1,self.my_snake.length - 1):
            self.grid[self.my_snake.body[i]['x']][self.my_snake.body[i]['y']] = GridState.MY_BODY

        for i in range(1,self.enemy_snake.length - 1):
            self.grid[self.enemy_snake.body[i]['x']][self.enemy_snake.body[i]['y']] = GridState.ENEMY_BODY

    def is_empty(self, x, y):
        if not self.check_range(x, y):
            return False

        solo_safe = (self.grid[x][y] in [GridState.SPACE, GridState.FOOD] or
                    (self.grid[x][y] == GridState.MY_TAIL and self.my_snake.health < MAX_HEALTH and self.turn > 3))

        if not solo_safe:
            return False

        if self.my_snake.length <= self.enemy_snake.length:
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if self.check_range(nx, ny) and self.grid[nx][ny] == GridState.ENEMY_HEAD:
                    return False
        return True   
        
    def check_range(self,x,y):
        return x >= 0 and y >= 0 and x < self.width and y < self.height
    
    def is_food(self,x,y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        if self.grid[x][y] == GridState.FOOD:
            return True
        else:
            return False       
    
class Evaluator:
    def __init__(self,board,my_snake):
        self.board = board
        self.my_snake = my_snake
        
    def get_safe_moves(self):
        is_move_safe = {"U": True, "D": True, "L": True, "R": True}
        if self.board.is_empty(self.my_snake.head['x'] + 1,self.my_snake.head['y']) == False:
            is_move_safe['R'] = False
        if self.board.is_empty(self.my_snake.head['x'] - 1,self.my_snake.head['y']) == False:
            is_move_safe['L'] = False
        if self.board.is_empty(self.my_snake.head['x'],self.my_snake.head['y'] + 1) == False:
            is_move_safe['U'] = False        
        if self.board.is_empty(self.my_snake.head['x'],self.my_snake.head['y'] - 1) == False:
            is_move_safe['D'] = False
        safe_moves = []
        for move, isSafe in is_move_safe.items():
            if isSafe:
                safe_moves.append(move)
        return safe_moves
    
    def get_best_food(self):
        my_snake_head_x = self.my_snake.head['x']
        my_snake_head_y = self.my_snake.head['y']
        min_food_distant = self.board.width + self.board.height
        best_food = None
        food_distant = None
        for food in self.board.foods:
            food_distant = abs(my_snake_head_x - food['x']) + abs(my_snake_head_y - food['y'])
            if min_food_distant >= food_distant:
                min_food_distant = food_distant
                best_food = food
        return best_food
    
    def get_food_directions(self):
        FOOD_POINT = 1
        food_directions = {'U': 0, 'D' : 0, 'L' : 0, 'R' : 0}
        food = self.get_best_food()
        if food == None :
            return food_directions
        if food['x'] > self.my_snake.head['x']:
            food_directions["R"] += FOOD_POINT
        elif food['x'] < self.my_snake.head['x']:
            food_directions["L"] += FOOD_POINT
        if food['y'] > self.my_snake.head['y']:
            food_directions["U"] += FOOD_POINT
        elif food['y'] < self.my_snake.head['y']:
            food_directions["D"] += FOOD_POINT   
        return food_directions
      
    def is_empty(self,x,y,tail_stop):
        if x < 0 or y < 0 or x >= self.board.width or y >= self.board.height:
            return False
        if self.grid_copy[x][y] == GridState.SPACE or self.grid_copy[x][y] == GridState.FOOD or (self.grid_copy[x][y] == GridState.MY_TAIL and tail_stop == False and self.board.turn > 3):   #empty,food,tail
            return True
        else:
            return False   

class GridState(Enum):
    SPACE = 0
    FOOD = -1
    MY_EXPLORED = 4
    ENEMY_EXPLORED = 5
    MY_HEAD = 1
    MY_BODY = 2
    MY_TAIL = 3
    ENEMY_HEAD = 11
    ENEMY_BODY = 12
    ENEMY_TAIL = 13

class Result(Enum):
    LOSE = -1
    SAFE = 0
    WIN  = 1

DIRS = {
    "U": (0, 1),
    "D": (0, -1),
    "L": (-1, 0),
    "R": (1, 0)
}

STRING_DIRS_CONVERSION = {
    "U": "up",
    "D": "down",
    "L": "left",
    "R": "right"
}

class Stats:
    def __init__(self):
        self.my_dead = False
        self.enemy_dead = False
        self.my_move_sum = 0
        self.enemy_move_sum = 0
        self.node_count = 0

class Simulator:
    def __init__(self,board,my_snake,enemy_snake):
        self.board = board
        self.grid = copy.deepcopy(board.grid)
        self.width = board.width
        self.height = board.height
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[x][y] in (GridState.MY_BODY,GridState.MY_HEAD):
                    self.grid[x][y] = GridState.MY_EXPLORED
                if self.grid[x][y] in (GridState.ENEMY_BODY,GridState.ENEMY_HEAD):
                    self.grid[x][y] = GridState.ENEMY_EXPLORED
        self.my_body = copy.deepcopy(my_snake.body)
        self.enemy_body = copy.deepcopy(enemy_snake.body)
        self.my_head = my_snake.head
        self.enemy_head = enemy_snake.head
        self.my_health = my_snake.health
        self.enemy_health = enemy_snake.health
        self.my_tail_stop = False
        self.enemy_tail_stop = False
        self.my_length = my_snake.length
        self.enemy_length = enemy_snake.length
        self.MAX_DEPTH = 4

    def check_range(self,x,y):
        return 0 <= x < self.width and 0 <= y < self.height
    
    def legal_moves(self,x, y,my_tail_stop,enemy_tail_stop):
        moves = []
        for d, (dx, dy) in DIRS.items():
            nx = x + dx
            ny = y + dy
            if self.check_range(nx, ny) and self.is_empty(nx,ny,my_tail_stop,enemy_tail_stop):
                moves.append((d, nx, ny))
        return moves
    
    def dfs(self,depth,my_food_count,enemy_food_count,mx,my,ex,ey,my_tail_stop,enemy_tail_stop):
        if depth == self.MAX_DEPTH:
            return        
        my_moves  = self.legal_moves(mx,my,my_tail_stop,enemy_tail_stop)
        enemy_moves = self.legal_moves(ex,ey,my_tail_stop,enemy_tail_stop)

        self.stats.my_move_sum  += len(my_moves)
        self.stats.enemy_move_sum += len(enemy_moves)
        self.stats.node_count   += 1

        for _, mnx, mny in my_moves:
            for _, enx, eny in enemy_moves:
                my_dead,enemy_dead = self.judge_death(depth,mnx,mny,enx,eny,my_food_count,enemy_food_count,my_tail_stop,enemy_tail_stop)
                if not my_dead and not enemy_dead:
                    changed,my_ate,enemy_ate,removed_my_tail,removed_enemy_tail = self.apply_move(mnx,mny,enx,eny,my_tail_stop,enemy_tail_stop)
                    if my_ate:
                        my_food_count += 1
                    if enemy_ate:
                        enemy_food_count += 1
                    self.dfs(depth + 1,my_food_count,enemy_food_count,mnx,mny,enx,eny,my_ate,enemy_ate)
                    self.undo(changed,removed_my_tail,removed_enemy_tail)

    def is_empty(self, x, y, my_tail_stop, enemy_tail_stop):
        state = self.grid[x][y]

        if state in (GridState.SPACE, GridState.FOOD):
            return True
        if state == GridState.MY_TAIL:
            return not my_tail_stop
        if state == GridState.ENEMY_TAIL:
            return not enemy_tail_stop
        return False    

    def judge_death(self,depth,mnx,mny,enx,eny,my_food_count,enemy_food_count,my_tail_stop,enemy_tail_stop):
        my_dead  = not (self.check_range(mnx, mny) and self.is_empty(mnx,mny,my_tail_stop,enemy_tail_stop)) or self.my_health - depth + my_food_count*100 < 1
        enemy_dead = not (self.check_range(enx, eny) and self.is_empty(enx,eny,my_tail_stop,enemy_tail_stop)) or self.enemy_health - depth + enemy_food_count*100 < 1

        my_length = len(self.my_body)
        enemy_length = len(self.enemy_body)
        if (mnx, mny) == (enx, eny):
            if my_length >= enemy_length:
                enemy_dead = True
            if my_length <= enemy_length:
                my_dead = True
        return my_dead,enemy_dead

    def apply_move(self,mnx,mny,enx,eny,my_tail_stop,enemy_tail_stop):
        changed = []
        my_ate = (self.grid[mnx][mny] == GridState.FOOD)
        enemy_ate = (self.grid[enx][eny] == GridState.FOOD)

        for x, y in [(mnx, mny), (enx, eny)]:
            changed.append((x, y, self.grid[x][y]))
        
        self.grid[mnx][mny] = GridState.MY_EXPLORED
        self.grid[enx][eny] = GridState.ENEMY_EXPLORED

        self.my_body.insert(0,{"x": mnx, "y": mny})
        self.enemy_body.insert(0,{"x": enx, "y": eny})
        removed_my_tail,removed_enemy_tail = None,None

        if not my_tail_stop:
            removed_my_tail,tx, ty = self.pop_my_tail()
            new_tail = self.my_body[-1]
            ntx,nty = new_tail['x'],new_tail['y']
            changed.append((tx, ty, self.grid[tx][ty]))
            changed.append((ntx,nty,self.grid[ntx][nty]))
            self.grid[tx][ty] = GridState.SPACE
            self.grid[ntx][nty] = GridState.MY_TAIL

        if not enemy_tail_stop:
            removed_enemy_tail,tx, ty = self.pop_enemy_tail()
            new_tail = self.enemy_body[-1]
            ntx,nty = new_tail['x'],new_tail['y']
            changed.append((tx, ty, self.grid[tx][ty]))
            changed.append((ntx,nty,self.grid[ntx][nty]))
            self.grid[tx][ty] = GridState.SPACE
            self.grid[ntx][nty] = GridState.ENEMY_TAIL

        return changed, my_ate, enemy_ate,removed_my_tail,removed_enemy_tail
    
    def undo(self,changed,removed_my_tail,removed_enemy_tail):
        for x, y, old in changed:
            self.grid[x][y] = old
        if removed_my_tail is not None:
            self.my_body.append(removed_my_tail)
        if removed_enemy_tail is not None:
            self.enemy_body.append(removed_enemy_tail)
        self.my_body.pop(0)
        self.enemy_body.pop(0)

    def pop_my_tail(self):
        tail_state = self.my_body.pop()
        return tail_state,tail_state['x'] , tail_state['y']
    def pop_enemy_tail(self):
        tail_state = self.enemy_body.pop()
        return tail_state,tail_state['x'] , tail_state['y']

    def evaluate_first_moves(self):
        result = {}
        depth = 0
        mx,my = self.my_head['x'],self.my_head['y']
        ex,ey = self.enemy_head['x'],self.enemy_head['y']
        my_food_count = 0
        enemy_food_count = 0
        my_tail_stop,enemy_tail_stop = False,False
        if self.grid[mx][my] == GridState.FOOD:
            my_food_count += 1
            my_tail_stop = True
        if self.grid[ex][ey] == GridState.FOOD:
            enemy_food_count += 1
            enemy_tail_stop = True
        
        my_moves = self.legal_moves(mx,my,my_tail_stop,enemy_tail_stop)
        enemy_moves = self.legal_moves(ex,ey,my_tail_stop,enemy_tail_stop)
        
        for d, mnx, mny in my_moves:
            self.stats = Stats()
            self.stats.node_count   += 1

            for _, enx, eny in enemy_moves:
                my_dead,enemy_dead = self.judge_death(depth,mnx,mny,enx,eny,my_food_count,enemy_food_count,my_tail_stop,enemy_tail_stop)
                if not my_dead and not enemy_dead:
                    changed,my_ate,enemy_ate,removed_my_tail,removed_enemy_tail = self.apply_move(mnx,mny,enx,eny,my_tail_stop,enemy_tail_stop)
                    if my_ate:
                        my_food_count += 1
                    if enemy_ate:
                        enemy_food_count += 1
                    self.dfs(depth + 1,my_food_count,enemy_food_count,mnx,mny,enx,eny,my_ate,enemy_ate)
                    self.undo(changed,removed_my_tail,removed_enemy_tail)
            result[d] = copy.copy(self.stats)
        return result

# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    board_snakes = game_state["board"]["snakes"]

    if len(board_snakes) < 2:
        return {"move": "down"}

    my_snake = Snake(game_state["you"])

    enemy_raw = next(
        snake for snake in board_snakes
        if snake["id"] != game_state["you"]["id"]
    )
    enemy_snake = Snake(enemy_raw)

    board = Board(game_state,my_snake,enemy_snake)
    evaluator = Evaluator(board,my_snake)
    simulator = Simulator(board,my_snake,enemy_snake)

    next_move = choose_best_move(board,evaluator,simulator)

    if next_move == None:
        print(f"MOVE {game_state['turn']}: {next_move}\n")
        return {"move": "down"}
    print(f"MOVE {game_state['turn']}: {next_move}\n")
    return {"move": next_move}

def choose_best_move(board,evaluater,simulator):
    FOOD_W = 200
    safe_moves = evaluater.get_safe_moves()
    food_directions = evaluater.get_food_directions()
    result = simulator.evaluate_first_moves()
    my_free = {}
    enemy_free = {}
    for d, s in result.items():
        if s.my_dead:
            life = "LOSE"
        elif s.enemy_dead:
            life = "WIN"
        else:
            life = "SAFE"

        my_free[d] =  s.my_move_sum  
        enemy_free[d]  = s.enemy_move_sum 
    print("myfree, enemyfree :")
    print(my_free, enemy_free)
    print("safe_moves:")
    print(safe_moves)
    print("food_directions")
    print(food_directions)
    if len(safe_moves) > 0:
        best_move = max(safe_moves, key=lambda move: my_free[move] - enemy_free[move] + food_directions[move] * FOOD_W)
        return STRING_DIRS_CONVERSION[best_move]
    else:
        return None


# Start server when `python main.py` is run
if __name__ == "__main__":
    os.system('cls')
    from server import run_server
    run_server({"info": info, "start": start, "move": move, "end": end})