# Group14
# Python 3.12.3

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
        self.neck = self.body[1]
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
    
class Evaluator:
    def __init__(self,board,my_snake):
        self.board = board
        self.my_snake = my_snake
        self.grid_copy = copy.deepcopy(board.grid)
        self.grid_copy_fill = None
        self.food_candidates = []
        self.MAX_DEPTH = 8
        if self.my_snake.length >= 8:
            self.MAX_DEPTH = 9
        if self.my_snake.length >= 15:
            self.MAX_DEPTH = 12
        if self.my_snake.length >= 20:
            self.MAX_DEPTH = 13
        if self.my_snake.length >= 25:
            self.MAX_DEPTH = self.my_snake.length - 12

        self.food_counts = {"up": 3, "down": 3, "left": 3, "right": 3}
        self.explored_counts = {"up": 0, "down": 0, "left": 0, "right": 0}

    def get_food_next_counts(self):
        NEXT_FOOD_POINT = 2
        vectors = {"up": [0,1], "down": [0,-1], "left": [-1,0], "right": [1,0]}
        food_next_counts = {"up": 0, "down": 0, "left": 0, "right": 0}
        my_head_x = self.my_snake.head['x']
        my_head_y = self.my_snake.head['y']
        for move in ["up","down","left","right"]:
            for food in self.board.foods:
                if abs(my_head_x + vectors[move][0] - food['x']) + abs(my_head_y + vectors[move][1] - food['y']) == 1:
                    food_next_counts[move] += NEXT_FOOD_POINT
        return food_next_counts


    def get_direction_counts(self):
        direction_counts = {"up": 0, "down": 0, "left": 0, "right": 0}

        dx = self.my_snake.head['x'] - self.my_snake.neck['x'] 
        dy = self.my_snake.head['y'] - self.my_snake.neck['y']
        i = 1
        for i in range(2,min(self.my_snake.length - 1,6)):
            if self.my_snake.body[i]['x'] != self.my_snake.head['x'] - dx * i or  self.my_snake.body[i]['y'] != self.my_snake.head['y'] - dy * i:
                break

        if dx == 1 and dy == 0:
            direction_counts['right'] = i
        elif dx == -1 and dy == 0:
            direction_counts['left'] = i
        elif dx == 0 and dy == 1:
            direction_counts['up'] = i
        elif dx == 0 and dy == -1:
            direction_counts['down'] = i
        return direction_counts

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
    
    def asess_food_counts(self):
        return self.food_counts
    
    def asess_explored_counts(self):
        return self.explored_counts
    
    def get_food_candidates(self):
        return self.food_candidates

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
            if distance == 1:
                if self.my_snake.length >= 25:
                    tail_distances[move] = 0
                else:
                    tail_distances[move] = 2
            else:
                tail_distances[move] = distance - 1
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
                max_depth,total_food_count = self._count_reachble_ways(next_x,next_y,first_depth,move,food_count,tail_stop)
                reachble_counts[move] = max_depth
                self.food_candidates.appdnd({'move':move,'distant':0,'max_depth':max_depth,'food_count':total_food_count})          
            else:
                reachble_counts[move],total_food_count = self._count_reachble_ways(next_x,next_y,first_depth,move,food_count,tail_stop)
            self.explored_counts[move] = self.count_explored()
        return reachble_counts

    def _count_reachble_ways(self,current_x,current_y,depth,first_move,food_count,tail_stop):
        if self.is_empty(current_x,current_y,tail_stop) == False or self.grid_copy[current_x][current_y] == EXPLORED:
            return depth,food_count
        if depth == self.MAX_DEPTH:
            if self.food_counts[first_move] > food_count:
                self.food_counts[first_move] = food_count
            if self.grid_copy[current_x][current_y] != MY_TAIL:
                return depth + 2,food_count
            else:
                return depth + 1,food_count
            
        max_depth = depth

        tail_index = self.my_snake.length + food_count - depth - 2
        next_tail_x,next_tail_y,current_tail_x,current_tail_y = None,None,None,None

        next_tail_cell,current_tail_cell = None,None
        if tail_index >= 0:
            next_tail_x = self.my_snake.body[tail_index]['x']
            next_tail_y = self.my_snake.body[tail_index]['y']
            current_tail_x = self.my_snake.body[tail_index+1]['x']
            current_tail_y = self.my_snake.body[tail_index+1]['y']
            next_tail_cell = self.grid_copy[next_tail_x][next_tail_y]
            current_tail_cell = self.grid_copy[current_tail_x][current_tail_y]
            self.grid_copy[next_tail_x][next_tail_y] = MY_TAIL
            self.grid_copy[current_tail_x][current_tail_y] = SPACE

        current_cell = self.grid_copy[current_x][current_y]
        self.grid_copy[current_x][current_y] = EXPLORED
        self.grid_copy_fill[current_x][current_y] = EXPLORED

        next_food_count = food_count
        next_tail_stop = False
        if self.board.grid[current_x][current_y] == FOOD:
            food_distant = depth
            next_food_count += 1
            next_tail_stop = True

        min_food_count = 3

        if depth < self.MAX_DEPTH:
            for vector in [[1,0],[-1,0],[0,1],[0,-1]]:
                total_depth,total_food_count = self._count_reachble_ways(current_x + vector[0],current_y + vector[1],depth + 1,first_move,next_food_count,next_tail_stop)
                if max_depth < total_depth:
                    max_depth = total_depth
                    min_food_count = total_food_count
                elif  max_depth == total_depth and min_food_count > total_food_count:
                    max_depth = total_depth
                    min_food_count = total_food_count  

                if next_tail_stop == True and next_food_count == 1 and total_depth >= self.MAX_DEPTH:  #if self.board.grid[current_x][current_y] == FOOD:
                    self.food_candidates.append({'move':first_move,'distant':food_distant,'max_depth':max_depth,'food_count':total_food_count})               
                              
        self.grid_copy[current_x][current_y] = current_cell
        if tail_index >= 0:
            self.grid_copy[next_tail_x][next_tail_y] = next_tail_cell
            self.grid_copy[current_tail_x][current_tail_y] = current_tail_cell
        return max_depth,min_food_count
      
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
        print(f"MOVE {game_state['turn']}: {next_move}\n")
        return {"move": "down"}
    print(f"MOVE {game_state['turn']}: {next_move}\n")
    return {"move": next_move}

def choose_best_move(my_snake,evaluater):
    HEALTH_LEVEL = max(12,my_snake.length + 5)
    if my_snake.length >= 25:
        HEALTH_LEVEL = my_snake.length + 10
    MAX_DEPTH = evaluater.MAX_DEPTH
    TAIL_W = 1
    FOOD_W = 20
    FOOD_NEXT_W = 0
    if my_snake.length >= 25:
        FOOD_NEXT_W = 3
        TAIL_W = 1.5
    DIRECTION_W = 2

    safe_moves = evaluater.get_safe_moves()
    print("safe_moves:")
    print(safe_moves)
    if len(safe_moves) == 0:
        print(f"There is no safe moves!")
        return None
    
    super_safe_moves = []
    best_move = None

    reachble_counts = evaluater.asess_reachble_counts()
    move_scores = {"up": 0, "down": 0, "left": 0, "right": 0}
    direction_counts = evaluater.get_direction_counts()
    food_counts = evaluater.asess_food_counts()
    explored_counts = evaluater.asess_explored_counts()
    tail_distances = evaluater.asess_tail_distances()
    food_next_counts = evaluater.get_food_next_counts()

    if my_snake.health > HEALTH_LEVEL or my_snake.length >= 34:
        for move in safe_moves:
            if reachble_counts[move] >= MAX_DEPTH:
                super_safe_moves.append(move)
                move_scores[move] = (
                    explored_counts[move] + 
                    (3 - food_counts[move]) * FOOD_W - 
                    tail_distances[move] * TAIL_W + 
                    (reachble_counts[move] - MAX_DEPTH) * 2 - 
                    direction_counts[move] * DIRECTION_W - 
                    food_next_counts[move] * FOOD_NEXT_W
                )

        if len(super_safe_moves) == 0:
            move_scores = reachble_counts

        best_move = max(safe_moves, key=lambda move: move_scores[move])
        #print_scores(reachble_counts,food_counts,explored_counts,tail_distances,direction_counts,move_scores)
    else:
        food_candidates = evaluater.get_food_candidates()
        best_food_count = 3
        best_food_distant = 0
        best_space = 0
        best_direction = 6
        best_tail = 12
    
        APPROACH_MARGIN = 0
        if my_snake.length >= 20:
            APPROACH_MARGIN = 2
        if my_snake.length >= 30:
            APPROACH_MARGIN = my_snake.length / 10
        MAX_DEPTH_MARGIN = 1
        if my_snake.length >= 25:
            MAX_DEPTH_MARGIN = 1.1


        primary_candidates = [
            food_candidate for food_candidate in food_candidates
            if (
                food_candidate['move'] != None and 
                food_candidate['max_depth'] == MAX_DEPTH + 2 and 
                food_candidate['distant'] <= MAX_DEPTH / MAX_DEPTH_MARGIN and
                food_candidate['distant'] < my_snake.health - APPROACH_MARGIN
            )
        ]

        target_candidates = None
        if primary_candidates:
            target_candidates = primary_candidates
        else:
            target_candidates = [
                food_candidate for food_candidate in food_candidates
                if(
                    food_candidate['move'] != None and
                    food_candidate['max_depth'] > MAX_DEPTH and  
                    food_candidate['distant'] < my_snake.health           
                )
            ]

        AVOID_LENGTH_LEVEL = 10
        if my_snake.length <= AVOID_LENGTH_LEVEL:
            for target_candidate in target_candidates:
                #print(target_candidate)
                move = target_candidate['move']
                distant = target_candidate['distant']
                food_count = target_candidate['food_count']
                if food_count < best_food_count or (distant >= best_food_distant and food_count <= best_food_count):
                    best_food_count = food_count
                    best_food_distant = distant
                    best_move = move
        else:
            for target_candidate in target_candidates:
                #print(target_candidate)
                move = target_candidate['move']
                distant = target_candidate['distant']
                space = explored_counts[move] 
                direction = direction_counts[move]
                food_count = target_candidate['food_count']
                if food_count < best_food_count or (distant >= best_food_distant and food_count <= best_food_count and  best_space <= space and best_direction >= direction):
                    best_food_count = food_count
                    best_food_distant = distant
                    best_move = move
                    best_space = space
                    best_direction = direction

        if best_move == None:
            for move in safe_moves:
                if reachble_counts[move] >= MAX_DEPTH and my_snake.length <= 25:
                    super_safe_moves.append(move)
                    move_scores[move] = explored_counts[move] + (3 - food_counts[move]) * FOOD_W - direction_counts[move] * DIRECTION_W + TAIL_W * tail_distances[move]
                elif reachble_counts[move] >= MAX_DEPTH and my_snake.length > 25:
                    super_safe_moves.append(move)
                    move_scores[move] = explored_counts[move] + (3 - food_counts[move]) * FOOD_W - direction_counts[move] * DIRECTION_W - TAIL_W * tail_distances[move]
            if len(super_safe_moves) == 0:
                move_scores = reachble_counts
            best_move = max(safe_moves, key=lambda move: move_scores[move])
        #print_scores(reachble_counts,food_counts,explored_counts,tail_distances,direction_counts,move_scores)
    return best_move

def print_scores(reachble_counts,food_counts,explored_counts,tail_distances,direction_counts,move_scores):
    print(f"reachble count:\n{reachble_counts}")
    print(f"food counts:\n{food_counts}")
    print(f"explored counts:\n{explored_counts}")
    print(f"tail distances:\n{tail_distances}")
    print(f"direction counts:\n{direction_counts}")
    #print(f"food_next_counts:\n{food_next_counts}")
    print(f"move scores:\n{move_scores}")

# Start server when `python main.py` is run
if __name__ == "__main__":
    #os.system('cls')
    from server import run_server
    run_server({"info": info, "start": start, "move": move, "end": end})