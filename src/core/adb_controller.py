#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : adb_controller.py
@Author  : Guaig
@Date    : 2026-06-25
@Desc    : 基于 ADB 命令的设备控制器 (支持图片缓存)
"""

import sys
import time
import subprocess
from pathlib import Path
import cv2
import numpy as np
import random

from src.core.logger import log_manager

class Point:
    """模拟 PyAutoGUI 返回的坐标对象，确保 ShopTask 兼容"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

class AdbController:
    # ✅ 标识设备类型，供 ShopTask 安全判断
    is_adb = True

    def __init__(self, serial, speed_profile, image_dir):
        self.serial = serial
        self.speed = speed_profile
        self._cached_screen = None
        
        # 🌟 核心清理：彻底解耦！直接使用 Runner 传来的绝对路径，不再关心是否打包
        self.image_dir = Path(image_dir)
            
        # 2. 图片内存缓存字典
        self.image_cache = {}
        
        # 测试 ADB 连接
        self._check_connection()

    def clear_cache(self):
        """清理内存缓存，释放资源"""
        self.image_cache.clear()
        self._cached_screen = None
        log_manager.debug("🧹 已清空 ADB 图片及屏幕缓存")

    def _check_connection(self):
        """检查设备是否在线，如果不在线则尝试自动连接"""
        try:
            # 🌟 修复：增加 creationflags=subprocess.CREATE_NO_WINDOW 隐藏黑框
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if self.serial not in result.stdout or 'offline' in result.stdout:
                log_manager.warning(f"⚠️ 未检测到 {self.serial}，正在尝试自动连接...")
                conn_result = subprocess.run(['adb', 'connect', self.serial], capture_output=True, text=True, encoding='utf-8', errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                if "connected" in conn_result.stdout or "already connected" in conn_result.stdout:
                    log_manager.info(f"✅ 成功连接到模拟器: {self.serial}")
                else:
                    log_manager.error(f"❌ 自动连接失败，ADB返回: {conn_result.stdout.strip()}")
            else:
                log_manager.info(f"✅ 模拟器 {self.serial} 已连接就绪。")
        except Exception as e:
            log_manager.error(f"❌ ADB 环境异常，请确认是否已安装 ADB 并配置环境变量: {e}")

    def _run_adb(self, cmd_args, raw_output=False):
        """执行 ADB 命令的底层工具"""
        cmd = ['adb', '-s', self.serial] + cmd_args
        try:
            if raw_output:
                # 🌟 修复：增加 creationflags=subprocess.CREATE_NO_WINDOW 隐藏黑框
                result = subprocess.run(cmd, capture_output=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                # 🌟 修复：增加 creationflags=subprocess.CREATE_NO_WINDOW 隐藏黑框
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return result.stdout
        except subprocess.CalledProcessError as e:
            log_manager.error(f"❌ ADB 命令执行失败: {' '.join(cmd)}")
            return b"" if raw_output else ""
        except Exception as e:
            log_manager.error(f"❌ ADB 发生未知异常: {e}")
            return b"" if raw_output else ""

    def _get_template(self, img_name):
        """从缓存获取模板图，安全读取防崩溃"""
        if img_name not in self.image_cache:
            img_path = str(self.image_dir / img_name)
            if not Path(img_path).exists():
                log_manager.error(f"❌ 警告：图片文件不存在！路径为: {img_path}")
                return None
            template = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                log_manager.error(f"❌ 无法读取图片，可能文件损坏: {img_path}")
                return None
            self.image_cache[img_name] = template
        return self.image_cache.get(img_name)

    def get_screen_size(self):
        """获取设备屏幕分辨率 (宽, 高)"""
        output = self._run_adb(['shell', 'wm', 'size'])
        try:
            size_str = output.strip().split(': ')[-1]
            w, h = map(int, size_str.split('x'))
            return max(w, h), min(w, h)
        except Exception:
            return 2560, 1080 

    def click(self, x, y):
        """执行点击 (增加防检测随机偏移)"""
        offset_x = random.randint(-8, 8)
        offset_y = random.randint(-8, 8)
        screen_w, screen_h = self.get_screen_size()
        final_x = max(0, min(int(x) + offset_x, screen_w - 1))
        final_y = max(0, min(int(y) + offset_y, screen_h - 1))
        
        self._run_adb(['shell', 'input', 'tap', str(final_x), str(final_y)])
        base_sleep = self.speed.get('click_move', 0.5)
        time.sleep(base_sleep + random.uniform(0.05, 0.15))

    def swipe_up(self):
        """执行上滑操作 (锚点定位 + 防检测随机)"""
        anchor = self.find_image('refresh_btn.png', conf=0.75)
        if anchor:
            start_x = anchor.x + 700 + random.randint(-10, 10)
            start_y = anchor.y - 50 + random.randint(-10, 10)
            end_x = start_x + random.randint(-5, 5)
            end_y = start_y - random.randint(380, 420)
            
            base_duration = int(self.speed['swipe_drag'] * 1000)
            duration = max(250, base_duration + random.randint(-50, 150))

            self._run_adb(['shell', 'input', 'swipe', 
                           str(int(start_x)), str(int(start_y)), 
                           str(int(end_x)), str(int(end_y)), 
                           str(duration)])
            
            time.sleep(self.speed['wait_after_swipe'])
            self._cached_screen = None 
            return True
        return False

    def find_image(self, img_name, conf=0.8, region=None, use_cache=False):
        """核心方法：截屏并使用 OpenCV 进行模板匹配"""
        if not use_cache or self._cached_screen is None:
            screen_bytes = self._run_adb(['exec-out', 'screencap'], raw_output=True)
            if not screen_bytes or len(screen_bytes) < 12: 
                return None
            
            width = int.from_bytes(screen_bytes[0:4], byteorder='little')
            height = int.from_bytes(screen_bytes[4:8], byteorder='little')
            expected_size = width * height * 4
            offset = len(screen_bytes) - expected_size
            
            if offset < 0:
                return None
                
            raw_pixels = screen_bytes[offset:]
            img_np = np.frombuffer(raw_pixels, dtype=np.uint8)
            img_rgba = img_np.reshape((height, width, 4))
            self._cached_screen = cv2.cvtColor(img_rgba, cv2.COLOR_RGBA2GRAY)

        screen_img = self._cached_screen.copy()

        offset_x, offset_y = 0, 0
        if region:
            x, y, w, h = [int(v) for v in region]
            screen_img = screen_img[y:y+h, x:x+w]
            offset_x, offset_y = x, y

        template = self._get_template(img_name)
        if template is None:
            return None 

        th, tw = template.shape[:2]
        sh, sw = screen_img.shape[:2] 

        if sh < th or sw < tw:
            return None

        result = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= conf:
            center_x = max_loc[0] + tw // 2 + offset_x
            center_y = max_loc[1] + th // 2 + offset_y
            return Point(center_x, center_y)
            
        return None
