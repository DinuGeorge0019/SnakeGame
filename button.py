import pygame

COLOR_WHITE = 255, 255, 255
COLOR_GRAY = 100, 100, 100
COLOR_BLACK = 0, 0, 0


class Button:
    def __init__(self, buttonPos, width, height, text, displayTime=None) -> None:
        self.posX, self.posY = buttonPos
        self.height = height
        self.width = width
        self.text = text
        pygame.font.init()
        self.textFont = pygame.font.SysFont('Arial', 20)
        self.displayTime = displayTime
        self.isDisplaying = 0  # -1 -> always on; 0 -> hidden; greater then 0 timer is on

    def show(self):
        # if the the timer is set start displaying
        if self.isDisplaying:
            self.isDisplaying = self.displayTime
        # else we are in always on mode
        else:
            self.isDisplaying = -1

    def hide(self):
        # hide the popout
        self.isDisplaying = 0

    def update(self):
        # if the timer is set then start displaying and decreasing timer
        if self.isDisplaying > 0:
            self.isDisplaying -= 1

    def canClick(self, mousePosX, mousePosY):
        if not self.isDisplaying:
            return False
        if mousePosX < self.posX or mousePosX > self.posX + self.width:
            return False
        if mousePosY < self.posY or mousePosY > self.posY + self.height:
            return False
        return True

    def render(self, screen, isClicked=False):
        if self.isDisplaying != 0:
            # render the node depending of button state
            if isClicked:
                pygame.draw.rect(screen, COLOR_GRAY, pygame.Rect(self.posX, self.posY, self.width, self.height), 0, 5)
            else:
                pygame.draw.rect(screen, COLOR_WHITE, pygame.Rect(self.posX, self.posY, self.width, self.height), 0, 5)

            # calculate the center of the button
            buttonCenterX = self.posX + int(self.width / 2)
            buttonCenterY = self.posY + int(self.height / 2)

            # position the text in the center of the button
            text = self.textFont.render(str(self.text), True, COLOR_BLACK)
            textOffsetPosX = int(text.get_rect().width / 2)
            textOffsetPosY = int(text.get_rect().height / 2)
            screen.blit(text, (buttonCenterX - textOffsetPosX, buttonCenterY - textOffsetPosY))
