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
from PIL import Image

from src.core.logger import log_manager

# 模拟 ADB 模式的 Point 对象，保持上层接口完全一致
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class WinController:
    # ✅ 标识设备类型，供 ShopTask 安全判断
    is_adb = False

    def __init__(self, speed_config, image_dir):
        self.speed = speed_config
        
        # 🌟 核心清理：彻底解耦！直接使用 Runner 传来的绝对路径，不再关心是否打包
        self.image_dir = image_dir
            
        self.image_cache = {}
        self._cached_screen = None  # 🌟 新增：用于保存全屏截图的缓存
            
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = self.speed['global_pause']

    def clear_cache(self):
        """清理内存缓存，释放资源"""
        self.image_cache.clear()
        self._cached_screen = None
        log_manager.debug("🧹 已清空 Win 图片及屏幕缓存")

    def find_image(self, img_name, conf=0.8, region=None, use_cache=False):
        """🌟 移除了 sticky，并真正实现了 use_cache 逻辑"""
        # --- 1. 模板图缓存 ---
        if img_name not in self.image_cache:
            img_path = str(Path(self.image_dir) / img_name)
            if not os.path.exists(img_path):
                log_manager.error(f"❌ 警告：图片文件不存在！路径为: {img_path}")
                return None
            try:
                self.image_cache[img_name] = Image.open(img_path)
            except Exception as e:
                log_manager.error(f"❌ 无法读取图片 {img_path}: {repr(e)}")
                return None

        needle = self.image_cache[img_name]

        try:
            # --- 2. 屏幕画面真缓存逻辑 ---
            if not use_cache or self._cached_screen is None:
                self._cached_screen = pyautogui.screenshot()
            
            haystack = self._cached_screen

            # --- 3. 区域裁剪与匹配 ---
            if region:
                x, y, w, h = [int(v) for v in region]
                # 裁剪目标区域
                haystack = haystack.crop((x, y, x + w, y + h))
                
                # 在裁剪后的图片中寻找
                box = pyautogui.locate(needle, haystack, confidence=conf)
                if box:
                    center = pyautogui.center(box)
                    # 换算回全屏绝对坐标
                    return Point(center.x + x, center.y + y)
                return None
            else:
                box = pyautogui.locate(needle, haystack, confidence=conf)
                if box:
                    center = pyautogui.center(box)
                    return Point(center.x, center.y)
                return None
                
        except pyautogui.ImageNotFoundException:
            return None
        except Exception as e:
            log_manager.error(f"❌ 处理图片 {img_name} 时发生内部错误: {repr(e)}")
            return None

    def click(self, x, y):
        """鼠标点击接口"""
        pyautogui.click(x, y, duration=self.speed['click_move'])

    def swipe_up(self):
        """鼠标拖拽模拟向上滑动屏幕接口"""
        anchor = self.find_image('refresh_btn.png', conf=0.75, use_cache=False)
        
        if anchor:
            start_x = anchor.x + 700
            start_y = anchor.y - 50
            
            pyautogui.moveTo(start_x, start_y)
            pyautogui.dragTo(start_x, start_y - 400, duration=self.speed['swipe_drag'], button='left')
            time.sleep(self.speed['wait_after_swipe'])
            
            self._cached_screen = None # 🌟 滑动后画面改变，清空缓存
            return True
        else:
            return False
        
    def get_screen_size(self):
        """获取屏幕分辨率"""
        return pyautogui.size()
