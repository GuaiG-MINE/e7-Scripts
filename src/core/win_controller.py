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
import sys
from pathlib import Path

class WinController:
    def __init__(self, speed_config, image_dir):
        self.speed = speed_config
        
        # 🌟 核心修改：PyInstaller 路径拦截与兼容逻辑
        if hasattr(sys, '_MEIPASS'):
            # 如果是打包后的 exe 运行，强制将图片目录指向系统临时解压目录
            self.image_dir = os.path.join(sys._MEIPASS, 'data', 'images_win')
        else:
            # 如果是平时在 VS Code 里开发运行，保持原样
            self.image_dir = image_dir
            
        # 开启防爆死机制：鼠标移到屏幕四角自动停止脚本
        pyautogui.FAILSAFE = True
        # 设置全局操作停顿时间
        pyautogui.PAUSE = self.speed['global_pause']

    def find_image(self, img_name, conf=0.85, region=None):
        """🛡️ 安全查找图片接口"""
        img_path = str(Path(self.image_dir) / img_name)
        if not os.path.exists(img_path): 
            print(f"❌ 警告：图片文件不存在！路径为: {img_path}")
            return None
        try:
            if region: 
                return pyautogui.locateCenterOnScreen(img_path, confidence=conf, region=region)
            return pyautogui.locateCenterOnScreen(img_path, confidence=conf)
        except pyautogui.ImageNotFoundException:
            print(f"⚠️ 没找到图片: {img_path} (conf={conf})")
            return None
        except Exception as e: 
            # 🌟 真正的异常，用 repr(e) 把错误类型带上，防止又是空字符串
            print(f"❌ 崩溃啦！处理图片 {img_path} 时发生内部错误: {repr(e)}")
            return None

    def click(self, x, y):
        """鼠标点击接口"""
        pyautogui.click(x, y, duration=self.speed['click_move'])

    def swipe_up(self):
        """鼠标拖拽模拟向上滑动屏幕接口 (🌟 宽屏适配 & 大幅度滑动版)"""
        # 寻找商店界面固定存在的“刷新按钮”作为坐标系原点
        anchor = self.find_image('refresh_btn.png', conf=0.75)
        
        if anchor:
            # 🌟 1. 宽屏修正：X轴往右偏移 700，确保鼠标落在右侧的可滑动商品列表内 后续添加不同尺寸大小适配
            start_x = anchor.x + 700
            # 🌟 2. Y轴起点修正：从 -150 改为 -50（稍微往下挪一点），给向上滑动留出更长的“跑道”
            start_y = anchor.y - 50
            
            pyautogui.moveTo(start_x, start_y)
            # 🌟 3. 滑动幅度修正：将向上滑动的距离从 250 加大到 400
            pyautogui.dragTo(start_x, start_y - 400, duration=self.speed['swipe_drag'], button='left')
            time.sleep(self.speed['wait_after_swipe'])
            return True
        else:
            # ❌ 没找到锚点，说明可能不在商店界面或画面被遮挡，拒绝盲目滑动
            print("⚠️ 警告：找不到刷新按钮锚点，无法滑动！请确认在商店界面并且画面无遮挡。")
            return False
        
    def get_screen_size(self):
        """获取屏幕分辨率"""
        return pyautogui.size()
