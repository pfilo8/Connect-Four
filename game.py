import numpy as np
import pygame
from pygame.locals import *

BOARDWIDTH = 7
BOARDHEIGHT = 6 
SPACESIZE = 50 

FPS = 30 
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * SPACESIZE) / 2) - 10
YMARGIN = int((WINDOWHEIGHT - BOARDHEIGHT * SPACESIZE) / 2) + 20

WHITE = (255, 255, 255)
PINK = (255, 124, 214)
YELLOW = (253, 222, 50)
BLACK = (0, 0, 0)

player = 1
computer = 4

pygame.init()
FPSCLOCK = pygame.time.Clock()
FPSCLOCK.tick(FPS)
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Connect Four')

REDPILERECT = pygame.Rect(int(SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
BLACKPILERECT = pygame.Rect(WINDOWWIDTH - int(3 * SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
REDTOKENIMG = pygame.image.load('yellow.png')
REDTOKENIMG = pygame.transform.smoothscale(REDTOKENIMG, (SPACESIZE, SPACESIZE))
BLACKTOKENIMG = pygame.image.load('black.png')
BLACKTOKENIMG = pygame.transform.smoothscale(BLACKTOKENIMG, (SPACESIZE, SPACESIZE))
BOARDIMG = pygame.image.load('board.png')
BOARDIMG = pygame.transform.smoothscale(BOARDIMG, (SPACESIZE, SPACESIZE))
BACKGROUND = pygame.image.load('background.png')
BACKGROUND2 = pygame.image.load('background2.png')
HUMANWINNERIMG = pygame.image.load('player_win.png')
HUMAN2WINNERIMG = pygame.image.load('player2_win.png')
COMPUTERWINNERIMG = pygame.image.load('computer_win.png')
TIEWINNERIMG = pygame.image.load('tie.png')
BLIP = pygame.mixer.Sound('pop.wav')

class Button(pygame.font.Font): #przyciski menu
    """Klasa przycisku menu"""
    def __init__(self, text, size=30, x=0, y=0):
        pygame.font.Font.__init__(self, 'Good_Morning.ttf', size)
        self.text = text
        self.color = WHITE
        self.label = self.render(self.text, 1, self.color)
        self.width = self.label.get_rect().width
        self.height = self.label.get_rect().height
        self.position = x, y

    def undermouse(self,mousepos):
        """Sprawdza, czy tekst znajduje się pod kursorem"""
        x = mousepos[0]
        y = mousepos[1]
        if (x >= self.position[0] and x <= self.position[0] + self.width) and \
            (y >= self.position[1] and y <= self.position[1] + self.height):
                return True
        return False
    
    def changeColor(self,color):
        self.color = color
        self.label = self.render(self.text, 1, color)

class Text(pygame.font.Font):   #tekst bez akcji
    """Tworzy tekst na powierzchni"""
    def __init__(self, text, size=30, color = WHITE, font = 'Good_Morning.ttf', x=0, y=0):
        pygame.font.Font.__init__(self, font, size)
        self.text = text
        self.label = self.render(self.text, 1, color)
        self.width = self.label.get_rect().width
        self.height = self.label.get_rect().height
        self.position = x, y  

def main():
    """Główna funkcja gry."""
    mode = 'COMPUTER'
    connectFour = Text('CONNECT FOUR', 45, PINK)
    connectFour.position = (WINDOWWIDTH/2 - connectFour.width/2, 30)
    labels = ['START', 'MODE', 'INSTRUCTION', 'QUIT']
    menuButtons = []
    for index, label in enumerate(labels):
        button = Button(label)
        button.position = (WINDOWWIDTH/2 - button.width/2, 80*(index+1) + 50)
        menuButtons.append(button)
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                return
            elif event.type == MOUSEBUTTONDOWN:
                if menuButtons[0].undermouse(pygame.mouse.get_pos()):
                    if mode == 'COMPUTER':
                        difficulty = selectLevel()
                        if type(difficulty) == int:
                            game(difficulty, mode)
                    else:
                        game(None, mode)
                elif menuButtons[1].undermouse(pygame.mouse.get_pos()):
                    mode = selectMode()
                elif menuButtons[2].undermouse(pygame.mouse.get_pos()):
                    showInstruction()
                elif menuButtons[3].undermouse(pygame.mouse.get_pos()):
                    pygame.quit()
                    return
        
        DISPLAYSURF.blit(BACKGROUND,(0,0))
        DISPLAYSURF.blit(connectFour.label, connectFour.position)
        for button in menuButtons:
            if button.undermouse(pygame.mouse.get_pos()):
                button.label = button.render(button.text, 1, YELLOW)
            else:
                button.label = button.render(button.text, 1, WHITE)
            DISPLAYSURF.blit(button.label, button.position)
                        
        pygame.display.flip()
    
def game(difficulty, enemy = 'COMPUTER'):
    """Rozgrywka."""
    board = np.zeros((BOARDHEIGHT,BOARDWIDTH))
    turn = np.random.choice(['PLAYER1',enemy])
    
    drawBoard(board)
    
    while True:
        if turn == 'PLAYER1':
            board = playerTurn(board, player)
            
            # gracz chce wyjsc
            if type(board) != np.ndarray:
                return
            
            if checkWin(board,player):
                winnerImg = HUMANWINNERIMG
                break
            turn = enemy
            
        elif turn == 'PLAYER2':
            board = playerTurn(board, computer)
            
            # gracz chce wyjsc
            if type(board) != np.ndarray:
                return
            
            if checkWin(board, computer):
                winnerImg = HUMAN2WINNERIMG
                break
            turn = 'PLAYER1'
            
        else:
            board = computerTurn(board, difficulty)
            if checkWin(board,computer):
                winnerImg = COMPUTERWINNERIMG
                break
            turn = 'PLAYER1'
        
        drawBoard(board)

        if isFullBoard(board):
            winnerImg = TIEWINNERIMG
            break
    
    drawBoard(board)
    WINNERRECT = winnerImg.get_rect()
    WINNERRECT.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(winnerImg, WINNERRECT)
    pygame.display.flip()
    
    while True:
        # Keep looping until player clicks the mouse or quits.
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                return

def selectLevel():
    """ Ekran wyboru poziomu. """
    levelButtons = []
    for i in range(4):
        button = Button(str(i), 50)
        button.position = (int(WINDOWWIDTH/6)*(i+1) + 30, WINDOWHEIGHT/2 - button.width/2)
        levelButtons.append(button)
    title = Text("SELECT DIFFICULTY", 35, PINK)
    title.position = (WINDOWWIDTH/2 - title.width/2, 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 
            elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for index, button in enumerate(levelButtons):
                    if button.undermouse(pygame.mouse.get_pos()):
                        return index

        DISPLAYSURF.blit(BACKGROUND, (0,0))
        DISPLAYSURF.blit(title.label, title.position)
        
        for button in levelButtons:
            if button.undermouse(pygame.mouse.get_pos()):
                button.label = button.render(button.text, 1, YELLOW)
            else:
                button.label = button.render(button.text, 1, WHITE)
            DISPLAYSURF.blit(button.label, button.position)
       
        pygame.display.flip()

def selectMode():
    """ Ekran wyboru vs Computer/Player. """
    title = Text("SELECT MODE", 35, PINK)
    title.position = (WINDOWWIDTH/2 - title.width/2, 40)
    vsComputer = Button('VS COMPUTER')
    vsComputer.position = (WINDOWWIDTH/2 - vsComputer.width/2, 200)
    vsPlayer = Button('VS PLAYER')
    vsPlayer.position = (WINDOWWIDTH/2 - vsPlayer.width/2, 300)
    modeButtons = [vsComputer, vsPlayer]
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'COMPUTER'
            elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                return 'COMPUTER'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if vsPlayer.undermouse(pygame.mouse.get_pos()):
                    return 'PLAYER2'
                elif vsComputer.undermouse(pygame.mouse.get_pos()):
                    return 'COMPUTER'
        
        DISPLAYSURF.blit(BACKGROUND,(0,0)) 
        DISPLAYSURF.blit(title.label, title.position)
        
        for button in modeButtons:
            if button.undermouse(pygame.mouse.get_pos()):
                button.label = button.render(button.text, 1, YELLOW)
            else:
                button.label = button.render(button.text, 1, WHITE)
            DISPLAYSURF.blit(button.label, button.position)
        pygame.display.flip()
    
def showInstruction():
    """ Ekran z instrukcjami. """
    title = Text('INSTRUCTION', 35, PINK)
    title.position = (WINDOWWIDTH/2 - title.width/2, 30)
    instructionsContainer = []
    instructions = ["CONNECT FOUR IS A GAME IN WHICH PLAYERS DROPS COLORED DISCS" ,
                    "FROM THE TOP INTO A GRID. THE PIECES FALL STRAIGHT DOWN,",
                    "OCCUPYING THE NEXT AVAILABLE SPACE WITHIN THE COLUMN.",
                    "THE OBJECTIVE OF THE GAME IS TO BE SPACE WITHIN THE COLUMN.",
                    "THE FIRST TO FORM A HORIZONTAL, VERTICAL, OR DIAGONAL LINE",
                    "OF FOUR OF ONE'S OWN DISCS."]
    for index, instruction in enumerate(instructions):
        text = Text(instruction, size = 30, font = 'Meatloaf Sketched.ttf')
        text.position = (WINDOWWIDTH/2 - text.width/2, 50 * (index + 1) + 70)
        instructionsContainer.append(text)
        
    back = Button('BACK')
    back.position = (WINDOWWIDTH/2 - back.width/2, WINDOWHEIGHT - 80)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back.undermouse(pygame.mouse.get_pos()):
                    return
        
        if back.undermouse(pygame.mouse.get_pos()):
            back.changeColor(YELLOW)
        else:
            back.changeColor(WHITE)
        
        DISPLAYSURF.blit(BACKGROUND,(0,0))
        DISPLAYSURF.blit(title.label, title.position)
        DISPLAYSURF.blit(back.label, back.position)
        for instruction in instructionsContainer:
            DISPLAYSURF.blit(instruction.label, instruction.position)
        pygame.display.flip()

def drawBoard(board, extraToken = None):
    """ Rysowanie wykresu. """
    DISPLAYSURF.blit(BACKGROUND2,(0,0))
    spaceRect = pygame.Rect(0, 0, SPACESIZE, SPACESIZE)
    
    for i in range(BOARDWIDTH):
        button = Button(str(i+1), 20)
        button.position = (XMARGIN + 20 + (i * SPACESIZE), YMARGIN - SPACESIZE)
        DISPLAYSURF.blit(button.label, button.position)
    # draw tokens
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
            if board[y][x] == player:
                DISPLAYSURF.blit(REDTOKENIMG, spaceRect)
            elif board[y][x] == computer:
                DISPLAYSURF.blit(BLACKTOKENIMG, spaceRect)
            elif board[y][x] == 0:
                DISPLAYSURF.blit(BOARDIMG, spaceRect)

    pygame.display.flip()

def animateDroppingToken(board, line, gamer):
    """ Funkcja animująca wrzucanie tokenu. """
    x = XMARGIN + line * SPACESIZE
    y = YMARGIN - SPACESIZE
    dropSpeed = 0

    lowestEmptySpace = getLowestEmptySpace(board, line)

    while True:
        y += int(dropSpeed)
        dropSpeed += 0.05
        if int((y - YMARGIN) / SPACESIZE) >= lowestEmptySpace:
            return
        
        position = (x, y, SPACESIZE, SPACESIZE)
        if gamer == player:
            DISPLAYSURF.blit(REDTOKENIMG, position)
        elif gamer == computer:
            DISPLAYSURF.blit(BLACKTOKENIMG, position)
        
        pygame.display.flip()

def playerTurn(board, player):
    """ Ruch gracza. """
    lineButtons = []
    color = BLACK if player == computer else YELLOW
    updateArea = pygame.Rect(XMARGIN + 20, YMARGIN - SPACESIZE, WINDOWWIDTH, 40)
    
    for i in range(BOARDWIDTH):
        button = Button(str(i+1), 20)
        button.position = (XMARGIN + 20 + (i * SPACESIZE), YMARGIN - SPACESIZE)
        lineButtons.append(button)
        DISPLAYSURF.blit(button.label, button.position)
    
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for index, button in enumerate(lineButtons):
                    if button.undermouse(pygame.mouse.get_pos()):
                        line = index
                        if isValid(board,line):
                            board = inputToken(board, line, player)
                            BLIP.play()
                            animateDroppingToken(board, line, player)
                            return board
        
        for button in lineButtons:
            if button.undermouse(pygame.mouse.get_pos()) and button.color == WHITE:
                button.changeColor(color)
                DISPLAYSURF.blit(button.label, button.position)
            elif not button.undermouse(pygame.mouse.get_pos()) and button.color != WHITE:
                button.changeColor(WHITE)
                DISPLAYSURF.blit(button.label, button.position)
        
        pygame.display.update(updateArea)
                
def computerTurn(board, difficulty):
    """ Ruch komputera. """
    line = computerMove(board, difficulty)
    board = inputToken(board, line, computer)
    animateDroppingToken(board, line, computer)
    return board

def computerMove(board, difficulty):
    potentialMoves = getPotentialMoves(board, difficulty)
    n = len(potentialMoves)
    
    bestMoveScore = max([potentialMoves[i] for i in range(n) if isValid(board,i)])
    bestMoves = [i for i in range(n) if (potentialMoves[i] == bestMoveScore and isValid(board,i))]
    return np.random.choice(bestMoves)

def getPotentialMoves(board, lookAhead):
    results = [0] * BOARDWIDTH
    
    if lookAhead == 0:
        return results
    
    for line in range(BOARDWIDTH):
        newBoard = np.copy(board)
        if not isValid(newBoard, line):
            continue
        newBoard = inputToken(newBoard, line, computer)
        if checkWin(newBoard, computer):
            results[line] = 1
            continue
        else:
            if isFullBoard(newBoard):
                results[line] = 0
            else:
                for playerMove in range(BOARDWIDTH):
                    boardForPlayerMove = np.copy(newBoard)
                    if not isValid(boardForPlayerMove, playerMove):
                        continue
                    boardForPlayerMove = inputToken(boardForPlayerMove, playerMove, player)
                    if checkWin(boardForPlayerMove, player):
                        results[line] = -1
                        break
                    else:
                        lowerResults = getPotentialMoves(boardForPlayerMove, lookAhead - 1)
                        results[line] += (sum(lowerResults)/BOARDWIDTH) / BOARDWIDTH
                        #tempResult = results[line] + (sum(lowerResults)/BOARDWIDTH) / BOARDWIDTH
                        #results[line] = min(results[line], tempResult)
    return results

def isValid(board,line):
    """ Sprawdza czy można wykonać taki ruch. """
    if board[0][line] != 0:
        return False
    return True

def isFullBoard(board):
    return (board != 0).all()

def getLowestEmptySpace(board, line):
    i = 0
    try:
        while True:
            if board[i+1][line] != 0:
                return i
            i += 1
    # Pusta linia, wrzuca na koniec
    except IndexError:
        return i

def inputToken(board,line,player):
    index = getLowestEmptySpace(board, line)
    board[index][line] = player
    return board

def checkWin(board,player):
    height, width = board.shape
    
    # check horizontally
    for i in range(height):
        for j in range(width - 3):
            if board[i][j] == player and board[i][j+1] == player and board[i][j+2] == player and board[i][j+3] == player:
                return True
    #check vertically
    for j in range(width):
        for i in range(height - 3):
            if board[i][j] == player and board[i+1][j] == player and board[i+2][j] == player and board[i+3][j] == player:
                return True
    #check diagonal \
    for j in range(width - 3):
        for i in range(height - 3):
            if board[i][j] == player and board[i+1][j+1] == player and board[i+2][j+2] == player and board[i+3][j+3] == player:
                return True
    #check diagonal /
    for i in range(3,height):
        for j in range(width - 3):
            if board[i][j] == player and board[i-1][j+1] == player and board[i-2][j+2] == player and board[i-3][j+3] == player:
                return True
    return False
    
if __name__ == '__main__':
    main()