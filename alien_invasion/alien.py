import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    def __init__(self,ai_game):
        super().__init__()
        self.screen=ai_game.screen
        self.settings=ai_game.settings

        self.image=pygame.image.load('./images/alien.bmp')
        self.rect=self.image.get_rect()

        # 设置每个外星人初始位置在左上角附近
        self.rect.x=self.rect.width
        self.rect.y=self.rect.height

        # 存储外星人的准确位置
        self.x=float(self.rect.x)

    def update(self):
        self.x += (self.settings.alien_speed*self.settings.fleet_direction)
        self.rect.x=self.x

    def _check_edge(self):
        if self.rect.left<=0 or self.rect.right>=self.screen.get_rect().right:
            return True