import random
from enum import Enum
from collections import namedtuple
import pygame
import numpy as np


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


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


class SnakeGameAI:

    def __init__(self, gamemode, display, DISPLAY_SCORE_POPUP, agentMode="Train"):
        self.DISPLAY_SCORE_POPUP = DISPLAY_SCORE_POPUP
        self.w = display.get_width()
        self.h = display.get_height()
        self.gamemode = gamemode
        # init display
        self.display = display
        self.clock = pygame.time.Clock()
        self.agentMode = agentMode
        self.reset()

    def reset(self):
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
        self.frame_iteration = 0

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

    def play_step(self, action):
        self.frame_iteration += 1

        # 2. move
        self._move(action)  # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or ((self.frame_iteration > 100 * len(self.snake)) and self.agentMode == "Train"):
            game_over = True
            reward = -10
            self.checkIfHighscore()
            self.updateScoresHistory()
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self.DISPLAY_SCORE_POPUP.setText("Score: " + str(self.score))
            self._place_food()
            self.speed += 1
        else:
            self.snake.pop()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(self.speed)

        # 6. return game over and score
        return reward, game_over, self.score

    def checkIfHighscore(self):
        player_name = f"Snake God {self.score}"

        if self.score > self.highscore:
            f = open("highscore.txt", "w")
            f.write(player_name)
            f.close()

    def updateScoresHistory(self):
        player_name = f"Snake God {self.score}"
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

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        if self.gamemode == "walls":
            if pt in self.walls:
                return True
        # hits itself
        if pt in self.snake[1:]:
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

    def _move(self, action):
        # [straight, right, left]
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            if self.head.x == self.w - BLOCK_SIZE:
                x = 0
            else:
                x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            if self.head.x == 0:
                x = self.w - BLOCK_SIZE
            else:
                x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            if self.head.y == self.h - BLOCK_SIZE:
                y = 0
            else:
                y += BLOCK_SIZE
        elif self.direction == Direction.UP:
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
