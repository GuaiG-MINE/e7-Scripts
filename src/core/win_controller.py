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
from PIL import Image  # 🌟 新增：用于将图片读取到内存

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
            
        # 🌟 性能优化：创建图片内存缓存池
        self.image_cache = {}
            
        # 开启防爆死机制：鼠标移到屏幕四角自动停止脚本
        pyautogui.FAILSAFE = True
        # 设置全局操作停顿时间
        pyautogui.PAUSE = self.speed['global_pause']

    def find_image(self, img_name, conf=0.85, region=None):
        """🛡️ 安全查找图片接口 (带内存缓存优化)"""
        
        # 🌟 1. 如果缓存里没有，才去硬盘读
        if img_name not in self.image_cache:
            img_path = str(Path(self.image_dir) / img_name)
            if not os.path.exists(img_path): 
                print(f"❌ 警告：图片文件不存在！路径为: {img_path}")
                return None
            try:
                # 使用 PIL 将图片读入内存并存入缓存
                self.image_cache[img_name] = Image.open(img_path)
            except Exception as e:
                print(f"❌ 无法读取图片 {img_path}: {repr(e)}")
                return None
                
        # 🌟 2. 直接从缓存中获取图片对象
        cached_img = self.image_cache[img_name]

        try:
            # pyautogui 支持直接传入 Image 对象，省去了重复读硬盘的时间！
            if region: 
                return pyautogui.locateCenterOnScreen(cached_img, confidence=conf, region=region)
            return pyautogui.locateCenterOnScreen(cached_img, confidence=conf)
        except pyautogui.ImageNotFoundException:
            # 找不到图是正常现象，不需要打印报错，保持安静即可（或者你想打印也可以放开）
            # print(f"⚠️ 没找到图片: {img_name} (conf={conf})")
            return None
        except Exception as e: 
            # 🌟 真正的异常，用 repr(e) 把错误类型带上
            print(f"❌ 崩溃啦！处理图片 {img_name} 时发生内部错误: {repr(e)}")
            return None

    def click(self, x, y):
        """鼠标点击接口"""
        pyautogui.click(x, y, duration=self.speed['click_move'])

    def swipe_up(self):
        """鼠标拖拽模拟向上滑动屏幕接口 (🌟 宽屏适配 & 大幅度滑动版)"""
        # 寻找商店界面固定存在的“刷新按钮”作为坐标系原点
        anchor = self.find_image('refresh_btn.png', conf=0.75)
        
        if anchor:
            # 🌟 1. 宽屏修正：X轴往右偏移 700
            start_x = anchor.x + 700
            # 🌟 2. Y轴起点修正：从 -150 改为 -50
            start_y = anchor.y - 50
            
            pyautogui.moveTo(start_x, start_y)
            # 🌟 3. 滑动幅度修正：将向上滑动的距离从 250 加大到 400
            pyautogui.dragTo(start_x, start_y - 400, duration=self.speed['swipe_drag'], button='left')
            time.sleep(self.speed['wait_after_swipe'])
            return True
        else:
            # ❌ 没找到锚点
            print("⚠️ 警告：找不到刷新按钮锚点，无法滑动！请确认在商店界面并且画面无遮挡。")
            return False
        
    def get_screen_size(self):
        """获取屏幕分辨率"""
        return pyautogui.size()
