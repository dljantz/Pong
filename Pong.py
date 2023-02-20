# Pong game created by David Jantz using Pygame
# Copyright March 2019

#Potential future add-ons:
#   play against the computer or another person
#   different levels -- faster ball, smaller paddles, multiple balls, etc
#   cool graphics! color changing ball / background, something fun when it hits the paddle and when you win / lose.
#   obstacles, wormholes, etc that the ball interacts with
#   collect super powers / extra lives by sending the ball through a token
#   sounds

import pygame, sys, random, math, time
from pygame.locals import *

WINDOWWIDTH = 800
WINDOWHEIGHT = 700
FPS = 72

# color tuples
WHITE =  (255, 255, 255)
BLACK =  (  0,   0,   0)
GREEN =  ( 20, 200,  20)
GOLD =   (230, 170,  30)
NAVY =   ( 30,  70,  80)
BLUE =   ( 90, 210, 240, 150)
RED =    (200,  60,  40)

TRANSPARENT = (255, 255, 255,   0)
CLEARGOLD =   (230, 170,  30, 150)

BGCOLOR = NAVY

# Helps with error prevention -- any typos will cause errors in the right places because that variable doesn't exist
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

def main():
    global FPSCLOCK, SCREEN, SCREEN2, BIGFONT, MEDIUMFONT, SMALLFONT
    pygame.init()
    
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    SCREEN2 = SCREEN.convert_alpha() # allows for transparent / translucent effects like the ball trail
    BIGFONT = pygame.font.Font('freesansbold.ttf', 80)
    MEDIUMFONT = pygame.font.Font('freesansbold.ttf', 40)
    SMALLFONT = pygame.font.Font('freesansbold.ttf', 20)
    pygame.display.set_caption('"Pong" adaptation by David Jantz')
    
    showStartScreen() # show until the player presses a key
    
    while True:
        runGame() # the meat and potatoes
        showGameOverScreen() # dessert

def terminate(): # syntactic sugar that makes code prettier
    pygame.quit()
    sys.exit()

def checkForTerminate(event): # If you press exit or hit escape, runs terminate()
    if event.type == QUIT:
        terminate()
    elif event.type == KEYUP and event.key == K_ESCAPE:
        terminate()

def showStartScreen(): # shows the start screen until a key is pressed or player exits out.
    titleBall = createNewBall(True, NAVY, 100, 150) # the ball with the game title doesn't die, is white, has a radius of 100, and a speed of 150.
    
    startGameTextP = BIGFONT.render('P', True, RED)
    startGameTextO = BIGFONT.render('O', True, GREEN)
    startGameTextN = BIGFONT.render('N', True, GREEN)
    startGameTextG = BIGFONT.render('G', True, RED)
    startGameInstructions1 = SMALLFONT.render('Control the left and right paddles with W, S, Up Arrow, and Down Arrow.', True, NAVY)
    startGameInstructions2 = SMALLFONT.render('There are 3 other letters on the keyboard that do fun things. Can you find them?', True, NAVY)
    startGameInstructions3 = SMALLFONT.render('Press any key to begin. Good luck!', True, NAVY)
    
    startGameRectP = startGameTextP.get_rect()
    startGameRectO = startGameTextO.get_rect()
    startGameRectN = startGameTextN.get_rect()
    startGameRectG = startGameTextG.get_rect()
    startGameRect1 = startGameInstructions1.get_rect()
    startGameRect2 = startGameInstructions2.get_rect()
    startGameRect3 = startGameInstructions3.get_rect()
    
    # Place the instructions in the middle of the screen
    startGameRect1.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) - 30)
    startGameRect2.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    startGameRect3.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 30)
    
    while True:
        for event in pygame.event.get():
            checkForTerminate(event)
            if event.type == KEYUP or event.type == MOUSEBUTTONUP:
                return
        
        # Move the title ball to the next spot in its trajectory (No paddles or gravity involved)
        titleBall = moveBall(titleBall, None, None, False)

        startGameRectP.bottomright = (titleBall['coords'])
        startGameRectO.bottomleft = (titleBall['coords'])
        startGameRectN.topright = (titleBall['coords'])
        startGameRectG.topleft = (titleBall['coords'])
        
        SCREEN.fill(CLEARGOLD)
        SCREEN2.fill(TRANSPARENT)
        
        # Draw the bouncing title
        drawBallTrail(titleBall)
        drawBall(titleBall)
        SCREEN.blit(startGameTextP, startGameRectP)
        SCREEN.blit(startGameTextO, startGameRectO)
        SCREEN.blit(startGameTextN, startGameRectN)
        SCREEN.blit(startGameTextG, startGameRectG)
        
        # Draw a translucent rectangle so the instructions are easier to read
        pygame.draw.rect(SCREEN2, CLEARGOLD, (0, int(WINDOWWIDTH / 2 - 50), WINDOWWIDTH, 100))
        SCREEN.blit(SCREEN2, (0, 0))
        
        # Draw the instructions
        SCREEN.blit(startGameInstructions1, startGameRect1)
        SCREEN.blit(startGameInstructions2, startGameRect2)
        SCREEN.blit(startGameInstructions3, startGameRect3)
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def runGame(): # main game loop once you're actually playing.
    ball = createNewBall(False, GOLD, 10, 300) #cheatMode is off, color is gold, radius is 10, speed is 300.
    paddle1 = CreateNewPaddle(LEFT)
    paddle2 = CreateNewPaddle(RIGHT)

    gravity = 0 # a fun easter egg you can toggle on / off by pressing 'g'.
    paddleInertia = True # setting that changes how the paddles move: instant changes in velocity or some physics-y acceleration, bouncing, and friction
    
    while True:
        # event handling loop
        for event in pygame.event.get():
            checkForTerminate(event)
            if event.type == KEYDOWN:
                if event.key == K_w:
                    paddle1['direction'] = UP
                elif event.key == K_s:
                    paddle1['direction'] = DOWN
                if event.key == K_UP: # use a second if rather than elif in case players hit their keys during the exact same iteration.
                    paddle2['direction'] = UP
                elif event.key == K_DOWN:
                    paddle2['direction'] = DOWN
                elif event.key == K_c: # pressing 'c' toggles Cheat Mode on and off
                    if ball['cheatMode']:
                        ball['cheatMode'] = False
                    else:
                        ball['cheatMode'] = True
                elif event.key == K_i: # pressing 'i' toggles inertia mode on and off.
                    if paddleInertia ==  True:
                        paddleInertia = False
                    else:
                        paddleInertia = True
                elif event.key == K_g: # pressing 'g' toggles gravity mode on and off. Also turning on gravity turns on inertia for paddles.
                    if gravity != 0:
                        gravity = 0
                    else:
                        gravity = 5
                        paddleInertia = True
            if event.type == KEYUP and (event.key == K_w or event.key == K_s):
                paddle1['direction'] = None
            elif event.type == KEYUP and (event.key == K_UP or event.key == K_DOWN):
                paddle2['direction'] = None
        
        # calculate all the new ball variables without actually drawing any of it to the screen.
        ball = moveBall(ball, paddle1, paddle2, gravity)
        
        # When the ball dies, turn the ball black and wait two seconds showing game over screen.
        if not ball['alive']:
            ball['color'] = BLACK
            if time.time() - ball['timer'] > 2:
                return
        
        # calculate all the new paddle variables based on current mode of paddle movement.
        if paddleInertia:
            paddle1 = movePaddleInertia(paddle1, gravity)
            paddle2 = movePaddleInertia(paddle2, gravity)
        else:
            paddle1 = movePaddleNormal(paddle1)
            paddle2 = movePaddleNormal(paddle2)
        
        SCREEN.fill(BGCOLOR)
        SCREEN2.fill(TRANSPARENT)
        drawBall(ball)
        drawPaddle(paddle1)
        drawPaddle(paddle2)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def showGameOverScreen(): # after someone has lost, does end of game stuff
    gameOverMessage = BIGFONT.render('Game Over', True, WHITE)
    gameOverRect = gameOverMessage.get_rect()
    gameOverRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

    SCREEN.fill(BGCOLOR)
    SCREEN.blit(gameOverMessage, gameOverRect)
    pygame.display.update()
    pygame.time.wait(1000) #add a time delay before asking player if they want to play again.
    
    SCREEN.fill(BGCOLOR)
    pygame.display.update()
    pygame.time.wait(500)
    
    playAgainMessage = MEDIUMFONT.render('Press any key to play again', True, GOLD)
    playAgainRect = playAgainMessage.get_rect()
    playAgainRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    
    SCREEN.fill(BGCOLOR)
    SCREEN.blit(playAgainMessage, playAgainRect)
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            checkForTerminate(event)
            if event.type == KEYUP:
                return

def createNewBall(cheatMode, color, radius, speed): # creates a dictionary of values that represent the ball.
    ball = {'alive': True,
            'cheatMode': cheatMode,
            'color': color,
            'coords': (),
            'direction': (),
            'pastCoords': [], # later, will become a list of past ball locations to draw ball trail.
            'radius': radius,
            'speed': speed, # units are pixels per second
            'timer': None,
            'trailLength': 100}
    ball['coords'] = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2)) # ball starts in the middle
    ball['direction'] = getRandomBallDirection(ball) # returns float tuple for velocity and direction (dx, dy)
    
    return ball

def CreateNewPaddle(side): # Create a dictionary of values, including a Rectangle Object, to represent the paddles.
    width = 25
    height = 200
    gap = 10
    rectObj = pygame.Rect(0, 0, width, height)
    
    if side == LEFT:
        rectObj.midleft = (gap, int(WINDOWHEIGHT / 2))
        color = RED
    else:
        rectObj.midright = (WINDOWWIDTH - gap, int(WINDOWHEIGHT / 2))
        color = GREEN
    
    paddle = {'color': color,
              'direction': None,
              'gap': gap,
              'height': height,
              'rectObj': rectObj,
              'topspeed': 200, # speed the paddle moves when it's not in inertia mode. Units are in pixels per second.
              'velocity': 0,
              'width': width}
    
    return paddle
    
def getRandomBallDirection(ball): # Takes a random number between 0 and tau and converts it to an ordered pair describing direction and velocity.
    radianDirection = random.random() * math.tau
    
    dx = math.cos(radianDirection) * ball['speed'] / FPS # changing the frame rate doesn't change the speed of the ball for the players.
    dy = math.sin(radianDirection) * ball['speed'] / FPS
    
    return (dx, dy) # float tuple, gets turned into integer later
    
def moveBall(ball, paddle1, paddle2, gravity): # Takes the current direction and speed and figures out new float coordinates for its velocity and position.
    
    # update the the ball trail's location
    ball['pastCoords'].append(ball['coords']) # adding the current ball coordinates to the end of the list creates an intentionally backwards list
    if len(ball['pastCoords']) > ball['trailLength']:
        ball['pastCoords'].remove(ball['pastCoords'][0]) # remove the first item in the list if the ball trail is long enough
    
    if ball['alive']:
        ball['timer'] = time.time() # When the ball dies, time stops updating so I can show the dead ball for two seconds.
        ball, isBouncing = wallBounce(ball) # changes ball direction if it hits a wall
        if paddle1 != None and paddle2 != None: # i.e. if we are actually playing, not in the intro screen
            ball = paddleBounce(ball, paddle1, paddle2) # changes ball direction if it hits a paddle
    
        if not isBouncing: # if the ball is in the process of bouncing off a wall, don't fuck around with gravity this iteration. I tried and it was bad news bears.
            newDy = ball['direction'][1] + gravity / FPS
            ball['direction'] = (ball['direction'][0], newDy)
    
        newX = ball['coords'][0] + ball['direction'][0]
        newY = ball['coords'][1] + ball['direction'][1]
        ball['coords'] = (newX, newY)

    return ball

def drawBall(ball):
    intBallCoords = (round(ball['coords'][0]), round(ball['coords'][1])) # round exact ball coords to integers so pygame can draw the ball.
    pygame.draw.circle(SCREEN, ball['color'], intBallCoords, ball['radius'])
    drawBallTrail(ball)

def drawBallTrail(ball): # draws a comet-like trail behind the ball
    trailRadius = int(ball['radius'] / 2) # radius of the circle at the very end of the trail.
    increment = (ball['radius'] - trailRadius) / len(ball['pastCoords']) # the increment by which the ball trail size increases so it doesn't exceed the ball size
    transparency = 0
    
    for floatCoords in ball['pastCoords']:
        intCoords = (round(floatCoords[0]), round(floatCoords[1]))
        transparency += 0.5
        if transparency >= 100:
            transparency = 100 # prevents errors if the ball trail gets longer than 255 (255 is the max transparency value)
        trailColor = (ball['color'][0], ball['color'][1], ball['color'][2], transparency)
        pygame.draw.circle(SCREEN2, trailColor, intCoords, round(trailRadius)) # round to integers so pygame.draw can handle the numbers
        trailRadius += increment
    
    SCREEN.blit(SCREEN2, (0, 0)) # add the second surface to SCREEN

def movePaddleNormal(paddle): # assigns new location to paddles in the boring way -- no inertia or bouncing off the walls or anything.    
    paddleY = paddle['rectObj'].center[1]
    
    if paddle['direction'] == UP and paddle['rectObj'].midtop[1] >= paddle['gap']: # (if it's going up but hasn't reached the top)
        paddleY = round(paddleY - paddle['topspeed'] / FPS)
        paddle['rectObj'].center = (paddle['rectObj'].center[0], paddleY)
    elif paddle['direction'] == DOWN and paddle['rectObj'].midbottom[1] <= WINDOWHEIGHT - paddle['gap']: # (if it's going down but hasn't reached the bottom)
        paddleY = round(paddleY + paddle['topspeed'] / FPS)
        paddle['rectObj'].center = (paddle['rectObj'].center[0], paddleY)
    
    return paddle

def movePaddleInertia(paddle, gravity): # Makes the paddles move by accelerating and decelerating. Assigns a new centerpoint to each paddle.
    
    friction = 10 # no units in particular
    acceleration = 50 # no units in particular
    elasticity = 0.3 # bounciness of paddle collision with wall. Could be anywhere from 0 to 1.
    
    paddleY = paddle['rectObj'].center[1] # do this so the program doesn't reference newY before assignment.

    if paddle['direction'] == UP:
        paddle['velocity'] -= acceleration
    elif paddle['direction'] == DOWN:
        paddle['velocity'] += acceleration
    elif gravity != 0:
        paddle['velocity'] += gravity
    elif paddle['velocity'] < 0:
        paddle['velocity'] += friction
    elif paddle['velocity'] > 0:
        paddle['velocity'] -= friction
    
    # bounce off the ceiling or the floor
    if paddle['rectObj'].midtop[1] <= paddle['gap'] and paddle['velocity'] < 0:
        paddle['velocity'] = abs(paddle['velocity']) * elasticity
    elif paddle['rectObj'].midbottom[1] >= WINDOWHEIGHT - paddle['gap'] and paddle['velocity'] > 0:
        paddle['velocity'] = abs(paddle['velocity']) * -elasticity
    
    paddleY = round(paddleY + paddle['velocity'] / FPS)
    paddle['rectObj'].center = (paddle['rectObj'].center[0], paddleY)
    
    return paddle

def drawPaddle(paddle): # Draws one paddle.
    thickness = 5
    pygame.draw.rect(SCREEN, paddle['color'], paddle['rectObj'])
    insideRect = (paddle['rectObj'][0] + thickness, paddle['rectObj'][1] + thickness, paddle['rectObj'][2] - thickness * 2, paddle['rectObj'][3] - thickness * 2)
    pygame.draw.rect(SCREEN, BGCOLOR, insideRect)

def wallBounce(ball): # detects walls and changes ball direction accordingly.
    # syntactic sugar
    x = ball['coords'][0]
    y = ball['coords'][1]
    dx = ball['direction'][0]
    dy = ball['direction'][1]
    isBouncing = False
    
    if ball['cheatMode']:
        if x + ball['radius'] >= WINDOWWIDTH:
            isBouncing = True
            dx = abs(dx) * -1
        elif x - ball['radius'] <= 0:
            isBouncing = True
            dx = abs(dx)
    elif x + ball['radius'] >= WINDOWWIDTH or x - ball['radius'] <= 0: # if the ball hits a side wall, it dies.
            ball['alive'] = False
    if y + ball['radius'] >= WINDOWHEIGHT:
        isBouncing = True
        dy = abs(dy) * -1
    elif y - ball['radius'] <= 0:
        isBouncing = True
        dy = abs(dy)
    
    ball['direction'] = (dx, dy)
    
    return ball, isBouncing

def paddleBounce(ball, paddle1, paddle2): # make the ball bounce when it hits a paddle.
    
    ballX = ball['coords'][0]
    ballY = ball['coords'][1]
    
    # if the ball is about to overlap with the paddle and the paddle and ball are at the same height, do the bounce by calculating
    #   the bounce angle and converting it to dx and dy values based on ball speed.
    if ballX - ball['radius'] <= paddle1['rectObj'].midright[0] and abs(ballY - paddle1['rectObj'].center[1]) <= paddle1['height'] / 2 + ball['radius'] / 2:
        height = (ballY - paddle1['rectObj'].center[1]) / (paddle1['height']) # produces a number between -0.5 and 0.5
        radians = height * math.pi / 2 # to bounce to the right, the range of angles is -pi/2 to pi/2
        
        dx = math.cos(radians) * ball['speed'] / FPS
        dy = math.sin(radians) * ball['speed'] / FPS
        ball['direction'] = (dx, dy)
        
    elif ballX + ball['radius'] >= paddle2['rectObj'].midleft[0] and abs(ballY - paddle2['rectObj'].center[1]) <= paddle2['height'] / 2 + ball['radius'] / 2:
        height = (paddle2['rectObj'].center[1] - ballY) / (paddle2['height']) # produces a number between -0.5 and 0.5
        radians = height * math.pi / 2 + math.pi # to bounce to the left, the range of angles is pi/2 to 3pi/2
        
        dx = math.cos(radians) * ball['speed'] / FPS
        dy = math.sin(radians) * ball['speed'] / FPS
        ball['direction'] = (dx, dy)
    
    return ball


if __name__ == '__main__':
    main()