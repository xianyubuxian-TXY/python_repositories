import sys
from time import sleep
import pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
    """管理游戏资源和行为的类"""
    
    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.settings=Settings() # 创建一个设置实例，存储游戏设置

        self.screen=pygame.display.set_mode(
            (self.settings.screen_width,self.settings.screen_height)) # 设置窗口像素，并返回”窗口对象“，用于之后设置窗口属性
        
        pygame.display.set_caption("Alien Invasion")  # 设置窗口主题

        self.stats=GameStats(self)  # 创建一个游戏统计实例，用于跟踪游戏状态

        self.ship=Ship(self)  # 创建飞船实例

        self.bullets=pygame.sprite.Group()  # 创建一个子弹编组，用于存储所有子弹

        self.aliens=pygame.sprite.Group()  # 创建一个外星人编组，用于存储所有外星人
        self._create_fleet()  # 创建外星人群

        self.play_button=Button(self,"Play") #创建Play按钮

        self.scoreboard=Scoreboard(self)  #创建记分牌

    def run_game(self):
        """游戏主循环"""
        while True:
            #监视键盘和鼠标事件
            self._check_events()

            if self.stats.game_active:
                #更新飞船数据
                self.ship.update()
                #更新子弹数据
                self._update_bullets()
                #更新外星人数据
                self._update_aliens()

            #更新屏幕上的图像
            self._update_screen()


    def _check_events(self):
        """响应按键和鼠标事件"""
        for event in pygame.event.get():
            # 退出事件
            if event.type == pygame.QUIT:
                sys.exit()

            # 按键按下事件
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            
            # 按键抬起事件
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

            elif event.type==pygame.MOUSEBUTTONDOWN:
                mouse_pos=pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
    
    # 处理按键按下事件
    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:  # 按下右箭头键时，飞船向右移动
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT: # 按下左箭头键时，飞船向左移动
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE: # 按下空格键时，发射子弹
            self._fire_bullet()
        elif event.key == pygame.K_q: # 按下ESC键时，退出游戏
            sys.exit()
        
    # 处理按键抬起事件
    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT: # 抬起右箭头键时，停止飞船向右移动
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT: # 抬起左箭头键时，停止飞船向左移动
            self.ship.moving_left = False


    # 检查外星人群是否到达屏幕边缘：每当存在外星人触碰屏幕边缘，外星人群位置下移，位移方向改变
    def _check_fleet_edges(self):
        """响应外星人到达屏幕边缘"""
        for alien in self.aliens.sprites():
            if alien._check_edge():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """将外星人群向下移动，并改变移动方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_bullet_alien_collisions(self):
        """检查子弹与外星人碰撞，并删除发生碰撞的子弹和外星人"""
        # 检查子弹与外星人碰撞并删除发生碰撞的子弹和外星人
        collisions=pygame.sprite.groupcollide(
            self.bullets,self.aliens,True,True) # 第一个True表示删除子弹，第二个True表示删除外星人
        # 每击杀一个敌人，分数增加
        if collisions:
            for aliens in collisions.values():
                self.stats.score+=self.settings.alien_points*len(aliens)
            self.scoreboard.prep_score()
            self.scoreboard.check_high_score()

        # 外星人被消灭完后，生成新的一批外星人，同时消除屏幕中的子弹，并加快游戏节奏
        if not self.aliens:
            self.bullets.empty()  # 清空子弹编组
            self._create_fleet()  # 创建新的外星人群
            self.settings.increase_speed() #加快游戏节奏
            #提高等级
            self.stats.level+=1
            self.scoreboard.prep_level()

    def _check_aliens_bottom(self):
        screen_rect=self.screen.get_rect()
        for aline in self.aliens.sprites():
            if aline.rect.bottom >= screen_rect.bottom:
                """如果外星人到达屏幕底部，结束游戏"""
                self._ship_hit()
                break

    def _check_play_button(self,mouse_pos):
        """在玩家点击Play按钮且游戏状态game_active==Fasle时开启新游戏"""
        button_clicked=self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.stats.reset_stats()
            self.stats.game_active=True

            #面板初始化
            self.scoreboard.prep_score()
            self.scoreboard.prep_level()
            self.scoreboard.prep_ships()

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()

            #重置游戏节奏
            self.settings.initialize_dynamic_settings()

            #隐藏鼠标
            pygame.mouse.set_visible(False)


    # 更新屏幕
    def _update_screen(self):
        """更新屏幕上的图像，并切换到新屏幕"""
        #填充背景
        self.screen.fill(self.settings.bg_color)

        #绘制飞船
        self.ship.blitme()

        #绘制子弹
        for bullet in self.bullets:
            bullet.draw_bullet()

        #绘制外星人群
        self.aliens.draw(self.screen)

        #绘制Play按钮
        if not self.stats.game_active:
            self.play_button.draw_button()

        #显示得分
        self.scoreboard.show_score()

        #更新屏幕
        pygame.display.flip()

    # 更新子弹
    def _update_bullets(self):
        """更新子弹"""
        self.bullets.update()

        #删除超出屏幕顶部的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        #print(len(self.bullets)) # 打印当前子弹数量，便于调试

        self._check_bullet_alien_collisions()  # 检查子弹与外星人碰撞


    # 检查子弹
    def _update_aliens(self):
        """更新外星人"""
        self._check_fleet_edges()  # 检查外星人群是否到达屏幕边缘
        self.aliens.update()

        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            """如果飞船与外星人发生碰撞，结束游戏"""
            self._ship_hit()

        # 检查是否有外星人到达了屏幕底端
        self._check_aliens_bottom()

    # 创建子弹并添加到编组中
    def _fire_bullet(self):
        """创建一个子弹并将其添加到编组bullets中"""
        if len(self.bullets)<self.settings.bullets_allowed:
            new_bullet=Bullet(self)
            self.bullets.add(new_bullet)

    def _ship_hit(self):
        self.stats.ships_left -= 1  # 飞船数量减1
        if self.stats.ships_left > 0:  # 如果飞船数量大于0
            self.scoreboard.prep_ships() #更新剩余飞船命数
            self.aliens.empty()  # 清空外星人编组
            self.bullets.empty()  # 清空子弹编组
            self._create_fleet()
            self.ship.center_ship()  # 将飞船放置在屏幕底部中央
            # 暂停游戏
            sleep(0.5)
        else:
            self.stats.game_active = False  # 如果游戏结束，设置游戏状态为不活跃
            print("Game Over! No ships left.")  # 打印游戏结束信息
            #显示鼠标
            pygame.mouse.set_visible(True)

    # 创建外星人群
    def _create_fleet(self):
        """创建外星人群"""
        #创建一个外星人用来计算每行可以容纳多少外星人（屏幕左右空出一个外星人宽度，相邻外星人之间间隔一个外星人宽度）
        alien=Alien(self)
        alien_width,alien_hieght=alien.rect.size
        available_space_x=self.screen.get_width()-(2*alien_width)  # 屏幕宽度减去两侧的外星人宽度
        number_aliens_x=available_space_x//(2*alien_width) #每两个外星人宽度空间容纳一个外星人

        #计算屏幕可容纳多少行外星人
        ship_height=self.ship.rect.height
        available_space_y=self.screen.get_height()-(3*alien_hieght)-ship_height

        num_rows= available_space_y // (2 * alien_hieght)

        # 创建外星人群
        for row_idx in range(num_rows):
            for alien_idx in range(number_aliens_x):
                # 创建外星人并添加到外星人群中
                alien=self._create_alien(alien_idx,row_idx)
                self.aliens.add(alien)

    # 创建外星人
    def _create_alien(self,alien_idx,row_idx):
        alien=Alien(self)
        alien_width,alien_height=alien.rect.size
        alien.x=alien_width+2*alien_width*alien_idx
        alien.y=alien_height+2*alien_height*row_idx
        alien.rect.x=alien.x
        alien.rect.y=alien.y
        return alien


if __name__ == '__main__':
    #创建游戏实例并运行
    ai = AlienInvasion()
    ai.run_game()