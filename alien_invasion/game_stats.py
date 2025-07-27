import json
import os
class GameStats:
    """跟踪游戏的统计信息"""

    def __init__(self,ai_game):
        """初始化统计信息"""
        self.settings=ai_game.settings
        self.game_active=False  # 游戏是否处于活动状态
        self.reset_stats()

        #记分
        self.score=0
        self.high_score=0 #最高得分

        #历史最高得分文件名
        self.file_name='highest_score.json'
        if not os.path.isfile(self.file_name):
            self.dump_highest_score()
        else:
            self.load_highest_score()

    def reset_stats(self):
        """重置游戏状态"""
        self.ships_left=self.settings.ship_limit  # 剩余飞船数
        self.score=0 #玩家得分
        self.level=1 #玩家等级

    def dump_highest_score(self):
        with open(self.file_name,'w') as f:
            json.dump(self.high_score,f)

    def load_highest_score(self):
        with open(self.file_name) as f:
            self.high_score=json.load(f)

    