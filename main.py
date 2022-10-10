# This program is creating a template for a monte carlo tree

# Things that includes:

# - game states, i.e. the nodes of the tree
# - the tree itself

import random
import numpy as np


# Things a game state needs:
# - the literal game state (board)
# - whose turn it is
# - pointer to the parent (if it exists)
# - pointers to the children (if they exist)
# - a total score
# - a counter to keep track of the number of visits
# - a method to calculate UCBI
# - a method that expands a node
# - a method that finds highestUCBI

# note: what is UCBI? It's a way to balance between exploration and exploitation.
# Exploitation side is the average value (self.total/self.visits)
# Exploration side is 2 * √(ln(visits to parent)/visits to child)
# UCBI is sum of Exploitation value + Exploration value
class GameState:

    def __init__(self, board, player = None):
        self.board = board
        self.total = 0
        self.visits = 0
        self.player = player

        self.parent = None
        self.children = []
        self.leaf = False

        if hasWon(self.board, userPlayer):
            self.total = -50
            self.visits = 0
            self.leaf = True
        elif hasWon(self.board, getNextPlayer(userPlayer)):
            self.total = 50
            self.visits = 0
            self.leaf = True


    def setParent(self, parentState):
        self.parent = parentState
        self.player = getNextPlayer(parentState.player)
        parentState.addChild(self)
        if hasWon(self.board, userPlayer):
            self.total = -50
            self.visits = 0
            self.leaf = True
        elif hasWon(self.board, getNextPlayer(userPlayer)):
            self.total = 50
            self.visits = 0
            self.leaf = True

    def addChild(self, childState):
        self.children.append(childState)

    def roll(self):
        if self.leaf:
            self.visits = -1
            return self.total
        return simulate(self.board, getNextPlayer(self.player))

    def addToTotal(self, newValue):
        self.total += newValue

        # now we have to update the parent as well
        # to do this, we'll use a bit of recursion!

        # base case:
        if self.parent == None:
            return
        # recursive step:
        else:
            self.parent.addToTotal(newValue)

    def addVisit(self):
        self.visits += 1

        # same as above
        # base case:
        if self.parent == None:
            return
        # recursive step:
        else:
            self.parent.addVisit()

    def calculateUCBI(self):

        if self.visits == np.Infinity:
            return np.Infinity

        # Formula:
        # average value + 10*√(ln(visits to parent)/visits to child)

        # THINGS THAT CAN BE 0
        # - self.visits -> return infinity because we have a fully unexplored branch
        # - self.parent -> CANNOT BE NONE because then this would never get called!
        # - self.total -> doesn't cause 0 division errors so we don't care

        if self.visits == 0:
            if self.player != userPlayer:
                return -np.Infinity
            return np.Infinity

        else:
            try:
                exploitationValue = self.total / self.visits
            except:
                exploitationValue = self.total // (self.visits)

            # NOTE: np.log is actually ln(), np.log10 is standard log()
            explorationValue = 50 * np.sqrt(np.log(self.parent.visits)/self.visits)

            if self.player != userPlayer:
                explorationValue *= -1

            try:
                return exploitationValue + explorationValue
            except:
                return 1 * 10**200


    def getChildrenUCBIs(self):
        childScores = []

        for child in self.children:
            childScores.append(child.calculateUCBI())

        return childScores

    def findHighestUCBILeaf(self):

        # base case:
        if self.visits == 0 and self.parent != None:
            return self

        # recursive step(s):
        if self.children == []:
            self.expand()
            try:
                return self.children[0]
            except:
                return self

        else:
            UCBIs = self.getChildrenUCBIs()
            favoriteChild = 0

            if self.player != userPlayer:
                max = UCBIs[0]

                for childNum in range(len(UCBIs)):
                    if UCBIs[childNum] > max:
                        favoriteChild = childNum
                        max = UCBIs[childNum]

            else:
                min = UCBIs[0]

                for childNum in range(len(UCBIs)):
                    if UCBIs[childNum] < min:
                        favoriteChild = childNum
                        min = UCBIs[childNum]

            return self.children[favoriteChild].findHighestUCBILeaf()


    def expand(self):
        nextMoves = getNextMoves(self.board, self.player)

        for nextState in nextMoves:
            newState = GameState(getBoardCopy(nextState))
            newState.setParent(self)

# Things a MCTree needs:
# - root node -> this will point to all the other nodes
# - iterate() function that updates the values
# - makeChoice(x) function that iterates x times and picks out the best branch

# note: to write this, we need to assume that a few game-specific functions exist

class MCTree:

    def __init__(self, start):

        # note: this root is likely going to be a part of a different tree. So we can't just reuse it – we need to reset the total and visits
        self.root = start #GameState(start.board, start.player)
        self.root.expand()

        """print("ROOT")
        printBoard(self.root.board)"""

    def iterate(self):
        leafToUpdate = self.root.findHighestUCBILeaf()

        score = leafToUpdate.roll()

        leafToUpdate.addToTotal(score)
        leafToUpdate.addVisit()

    def makeChoice(self, iterations):
        for iteration in range(iterations):
            self.iterate()

        childScores = []

        for child in self.root.children:
            try:
                childScores.append(child.total / child.visits)
            except:
                childScores.append(child.total)

        approved = 0
        try:
            max = childScores[0]

            for item in range(len(childScores)):
                if childScores[item] > max:
                    approved = item
                    max = childScores[item]
            #print(approved)
            return [self.root.children[approved].board, max]

        except:
            #print("except")
            return [self.root.children[0].board, 50]










## GAME SPECIFIC FUNCTIONS ## (right now tic tac toe)

# Takes in the currentPlayer, returns the next player
def getNextPlayer(currentPlayer):
    if currentPlayer == 'X':
        return 'O'

    return 'X'

# Takes in the board and the player, returns a list of BOARDS of the next possible game states
def getNextMoves(currentBoard, player):
    nextMoves = []

    for row in range(3):
        for col in range(3):
            if currentBoard[row][col] == '.':
                boardCopy = getBoardCopy(currentBoard)
                boardCopy[row][col] = player
                nextMoves.append(boardCopy)

    return nextMoves

# Copies the board (duh)
def getBoardCopy(board):
    boardCopy = []

    for row in board:
        boardCopy.append(row.copy())

    return boardCopy

# takes in a board and a player, returns a score (positive if the player won, negative otherwise)
def simulate(currentBoard, player):
    currentPlayer = getNextPlayer(player)
    boardCopy = getBoardCopy(currentBoard)

    if hasWon(currentBoard, userPlayer):
        return -50
    elif hasWon(currentBoard, getNextPlayer(userPlayer)):
        return 50

    simulationMoves = []
    nextMoves = getNextMoves(boardCopy, currentPlayer)


    while nextMoves != []:
        roll = random.randint(1, len(nextMoves)) - 1
        boardCopy = nextMoves[roll]

        simulationMoves.append(boardCopy)

        if hasWon(boardCopy, currentPlayer):
            break

        currentPlayer = getNextPlayer(currentPlayer)
        nextMoves = getNextMoves(boardCopy, currentPlayer)

    if hasWon(boardCopy, userPlayer):
        score = -50
    elif hasWon(boardCopy, getNextPlayer(userPlayer)):
        score = 50
    else:
        score = 0

    """try:
        printBoard(simulationMoves[-1])
    except:
        printBoard(currentBoard)
    print(score)"""
    return score

# Checks if someone has won (just for the input player)
def hasWon(currentBoard, player):
    for row in range(3):
        if currentBoard[row][0] == player and currentBoard[row][1] == player and currentBoard[row][2] == player:
            return True

    for col in range(3):
        if currentBoard[0][col] == player and currentBoard[1][col] == player and currentBoard[2][col] == player:
            return True

    if currentBoard[0][0] == player and currentBoard[1][1] == player and currentBoard[2][2] == player:
        return True

    if currentBoard[0][2] == player and currentBoard[1][1] == player and currentBoard[2][0] == player:
        return True

    return False

# prints the board (duh)
def printBoard(board):
    for row in range(3):
        for col in range(3):
            print(board[row][col], end = " ")
        print()

board = [
    [".", ".", "."],
    [".", ".", "."],
    [".", ".", "."]
]

gameOver = False
turn = "X"
userPlayer = "O"

while not gameOver:

    printBoard(board)

    if turn == userPlayer:
        row = int(input("which row? "))
        col = int(input("which col? "))
        board[row][col] = turn

    else:
        tree = MCTree(GameState(board, turn))
        move = tree.makeChoice(5000)
        board = move[0]
        if abs(move[1]) < 30:
            print("expected: tie")
        elif move[1] < 0:
            print("expected: Elliot made a coding mistake")
        else:
            print("expected: I win!")


    if hasWon(board, turn):
        print(turn, "has won!")
        printBoard(board)
        gameOver = True

    else:
        found = False
        for r in range(3):
            for c in range(3):
                if board[r][c] == ".":
                    found = True

        gameOver = not found
        if gameOver:
            printBoard(board)

    turn = getNextPlayer(turn)
