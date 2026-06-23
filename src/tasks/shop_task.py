#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : shop_task.py
@Author  : Guaig
@Date    : 2026-06-23
@Desc    : 秘密商店自动刷新与购买逻辑实现 (脚本的"大脑")
"""

import time
from src.tasks.base_task import BaseTask

class ShopTask(BaseTask):
    def __init__(self, device, speed_config):
        super().__init__(device, speed_config)
        self.stats = {'blue': 0, 'red': 0}

    def find_and_buy(self, icon_img_name):
        """【精准双重锁定版】左边认图标，右边认 1/1购买 -> 弹窗认全图"""
        icon_center = self.device.find_image(icon_img_name, conf=0.8)
        
        if icon_center:
            item_name = "誓约书签(蓝)" if "blue" in icon_img_name else "神秘奖牌(红)"
            print(f"🎯 发现目标图标 [{item_name}]！正在寻找购买按钮...")
            
            # 划定搜索区域：精准锁定下半区！
            # 起点Y：图标中心往上 15 像素，高度：100 像素 (完美包裹当前按钮，绝对不越界)
            screen_w, screen_h = self.device.get_screen_size()
            search_region = (0, max(0, int(icon_center.y - 15)), screen_w, 100)

            # 找新的带有 1/1 的购买按钮
            buy_center = self.device.find_image('buy_btn.png', conf=0.75, region=search_region)
            
            if buy_center:
                self.device.click(buy_center.x, buy_center.y)
                time.sleep(self.speed['wait_popup'])  
                
                # 🌟 动态决定要找哪张完整的确认图
                confirm_img = 'confirm_buy_blue.png' if "blue" in icon_img_name else 'confirm_buy_red.png'
                confirm_center = self.device.find_image(confirm_img, conf=0.8)
                
                if confirm_center:
                    self.device.click(confirm_center.x, confirm_center.y)
                    print(f"✅ 成功进货 1 次 {item_name}！")
                    time.sleep(self.speed['wait_buy_done'])
                    return True
                else:
                    print(f"⚠️ 没找到弹窗的确认按钮({confirm_img})，点空白处防卡死...")
                    self.device.click(icon_center.x, icon_center.y - 200)
                    time.sleep(self.speed['wait_cancel'])
            else:
                print("⚠️ 找到图标了，但没找到右侧的 [1/1 购买] 按钮？")
                
        return False

    def refresh_shop(self):
        """刷新商店并确认"""
        refresh_center = self.device.find_image('refresh_btn.png', conf=0.85)
        if refresh_center:
            self.device.click(refresh_center.x, refresh_center.y)
            time.sleep(self.speed['wait_refresh_pop'])
            
            confirm_center = self.device.find_image('confirm_refresh_btn.png', conf=0.85)
            if confirm_center:
                self.device.click(confirm_center.x, confirm_center.y)
                time.sleep(self.speed['wait_refresh_done'])

    def run(self):
        """任务主循环"""
        print("请在 3 秒内切换到游戏画面...")
        time.sleep(3)
        
        loop_count = 1
        while True:
            print(f"\n--- 第 {loop_count} 次巡逻 ---")
            
            # 每一轮刷新后，重置购买状态
            blue_bought = False
            red_bought = False
            
            # 1️⃣ 上半区搜寻
            if self.find_and_buy('icon_blue.png'):
                self.stats['blue'] += 1
                blue_bought = True
                
            if self.find_and_buy('icon_red.png'):
                self.stats['red'] += 1
                red_bought = True
                
            # 2️⃣ 判断是否需要滑动（如果两个都买到了，直接跳过滑动，进入刷新！）
            if not (blue_bought and red_bought):
                self.device.swipe_up()
                
                # 3️⃣ 下半区搜寻 (只找上半区没买到的东西！)
                if not blue_bought and self.find_and_buy('icon_blue.png'):
                    self.stats['blue'] += 1
                    
                if not red_bought and self.find_and_buy('icon_red.png'):
                    self.stats['red'] += 1
            else:
                print("🎉 天胡开局！上半区已全收，直接刷新！")
                
            print(f"🏆 战绩: 蓝票 {self.stats['blue']} | 红票 {self.stats['red']}")
            
            # 4️⃣ 刷新商店
            self.refresh_shop()
            
            loop_count += 1
            time.sleep(self.speed['loop_interval'])
