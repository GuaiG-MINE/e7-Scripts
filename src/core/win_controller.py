#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : win_controller.py
@Author  : Guaig
@Date    : 2026-06-23
@Desc    : Windows 平台控制器，基于 pyautogui 实现鼠标点击、滑动与图像识别 (脚本的"手脚")
"""

import pyautogui
import time
import os

class WinController:
    def __init__(self, speed_config, image_dir):
        self.speed = speed_config
        self.image_dir = image_dir
        
        # 开启防爆死机制：鼠标移到屏幕四角自动停止脚本
        pyautogui.FAILSAFE = True
        # 设置全局操作停顿时间
        pyautogui.PAUSE = self.speed['global_pause']

    def find_image(self, img_name, conf=0.85, region=None):
        """🛡️ 安全查找图片接口"""
        img_path = os.path.join(self.image_dir, img_name)
        if not os.path.exists(img_path): 
            return None
        try:
            if region: 
                return pyautogui.locateCenterOnScreen(img_path, confidence=conf, region=region)
            return pyautogui.locateCenterOnScreen(img_path, confidence=conf)
        except Exception: 
            return None

    def click(self, x, y):
        """鼠标点击接口"""
        pyautogui.click(x, y, duration=self.speed['click_move'])

    def swipe_up(self):
        """鼠标拖拽模拟向上滑动屏幕接口 (🌟 动态视觉锚点版)"""
        # 寻找商店界面固定存在的“刷新按钮”作为坐标系原点
        anchor = self.find_image('refresh_btn.png', conf=0.75)
        
        if anchor:
            # 在刷新按钮右上方的一块安全区域进行滑动，确保一定划在游戏窗口内
            start_x = anchor.x + 300
            start_y = anchor.y - 150
            
            pyautogui.moveTo(start_x, start_y)
            pyautogui.dragTo(start_x, start_y - 250, duration=self.speed['swipe_drag'], button='left')
            time.sleep(self.speed['wait_after_swipe'])
            return True
        else:
            # ❌ 没找到锚点，说明可能不在商店界面或画面被遮挡，拒绝盲目滑动
            return False
        
    def get_screen_size(self):
        """获取屏幕分辨率"""
        return pyautogui.size()
