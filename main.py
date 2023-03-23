import random
from enum import Enum
from collections import namedtuple

import pygame
from pygame.locals import *

from SnakeModel import Linear_QNet
from button import Button
from popup import Popup
from record import Record
from SnakeAgent import Agent
from SnakeGameAI import SnakeGameAI
from PlotHelper import plot
import torch

# UTILS VARIABLES
COLOR_BLACK = 0, 0, 0

# MODE MANAGEMENT VARIABLES
IDLE_MODE = True
ENTER_NAME_MODE = False
PLAY_MODE = False
GAME_OVER_MODE = False
PAUSE_MODE = False
HIGH_SCORES_MODE = False
TRAIN_SNAKE_MODE = False
VALIDATE_TRAIN_SNAKE_MODE = False
TEST_SNAKE_MODE = False
EXIT_MODE = False
FORCE_EXIT_MODE = False

# WINDOW CONFIG VARIABLES
MAIN_WINDOW_SIZE = MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT = 800, 600

# BUTTONS
PLAY_BUTTON = Button((310, 190), 150, 35, "PLAY")
HIGH_SCORES_BUTTON = Button((310, 240), 150, 35, "HIGH SCORES")
HIGH_SCORES_RETURN_BUTTON = Button((310, 490), 150, 35, "RETURN")
TRAIN_SNAKE_BUTTON = Button((310, 290), 150, 35, "TRAIN SNAKE")
TEST_SNAKE_BUTTON = Button((310, 340), 150, 35, "TEST SNAKE")
EXIT_GAME_BUTTON = Button((310, 390), 150, 35, "EXIT")
PAUSE_MODE_BACK_TO_MAIN_MENU_BUTTON = Button((150, 390), 150, 35, "BACK TO MENU")
PAUSE_MODE_RETURN_BUTTON = Button((450, 390), 150, 35, "RETURN TO PLAY")
PLAY_AGAIN_BUTTON = Button((450, 390), 150, 35, "PLAY AGAIN")
GAME_OVER_BACK_TO_MAIN_MENU_BUTTON = Button((150, 390), 150, 35, "BACK TO MENU")
ENTER_NAME_PLAY_GAME_BUTTON = Button((450, 390), 150, 35, "PLAY GAME")
ENTER_NAME_BACK_TO_MAIN_MENU_BUTTON = Button((150, 390), 150, 35, "BACK TO MENU")

EXIT_YES_BUTTON = Button((180, 390), 150, 35, "YES")
EXIT_NO_BUTTON = Button((440, 390), 150, 35, "NO")

# POPUPS
DEFAULT_POPUP_BOX = pygame.Rect(170, 10, 420, 35)
MAIN_MENU_POPUP = Popup("MAIN MENU", DEFAULT_POPUP_BOX)
ENTER_NAME_POPUP_BOX = pygame.Rect(170, 500, 420, 35)
ENTER_NAME_POPUP = Popup("ENTER NAME: ", ENTER_NAME_POPUP_BOX)
DISPLAY_SCORE_POPUP = Popup("SCORE: 0", DEFAULT_POPUP_BOX)
HIGH_SCORES_POPUP = Popup("HIGH_SCORES", DEFAULT_POPUP_BOX)
PAUSE_POPUP = Popup("PAUSE", DEFAULT_POPUP_BOX)
GAME_OVER_POPUP = Popup("GAME OVER", DEFAULT_POPUP_BOX)
TRAIN_SNAKE_MODE_POPUP = Popup("TRAIN SNAKE MODE", DEFAULT_POPUP_BOX)
TEST_SNAKE_MODE_POPUP = Popup("TEST SNAKE MODE", DEFAULT_POPUP_BOX)
EXIT_MODE_POPUP = Popup("EXIT GAME ?", DEFAULT_POPUP_BOX)

# RECORDS
DEFAULT_RECORD = pygame.Rect(145, 100, 470, 340)
HIGH_SCORES_RECORD = Record([""], DEFAULT_RECORD)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


class ControllerButtons(Enum):
    A = 0
    B = 1
    X = 2
    Y = 3


DIRECTION = Direction.RIGHT

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)
GREEN = (102, 255, 204)

BLOCK_SIZE = 20


class SnakeGame:

    def __init__(self, gamemode, display):
        self.w = display.get_width()
        self.h = display.get_height()
        self.gamemode = gamemode
        # init display
        self.display = display
        self.clock = pygame.time.Clock()

        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        self.highscore = self._getHighScore()
        self.score = 0
        self.speed = 10
        self.food = None
        if self.gamemode == "walls":
            self.walls = self._place_walls()
        self._place_food()

    def _place_walls(self):
        walls_coordinates = []
        for i in range(5):
            x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(5, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            while (Point(x, y) in walls_coordinates or y == self.head.y):
                x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
                y = random.randint(5, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            walls_coordinates.append(Point(x, y))
        return walls_coordinates

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(5, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake or self.food in self.walls:
            self._place_food()

    def play_step(self, direction):

        # 2. move
        self._move(direction)  # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            self.checkIfHighscore()
            self.updateScoresHistory()
            return game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            DISPLAY_SCORE_POPUP.setText("Score: " + str(self.score))
            self._place_food()
            self.speed += 1
        else:
            self.snake.pop()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(self.speed)
        # 6. return game over and score
        return game_over, self.score

    def checkIfHighscore(self):
        player_name = f"{ENTER_NAME_POPUP.getText()[12:]} {self.score}"

        if self.score > self.highscore:
            f = open("highscore.txt", "w")
            f.write(player_name)
            f.close()

    def updateScoresHistory(self):
        player_name = f"{ENTER_NAME_POPUP.getText()[12:]} {self.score}"
        f = open("scores_history.txt", "r")
        numberOfLines = len(f.readlines())
        f.close()
        if numberOfLines >= 1 and numberOfLines <= 4:
            f = open("scores_history.txt", "a")
            f.write('\n')
            f.write(player_name)
            f.close()
        elif numberOfLines == 0:
            f = open("scores_history.txt", "a")
            f.write(player_name)
            f.close()
        else:
            f = open("scores_history.txt", "r")
            scoresList = f.readlines()
            f.close()

            f = open("scores_history.txt", "w")
            f.close()

            newScoresList = scoresList[1:5]
            newScoresList.append(player_name)

            f = open("scores_history.txt", "a")
            f.write(newScoresList[0].strip())
            for score in newScoresList[1:]:
                f.write('\n')
                f.write(score.strip())

    def _is_collision(self):
        if self.gamemode == "walls":
            if self.head in self.walls:
                return True
        # hits itself
        if self.head in self.snake[1:]:
            return True
        return False

    def _update_ui(self):

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        if self.gamemode == "walls":
            for wall in self.walls:
                pygame.draw.rect(self.display, GREEN, pygame.Rect(wall.x, wall.y, BLOCK_SIZE, BLOCK_SIZE))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            if self.head.x == self.w - BLOCK_SIZE:
                x = 0
            else:
                x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            if self.head.x == 0:
                x = self.w - BLOCK_SIZE
            else:
                x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            if self.head.y == self.h - BLOCK_SIZE:
                y = 0
            else:
                y += BLOCK_SIZE
        elif direction == Direction.UP:
            if self.head.y == 0:
                y = self.h - BLOCK_SIZE
            else:
                y -= BLOCK_SIZE

        self.head = Point(x, y)

    def _getHighScore(self):
        f = open("highscore.txt", "r")
        highscore_aux = f.read()
        f.close()
        if highscore_aux == "":
            return 0
        else:
            highscore_aux = "".join([ch if not ch.isalpha() else "" for ch in reversed(highscore_aux)])
            return int(highscore_aux)


def onMainMenuEnter():
    # INIT IDLE MODE
    MAIN_MENU_POPUP.show()

    # BUTTON RENDER
    PLAY_BUTTON.show()
    HIGH_SCORES_BUTTON.show()
    TRAIN_SNAKE_BUTTON.show()
    TEST_SNAKE_BUTTON.show()
    EXIT_GAME_BUTTON.show()


def onMainMenuExit():
    # DE INIT IDLE MODE
    MAIN_MENU_POPUP.hide()

    # BUTTON RENDER
    PLAY_BUTTON.hide()
    HIGH_SCORES_BUTTON.hide()
    TRAIN_SNAKE_BUTTON.hide()
    TEST_SNAKE_BUTTON.hide()
    EXIT_GAME_BUTTON.hide()


def onExitModeEnter():
    # INIT EXIT MODE
    EXIT_MODE_POPUP.show()

    # BUTTON RENDER
    EXIT_YES_BUTTON.show()
    EXIT_NO_BUTTON.show()


def onExitModeExit():
    # DE INIT EXIT MODE
    EXIT_MODE_POPUP.hide()

    # BUTTON RENDER
    EXIT_YES_BUTTON.hide()
    EXIT_NO_BUTTON.hide()


def onHighScoresEnter():
    # INIT HIGH SCORES MODE
    HIGH_SCORES_POPUP.show()

    textList = []

    # Code for highscore
    in_file = open("highscore.txt", "r")
    textList.append("Lifetime highscore: " + in_file.readline().strip())
    textList.append("")
    textList.append("")
    in_file.close()

    # Code for score history (last 5 games)
    in_file = open("scores_history.txt", "r")
    for id, line in enumerate(in_file.readlines()):
        textList.append(f"{id + 1}. {line.rstrip()}")
    in_file.close()

    HIGH_SCORES_RECORD.setTextList(textList)
    HIGH_SCORES_RECORD.show()

    # BUTTON RENDER
    HIGH_SCORES_RETURN_BUTTON.show()


def onHighScoresExit():
    # DE INIT HIGH SCORES MODE
    HIGH_SCORES_POPUP.hide()
    HIGH_SCORES_RECORD.hide()

    # BUTTON RENDER
    HIGH_SCORES_RETURN_BUTTON.hide()


def onPlayGameExit():
    # DE INIT PLAY GAME MODE
    DISPLAY_SCORE_POPUP.hide()


def onPlayGameEnter():
    # DE INIT PLAY GAME MODE
    DISPLAY_SCORE_POPUP.show()


def onPauseMenuEnter():
    # INIT PAUSE MODE
    PAUSE_POPUP.show()

    # BUTTON RENDER
    PAUSE_MODE_BACK_TO_MAIN_MENU_BUTTON.show()
    PAUSE_MODE_RETURN_BUTTON.show()


def onPauseMenuExit():
    # DE INIT PAUSE MODE
    PAUSE_POPUP.hide()

    # BUTTON RENDER
    PAUSE_MODE_BACK_TO_MAIN_MENU_BUTTON.hide()
    PAUSE_MODE_RETURN_BUTTON.hide()


def onGameOverEnter():
    # INIT GAME OVER MODE
    GAME_OVER_POPUP.show()

    # BUTTON RENDER
    PLAY_AGAIN_BUTTON.show()
    GAME_OVER_BACK_TO_MAIN_MENU_BUTTON.show()


def onGameOverExit():
    # DE INIT GAME OVER MODE
    GAME_OVER_POPUP.hide()

    # BUTTON RENDER
    PLAY_AGAIN_BUTTON.hide()
    GAME_OVER_BACK_TO_MAIN_MENU_BUTTON.hide()


def onEnterNameEnter():
    # INIT GAME OVER MODE
    ENTER_NAME_POPUP.show()

    # BUTTON RENDER
    ENTER_NAME_PLAY_GAME_BUTTON.show()
    ENTER_NAME_BACK_TO_MAIN_MENU_BUTTON.show()

    ENTER_NAME_POPUP.setText("ENTER NAME: ")


def onEnterNameExit():
    # DE INIT ENTER NAME MODE
    ENTER_NAME_POPUP.hide()

    # BUTTON RENDER
    ENTER_NAME_PLAY_GAME_BUTTON.hide()
    ENTER_NAME_BACK_TO_MAIN_MENU_BUTTON.hide()

def onTrainSankeEnter():
    # INIT TRAIN SNAKE MODE
    DISPLAY_SCORE_POPUP.show()

def onTrainStakeExit():
    # DE INIT TRAIN SNAKE MODE
    DISPLAY_SCORE_POPUP.hide()


def onValidateTrainingEnter():
    # INIT PAUSE MODE
    PAUSE_POPUP.show()

    # BUTTON RENDER
    PAUSE_MODE_BACK_TO_MAIN_MENU_BUTTON.show()
    PAUSE_MODE_RETURN_BUTTON.show()

def onValidateTrainingExit():
    # DE INIT PAUSE MODE
    PAUSE_POPUP.hide()

    # BUTTON RENDER
    PAUSE_MODE_BACK_TO_MAIN_MENU_BUTTON.hide()
    PAUSE_MODE_RETURN_BUTTON.hide()

def onTestSnakeEnter():
    # INIT TEST SNAKE MODE
    DISPLAY_SCORE_POPUP.show()


def onTestSnakeExit():
    # DE INIT TEST SNAKE MODE
    DISPLAY_SCORE_POPUP.hide()



if __name__ == '__main__':

    # Initialize Pygame
    pygame.init()

    # Set the window dimensions
    MAIN_WINDOW = pygame.display.set_mode(MAIN_WINDOW_SIZE)
    pygame.display.set_caption('Graph editor')

    controller_count = pygame.joystick.get_count()

    controller = None

    if controller_count == 0:
        print("No joysticks connected")
    else:
        print(f"Found {controller_count} controller(s)")
        controller = pygame.joystick.Joystick(0)
        controller.init()

    game = None

    ###########################
    # START TRAIN SNAKE VARIABLES
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = None
    gameAI = None
    # STOP TRAIN SNAKE VARIABLES
    ############################

    onMainMenuEnter()

    while True:
        MAIN_WINDOW.fill(COLOR_BLACK)
        if PLAY_MODE and game is None:
            DIRECTION = DIRECTION.RIGHT
            DISPLAY_SCORE_POPUP.setText("Score: 0")
            game = SnakeGame("walls", MAIN_WINDOW)

        if TRAIN_SNAKE_MODE and agent is None and gameAI is None:
            DISPLAY_SCORE_POPUP.setText("Train Snake Score: 0")
            gameAI = SnakeGameAI("walls", MAIN_WINDOW, DISPLAY_SCORE_POPUP)
            agent = Agent()

        if TEST_SNAKE_MODE and agent is None and gameAI is None:
            DISPLAY_SCORE_POPUP.setText("Test Snake Score: 0")
            gameAI = SnakeGameAI("walls", MAIN_WINDOW, DISPLAY_SCORE_POPUP, "Test")
            model = Linear_QNet(11, 256, 3)
            model.load_state_dict(torch.load('model/model.pth'))
            agent = Agent(model, "Test")

        if not PLAY_MODE and not PAUSE_MODE:
            game = None



        if FORCE_EXIT_MODE:
            break
        elif VALIDATE_TRAIN_SNAKE_MODE:
            # check for events
            for event in pygame.event.get():
                # if we press a mouse button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mousePosX, mousePosY = event.pos
                    # left click config
                    if event.button == 1:
                        if PAUSE_MODE_BACK_TO_MAIN_MENU_BUTTON.canClick(mousePosX, mousePosY):
                            IDLE_MODE = True
                            VALIDATE_TRAIN_SNAKE_MODE = False
                            onValidateTrainingExit()
                            onMainMenuEnter()
                            break
                        if PAUSE_MODE_RETURN_BUTTON.canClick(mousePosX, mousePosY):
                            TRAIN_SNAKE_MODE = True
                            VALIDATE_TRAIN_SNAKE_MODE = False
                            onValidateTrainingExit()
                            onTrainSankeEnter()
                            break
        elif TRAIN_SNAKE_MODE:
            # check for events
            for event in pygame.event.get():
                # if we press a mouse button
                if event.type == pygame.QUIT:
                    TRAIN_SNAKE_MODE = False
                    FORCE_EXIT_MODE = True
                    onTrainStakeExit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mousePosX, mousePosY = event.pos

            # get old state
            state_old = agent.get_state(gameAI)

            # get move
            final_move = agent.get_action(state_old)

            # perform move and get new state
            reward, done, ai_score = gameAI.play_step(final_move)
            state_new = agent.get_state(gameAI)

            # train short memory
            agent.train_short_memory(state_old, final_move, reward, state_new, done)

            # remember
            agent.remember(state_old, final_move, reward, state_new, done)

            if done:
                # train long memory, plot result
                gameAI.reset()
                agent.n_games += 1
                agent.train_long_memory()

                if ai_score > record:
                    record = ai_score
                    agent.model.save()

                print('Game', agent.n_games, 'Score', ai_score, 'Record:', record)

                plot_scores.append(ai_score)
                total_score += ai_score
                mean_score = total_score / agent.n_games
                plot_mean_scores.append(mean_score)
                plot(plot_scores, plot_mean_scores)

                VALIDATE_TRAIN_SNAKE_MODE = True
                TRAIN_SNAKE_MODE = False
                onTrainStakeExit()
                onValidateTrainingEnter()
        elif TEST_SNAKE_MODE:

            # check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    TEST_SNAKE_MODE = False
                    FORCE_EXIT_MODE = True
                    onTestSnakeExit()
                # if we press a mouse button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mousePosX, mousePosY = event.pos

            # get old state
            state_old = agent.get_state(gameAI)

            # get move
            final_move = agent.get_action(state_old)

            # perform move and get new state
            reward, done, score = gameAI.play_step(final_move)

            if done:
                TEST_SNAKE_MODE = False
                GAME_OVER_MODE = True
                onTestSnakeExit()
                onGameOverEnter()

        elif IDLE_MODE:
            # check for events
            for event in pygame.event.get():
                # if we press a mouse button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mousePosX, mousePosY = event.pos
                    # left click config
                    if event.button == 1:
                        if PLAY_BUTTON.canClick(mousePosX, mousePosY):
                            ENTER_NAME_MODE = True
                            IDLE_MODE = False
                            onMainMenuExit()
                            onEnterNameEnter()
                            break
                        elif TRAIN_SNAKE_BUTTON.canClick(mousePosX, mousePosY):
                            TRAIN_SNAKE_MODE = True
                            IDLE_MODE = False
                            onMainMenuExit()
                            onTrainSankeEnter()
                            break
                        elif TEST_SNAKE_BUTTON.canClick(mousePosX, mousePosY):
                            TEST_SNAKE_MODE = True
                            IDLE_MODE = False
                            onMainMenuExit()
                            onTestSnakeEnter()
                            break
                        elif HIGH_SCORES_BUTTON.canClick(mousePosX, mousePosY):
                            HIGH_SCORES_MODE = True
                            IDLE_MODE = False
                            onMainMenuExit()
                            onHighScoresEnter()
                            break
                        elif EXIT_GAME_BUTTON.canClick(mousePosX, mousePosY):
                            EXIT_MODE = True
                            IDLE_MODE = False
                            onMainMenuExit()
                            onExitModeEnter()
                            break
        elif ENTER_NAME_MODE:
            textToChange = ENTER_NAME_POPUP.getText()

            # check for events
            for event in pygame.event.get():
                # if we press a mouse button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mousePosX, mousePosY = event.pos
                    # left click config
                    if event.button == 1:
                        if ENTER_NAME_PLAY_GAME_BUTTON.canClick(mousePosX, mousePosY):
                            PLAY_MODE = True
                            ENTER_NAME_MODE = False
                            onEnterNameExit()
                            onPlayGameEnter()
                        elif ENTER_NAME_BACK_TO_MAIN_MENU_BUTTON.canClick(mousePosX, mousePosY):
                            IDLE_MODE = True
                            ENTER_NAME_MODE = False
                            onEnterNameExit()
                            onMainMenuEnter()
                elif event.type == pygame.KEYDOWN:
                    # space key config
                    if event.key == K_BACKSPACE:
                        if len(textToChange) > 12:
                            textToChange = textToChange[0:-1]
                    if event.unicode.isalpha() and event.unicode.isascii():
                        textToChange = textToChange + chr(event.key)
                    ENTER_NAME_POPUP.setText(textToChange)
        elif PLAY_MODE:
            # check for events
            for event in pygame.event.get():
                # if we press a key button
                if event.type == pygame.JOYBUTTONDOWN:
                    # space key config
                    if controller.get_button(CONTROLLER_AXIS_TRIGGERRIGHT):
                        PAUSE_MODE = True
                        PLAY_MODE = False
                        onPlayGameExit()
                        onPauseMenuEnter()
                        break
                    elif controller.get_button(CONTROLLER_BUTTON_X):
                        if DIRECTION != Direction.RIGHT:
                            DIRECTION = Direction.LEFT
                    elif controller.get_button(CONTROLLER_BUTTON_B):
                        if DIRECTION != Direction.LEFT:
                            DIRECTION = Direction.RIGHT
                    elif controller.get_button(CONTROLLER_BUTTON_Y):
                        if DIRECTION != Direction.DOWN:
                            DIRECTION = Direction.UP
                    elif controller.get_button(CONTROLLER_BUTTON_A):
                        if DIRECTION != Direction.UP:
                            DIRECTION = Direction.DOWN

            # play the game
            game_over, score = game.play_step(DIRECTION)

            if game_over:
                PLAY_MODE = False
                GAME_OVER_MODE = True
                onPlayGameExit()
                onGameOverEnter()

        elif GAME_OVER_MODE:
            # check for events
            for event in pygame.event.get():
                # if we press a mouse button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mousePosX, mousePosY = event.pos
                    # left click config
                    if event.button == 1:
                        if PLAY_AGAIN_BUTTON.canClick(mousePosX, mousePosY):
                            if gameAI is not None and agent is not None:
                                TEST_SNAKE_MODE = True
                                GAME_OVER_MODE = False
                                gameAI = None
                                agent = None
                                onGameOverExit()
                                onTestSnakeEnter()
                            else:
                                PLAY_MODE = True
                                GAME_OVER_MODE = False
                                onGameOverExit()
                                onPlayGameEnter()
                            break
                        elif GAME_OVER_BACK_TO_MAIN_MENU_BUTTON.canClick(mousePosX, mousePosY):
                            IDLE_MODE = True
                            GAME_OVER_MODE = False
                            onGameOverExit()
                            onMainMenuEnter()
                            break
        elif PAUSE_MODE:
            # check for events
            for event in pygame.event.get():
                # if we press a mouse button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mousePosX, mousePosY = event.pos
                    # left click config
                    if event.button == 1:
                        if PAUSE_MODE_BACK_TO_MAIN_MENU_BUTTON.canClick(mousePosX, mousePosY):
                            IDLE_MODE = True
                            PAUSE_MODE = False
                            onPauseMenuExit()
                            onMainMenuEnter()
                            break
                        if PAUSE_MODE_RETURN_BUTTON.canClick(mousePosX, mousePosY):
                            PLAY_MODE = True
                            PAUSE_MODE = False
                            onPauseMenuExit()
                            onPlayGameEnter()
                            break
        elif HIGH_SCORES_MODE:
            # check for events
            for event in pygame.event.get():
                # if we press a mouse button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mousePosX, mousePosY = event.pos
                    # left click config
                    if event.button == 1:
                        if HIGH_SCORES_RETURN_BUTTON.canClick(mousePosX, mousePosY):
                            IDLE_MODE = True
                            HIGH_SCORES_MODE = False
                            onHighScoresExit()
                            onMainMenuEnter()
                            break
        elif EXIT_MODE:
            # check for events
            for event in pygame.event.get():
                # if we press a mouse button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mousePosX, mousePosY = event.pos
                    # left click config
                    if event.button == 1:
                        if EXIT_YES_BUTTON.canClick(mousePosX, mousePosY):
                            # Quit Pygame
                            EXIT_MODE = False
                            FORCE_EXIT_MODE = True
                            onExitModeExit()
                            break
                        elif EXIT_NO_BUTTON.canClick(mousePosX, mousePosY):
                            IDLE_MODE = True
                            EXIT_MODE = False
                            onExitModeExit()
                            onMainMenuEnter()
                            break

        # BUTTON RENDER
        PLAY_BUTTON.render(MAIN_WINDOW, PLAY_MODE)
        HIGH_SCORES_BUTTON.render(MAIN_WINDOW, HIGH_SCORES_MODE)
        HIGH_SCORES_RETURN_BUTTON.render(MAIN_WINDOW, False)
        TRAIN_SNAKE_BUTTON.render(MAIN_WINDOW, TRAIN_SNAKE_MODE)
        TEST_SNAKE_BUTTON.render(MAIN_WINDOW, TEST_SNAKE_MODE)
        EXIT_GAME_BUTTON.render(MAIN_WINDOW, False)
        EXIT_YES_BUTTON.render(MAIN_WINDOW, False)
        EXIT_NO_BUTTON.render(MAIN_WINDOW, False)
        PAUSE_MODE_BACK_TO_MAIN_MENU_BUTTON.render(MAIN_WINDOW, False)
        PAUSE_MODE_RETURN_BUTTON.render(MAIN_WINDOW, False)
        PLAY_AGAIN_BUTTON.render(MAIN_WINDOW, False)
        GAME_OVER_BACK_TO_MAIN_MENU_BUTTON.render(MAIN_WINDOW, False)
        ENTER_NAME_PLAY_GAME_BUTTON.render(MAIN_WINDOW, False)
        ENTER_NAME_BACK_TO_MAIN_MENU_BUTTON.render(MAIN_WINDOW, False)

        # POPUP RENDER
        MAIN_MENU_POPUP.render(MAIN_WINDOW)
        DISPLAY_SCORE_POPUP.render(MAIN_WINDOW)
        HIGH_SCORES_POPUP.render(MAIN_WINDOW)
        HIGH_SCORES_RECORD.render(MAIN_WINDOW)
        PAUSE_POPUP.render(MAIN_WINDOW)
        TRAIN_SNAKE_MODE_POPUP.render(MAIN_WINDOW)
        TEST_SNAKE_MODE_POPUP.render(MAIN_WINDOW)
        EXIT_MODE_POPUP.render(MAIN_WINDOW)
        GAME_OVER_POPUP.render(MAIN_WINDOW)
        ENTER_NAME_POPUP.render(MAIN_WINDOW)

        # update pygame display
        pygame.display.update()

    # Force quit the game
    pygame.quit()
