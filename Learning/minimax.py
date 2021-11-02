# Tutorial video I watched
# https://www.youtube.com/watch?v=fInYh90YMJU

# Creates minimax algorithm for a game where
# There are 11 sticks and two players
# each player gets to pick up either one or
# two sticks and the goal of the game is to
# pick up the last stick

from sys import maxsize

INF = maxsize

# Tree creator
class Node:

    def __init__(self, depth, player_num, sticks_remaining, value=0):
        # depth at which the tree will go
        # i.e. tree will only look 3 moves ahead if
        # depth = 3
        self.depth = depth
        # player_num is either positive or negative 1
        self.player_num = player_num
        # sticks remaining in the game
        self.sticks_remaining = sticks_remaining
        # value that each node holds- this
        # is the gamestate, in this example
        # it is either 0, +infinity, or -infinity
        self.value = value
        self.children = []
        self.create_children()

    def create_children(self):
        if self.depth >= 0:
            # loops over all possible moves
            # in this game it is only pulling
            # one stick or two sticks
            for i in range(1, 3): 
                # do the move then get the real
                # value of the gamestatethat to the list of children
                move = self.sticks_remaining - i
                self.children.append(Node(self.depth - 1, -self.player_num, move, self.real_val(move)))

    def real_val(self, sticks):
        # if there are 0 sticks remaining,
        # then the player who's turn it is wins
        # if there are less than 0, then they lose
        # otherwise the value of this node is 0 (neutral)
        if sticks == 0:
            return INF * self.player_num
        elif sticks < 0:
            return INF * -self.player_num
        return 0

# Minimax algorithm
def minimax(node, depth, player_num):
    # passes the best choice up to the parent node
    if (depth == 0) or (abs(node.value) == INF):
        return node.value
    
    # worst value to start, because the
    # algorithm will check if any move is
    # better than this "best_value", and if it
    # is, it will change the best_value to 
    # that new value, and repeat
    best_value = INF * -player_num

    for child in node.children:
        # "drills" to the bottom of the tree
        # reducing depth, and flipping players as it goes,
        # the algorithm will return a value either when
        # it reaches depth == 0 or when it reaches infinity
        val = minimax(child, depth-1, -player_num)
        if abs(INF * player_num - val) < abs(INF * player_num - best_value):
            best_value = val

    # returns the best move from the node given
    return best_value

# GAME

# checks if a players has won
def check_win(sticks, player_num) -> bool:
    if sticks <= 0:
        if player_num > 0:
            if sticks == 0:
                print("You win!")
            else:
                print("You lose!")
        else:
            if sticks == 0:
                print("Computer wins!")
            else:
                print("Computer loses!")
        return True
    return False

# Runs only when this file is ran
# Not run when imported
def main():
    stick_total = 11
    depth = 4
    current_player = 1
    while stick_total > 0:
        print(f"{stick_total} sticks remain. How many do you want to draw?")
        choice = input("1 or 2: ")
        stick_total -= int(float(choice))
        if not check_win(stick_total, current_player): 
            # now it is the computer's turn
            current_player *= -1
            node = Node(depth, current_player, stick_total)
            # best_choice is the actual move that will be played
            # best_value is the best value of the nodes, these
            # are not the same
            best_choice = -100
            best_value = INF * -current_player
            for i in range(len(node.children)):
                child = node.children[i]
                val = minimax(child, depth, -current_player)
                if (abs(current_player * INF - val) <= abs(current_player * INF - best_value)):
                    best_value = val
                    best_choice = i + 1
            print(f"Computer pulls: {str(best_choice)} sticks")
            stick_total -= best_choice
            check_win(stick_total, current_player)
            current_player *= -1



if __name__ == "__main__":
    main()

