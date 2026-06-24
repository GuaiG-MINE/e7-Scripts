#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : shop_task.py
@Author  : Guaig
@Date    : 2026-06-24
@Desc    : 秘密商店自动刷新与购买逻辑实现 (脚本的"大脑")
"""

import time
from src.tasks.base_task import BaseTask

class ShopTask(BaseTask):
    def __init__(self, device, speed_config, log_callback=None, stats_callback=None):
        super().__init__(device, speed_config)        
        self.stats = {'blue': 0, 'red': 0, 'refresh': 0}
        self.log_callback = log_callback
        self.stats_callback = stats_callback 

    def log(self, message, level="info"):
        print(message)  
        if self.log_callback and level != "debug":
            self.log_callback(message)

    def _notify_stats_update(self):
        if self.stats_callback:
            self.stats_callback(self.stats['blue'], self.stats['red'], self.stats['refresh'])

    # 🌟 1. 新增 use_cache 参数
    def find_and_buy(self, icon_img_name, use_cache=False):
        """【精准双重锁定版】左边认图标，右边认 1/1购买 -> 弹窗认全图"""
        if not self._running: return False
        
        # 🌟 2. 找图标时，根据外部传入决定是否使用缓存
        icon_center = self.device.find_image(icon_img_name, conf=0.8, use_cache=use_cache)
        
        if icon_center:
            item_name = "誓约书签(蓝)" if "blue" in icon_img_name else "神秘奖牌(红)"
            self.log(f"🎯 发现目标 [{item_name}]！正在寻找购买按钮...", level="debug")
            
            is_adb = hasattr(self.device, 'serial')
            
            if is_adb:
                offset_y = 50
                safe_height_limit = 200
            else:
                offset_y = 15
                safe_height_limit = 100
                
            screen_w, screen_h = self.device.get_screen_size()
            
            top_y = max(0, int(icon_center.y - offset_y))
            left_x = int(icon_center.x)
            safe_width = screen_w - left_x
            safe_height = min(safe_height_limit, screen_h - top_y) 
            
            search_region = (left_x, top_y, safe_width, safe_height)

            # 🌟 3. 找购买按钮时，画面绝对没变，100% 使用缓存提速！
            buy_center = self.device.find_image('buy_btn.png', conf=0.9, region=search_region, use_cache=True)
            
            if buy_center:
                self.device.click(buy_center.x, buy_center.y)
                time.sleep(self.speed['wait_popup'])  
                
                confirm_img = 'confirm_buy_blue.png' if "blue" in icon_img_name else 'confirm_buy_red.png'
                # 🌟 4. 找确认弹窗时，画面弹出了新东西，绝对不能用缓存！
                confirm_center = self.device.find_image(confirm_img, conf=0.8, use_cache=False)
                
                if confirm_center:
                    self.device.click(confirm_center.x, confirm_center.y)
                    self.log(f"✅ 成功进货 1 次 {item_name}！")
                    time.sleep(self.speed['wait_buy_done'])
                    return True
                else:
                    self.log(f"⚠️ 点了购买但没出弹窗，直接跳过防误触...", level="warning")
                    time.sleep(self.speed['wait_cancel'])
            else:
                self.log("⚠️ 找到图标了，但没找到右侧的 [1/1 购买] 按钮？", level="warning")
                
        return False

    def refresh_shop(self):
        """刷新商店并确认"""
        if not self._running: return
        
        # 刷新按钮稳妥起见，不使用缓存，强制拍一张最新照片
        refresh_center = self.device.find_image('refresh_btn.png', conf=0.85, use_cache=False)
        if refresh_center:
            self.device.click(refresh_center.x, refresh_center.y)
            time.sleep(self.speed['wait_refresh_pop'])
            
            # 弹窗必须不能用缓存
            confirm_center = self.device.find_image('confirm_refresh_btn.png', conf=0.85, use_cache=False)
            if confirm_center:
                self.device.click(confirm_center.x, confirm_center.y)
                
                self.stats['refresh'] += 1
                self._notify_stats_update()  
                
                time.sleep(self.speed['wait_refresh_done'])

    def run(self):
        """任务主循环"""
        self.log("⏳ 请在 3 秒内确保画面停留在【秘密商店】...")
        for _ in range(3):
            if not self._running: return
            time.sleep(1)
            
        if not self.device.find_image('refresh_btn.png', conf=0.8, use_cache=False):
            self.log("⚠️ 警告：未检测到商店界面！请确认画面无遮挡且停留在秘密商店。", level="warning")
            self.log("脚本将继续尝试运行，如果一直无反应请手动停止。", level="warning")
        else:
            self.log("✅ 成功识别到商店界面，开始执行任务！")
        
        loop_count = 1
        while self._running:
            self.log(f"\n--- 第 {loop_count} 次巡逻 ---", level="debug")
            
            blue_bought = False
            red_bought = False
            
            # ================= 上半区 =================
            # 1. 刚开始巡逻，必须拍一张新照片 (use_cache=False)
            blue_bought_top = False
            if self.find_and_buy('icon_blue.png', use_cache=False):
                self.stats['blue'] += 1
                blue_bought = True
                blue_bought_top = True
                self._notify_stats_update()  
                
            # 2. 如果上半区买了蓝书签，画面变了，不能用缓存；如果没买，直接白嫖刚才的照片！
            use_cache_for_red_top = not blue_bought_top
            if self.find_and_buy('icon_red.png', use_cache=use_cache_for_red_top):
                self.stats['red'] += 1
                red_bought = True
                self._notify_stats_update()  
                
            if not self._running: break
                
            if not (blue_bought and red_bought):
                # ================= 滑动 =================
                swipe_success = self.device.swipe_up()
                if not self._running: break
                
                if not swipe_success:
                    self.log("⚠️ 警告：找不到刷新按钮锚点！可能不在商店界面或画面被遮挡。", level="warning")
                    self.log("⏳ 暂停 3 秒后重试...", level="warning")
                    time.sleep(3)
                    continue
                
                # ================= 下半区 =================
                blue_bought_bottom = False
                first_check_bottom = True # 标记下半区是否已经拍过照片了
                
                if not blue_bought:
                    # 3. 滑动后画面变了，必须拍新照片 (use_cache=False)
                    if self.find_and_buy('icon_blue.png', use_cache=False):
                        self.stats['blue'] += 1
                        blue_bought = True
                        blue_bought_bottom = True
                        self._notify_stats_update()  
                    first_check_bottom = False
                    
                if not red_bought:
                    # 4. 终极逻辑：
                    # 如果 first_check_bottom 是 True，说明刚才没找蓝书签，现在必须拍新照片。
                    # 如果 first_check_bottom 是 False，说明找过蓝书签了，只要没买(没弹窗)，就能白嫖照片！
                    use_cache_for_red_bottom = (not first_check_bottom) and (not blue_bought_bottom)
                    if self.find_and_buy('icon_red.png', use_cache=use_cache_for_red_bottom):
                        self.stats['red'] += 1
                        red_bought = True
                        self._notify_stats_update()  
            else:
                self.log("🎉 天胡开局！上半区已全收，直接刷新！")
                
            if blue_bought or red_bought:
                self.log(f"🏆 战绩更新: 书签 {self.stats['blue']} | 神秘 {self.stats['red']} | 刷新 {self.stats['refresh']}")
            else:
                self.log(f"🏆 当前战绩: 书签 {self.stats['blue']} | 神秘 {self.stats['red']} | 刷新 {self.stats['refresh']}", level="debug")
            
            if not self._running: break
            
            self.refresh_shop()
            loop_count += 1
            
            wait_time = self.speed['loop_interval']
            for _ in range(int(wait_time * 10)):
                if not self._running: break
                time.sleep(0.1)
