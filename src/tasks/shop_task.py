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
        if not self._running: return False  # 🛑 收到停止指令，直接退出
        
        icon_center = self.device.find_image(icon_img_name, conf=0.8)
        
        if icon_center:
            item_name = "誓约书签(蓝)" if "blue" in icon_img_name else "神秘奖牌(红)"
            print(f"🎯 发现目标图标 [{item_name}]！正在寻找购买按钮...")
            
            screen_w, screen_h = self.device.get_screen_size()
            search_region = (0, max(0, int(icon_center.y - 15)), screen_w, 100)

            buy_center = self.device.find_image('buy_btn.png', conf=0.75, region=search_region)
            
            if buy_center:
                self.device.click(buy_center.x, buy_center.y)
                time.sleep(self.speed['wait_popup'])  
                
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
        if not self._running: return  # 🛑 收到停止指令，不执行刷新
        
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
        # 把 3 秒等待拆成小段，这样在这 3 秒内点停止也能立刻生效
        for _ in range(3):
            if not self._running: return
            time.sleep(1)
        
        loop_count = 1
        # ✅ 核心修改：把 while True 改成 while self._running
        while self._running:
            print(f"\n--- 第 {loop_count} 次巡逻 ---")
            
            blue_bought = False
            red_bought = False
            
            # 1️⃣ 上半区搜寻
            if self.find_and_buy('icon_blue.png'):
                self.stats['blue'] += 1
                blue_bought = True
                
            if self.find_and_buy('icon_red.png'):
                self.stats['red'] += 1
                red_bought = True
                
            if not self._running: break  # 🛑 随时检查是否需要停止
                
            # 2️⃣ 判断是否需要滑动
            if not (blue_bought and red_bought):
                # ✅ 接收滑动结果
                swipe_success = self.device.swipe_up()
                if not self._running: break  # 🛑 滑动后检查
                
                # ✅ 如果滑动失败（没找到锚点），则警告并重试
                if not swipe_success:
                    print("⚠️ 警告：找不到刷新按钮锚点！可能不在商店界面或画面被遮挡。")
                    print("⏳ 暂停 3 秒后重试...")
                    time.sleep(3)
                    continue  # 跳过后续步骤，直接进入下一轮循环重新识别
                
                # 3️⃣ 下半区搜寻
                if not blue_bought and self.find_and_buy('icon_blue.png'):
                    self.stats['blue'] += 1
                    
                if not red_bought and self.find_and_buy('icon_red.png'):
                    self.stats['red'] += 1
            else:
                print("🎉 天胡开局！上半区已全收，直接刷新！")
                
            print(f"🏆 战绩: 书签 {self.stats['blue']} | 神秘 {self.stats['red']}")
            
            if not self._running: break  # 🛑 刷新前检查
            
            # 4️⃣ 刷新商店
            self.refresh_shop()
            
            loop_count += 1
            
            # 把末尾的等待时间拆解，保证停止按钮“秒级响应”
            wait_time = self.speed['loop_interval']
            for _ in range(int(wait_time * 10)):
                if not self._running: break
                time.sleep(0.1)
