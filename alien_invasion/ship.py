import pygame
from pygame.sprite import Sprite

class Ship(Sprite):
    """"管理飞船的类"""

    def __init__(self,ai_game):
        """初始化飞船并设置其初始位置"""
        super().__init__()
        self.screen=ai_game.screen
        self.screen_rect=self.screen.get_rect()

        self.settings=ai_game.settings  #获取游戏设置

        #加载飞船图像并获取其外接矩形
        self.image=pygame.image.load('./images/ship.bmp')
        self.rect=self.image.get_rect()

        #每艘飞船最初都在屏幕底部中央
        self.rect.midbottom=self.screen_rect.midbottom

        #飞船的x坐标
        self.x=float(self.rect.x)  #self.rect.x只能是int类型，所以这里间接的使用了一个self.x

        self.moving_right = False  # 飞船右移标志
        self.moving_left = False   # 飞船左移标志

    def update(self):
        """更新游戏数据"""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # 更新飞船的rect对象(只存储self.x的整数部分)
        self.rect.x = self.x

    def blitme(self):
        """在指定位置绘制飞船"""
        self.screen.blit(self.image,self.rect)

    def center_ship(self):
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)