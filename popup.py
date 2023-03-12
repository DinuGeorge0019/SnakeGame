import pygame

COLOR_GRAY = 100, 100, 100
COLOR_WHITE = 255, 255, 255


class Popup:
    def __init__(self, text, textBox, displayTime=None) -> None:
        self.text = text
        self.displayTime = displayTime
        self.isDisplaying = 0  # -1 -> always on; 0 -> hidden; greater then 0 timer is on
        self.textBox = textBox
        self.textFont = pygame.font.SysFont('Arial', 20)
    
    def setText(self, text):
        self.text = text

    def getText(self):
        return self.text

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

    def render(self, screen):
        if self.isDisplaying != 0:
            # render textbox background
            pygame.draw.rect(screen, COLOR_GRAY, self.textBox, 0, 5)
            # calculate the center point of the text box
            boxCenterPosX = self.textBox.x + int(self.textBox.w / 2)
            boxCenterPosY = self.textBox.y + int(self.textBox.h / 2)
            # render text
            texts = self.textFont.render(str(self.text), True, COLOR_WHITE)
            textOffsetPosX = int(texts.get_rect().width / 2)
            textOffsetPosY = int(texts.get_rect().height / 2)
            screen.blit(texts, (boxCenterPosX - textOffsetPosX, boxCenterPosY - textOffsetPosY))
