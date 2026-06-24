#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : adb_controller.py
@Author  : Guaig
@Date    : 2026-06-24
@Desc    : 基于 ADB 命令的设备控制器 (支持图片缓存与打包路径)
"""

import sys
import time
import subprocess
from pathlib import Path
import cv2
import numpy as np
import random

class Point:
    """模拟 PyAutoGUI 返回的坐标对象，确保 ShopTask 兼容"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

class AdbController:
    def __init__(self, serial, speed_profile, image_dir):
        self.serial = serial
        self.speed = speed_profile
        self._cached_screen = None
        
        # 1. 🌟 处理 PyInstaller 打包后的资源路径
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
            # 如果打包时放在了 data/images_adb 下，则拼接路径
            self.image_dir = base_path / 'data' / 'images_adb'
        else:
            self.image_dir = Path(image_dir)
            
        # 2. 🌟 图片内存缓存字典
        self.image_cache = {}
        
        # 测试 ADB 连接
        self._check_connection()

    def _check_connection(self):
        """检查设备是否在线"""
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)
            if self.serial not in result.stdout:
                print(f"⚠️ 警告: 未在 adb devices 列表中找到设备 {self.serial}，请确保模拟器已开启并连接。")
        except Exception as e:
            print(f"❌ ADB 环境异常: {e}")

    def _run_adb(self, cmd_args, raw_output=False):
        """执行 ADB 命令的底层工具"""
        cmd = ['adb', '-s', self.serial] + cmd_args
        # 如果需要原始字节输出（比如截图），则不使用 text=True
        result = subprocess.run(cmd, capture_output=True, text=not raw_output)
        return result.stdout

    def _get_template(self, img_name):
        """从缓存获取模板图，安全读取防崩溃"""
        if img_name not in self.image_cache:
            img_path = str(self.image_dir / img_name)
            # 1. 检查文件是否存在
            if not Path(img_path).exists():
                print(f"❌ 警告：图片文件不存在！路径为: {img_path}")
                return None
                
            template = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                print(f"❌ 无法读取图片，可能文件损坏: {img_path}")
                return None
                
            self.image_cache[img_name] = template
        return self.image_cache.get(img_name)
    def get_screen_size(self):
        """获取设备屏幕分辨率 (宽, 高)"""
        output = self._run_adb(['shell', 'wm', 'size'])
        # 输出格式通常为: "Physical size: 1080x2560" 或 "Override size: 1080x2560"
        try:
            size_str = output.strip().split(': ')[-1]
            w, h = map(int, size_str.split('x'))
            # 🌟 核心修复：第七史诗永远是横屏，所以真正的宽度必定是较大的那个数！
            return max(w, h), min(w, h)
        except Exception:
            return 2560, 1080 # 默认降级分辨率改为你的带鱼屏尺寸


    def click(self, x, y):
        """执行点击 (🌟 增加防检测随机偏移)"""
        # 模拟真人手指：在中心点周围 -8 到 +8 像素的范围内随机偏移
        offset_x = random.randint(-8, 8)
        offset_y = random.randint(-8, 8)
        
        final_x = int(x) + offset_x
        final_y = int(y) + offset_y
        
        self._run_adb(['shell', 'input', 'tap', str(final_x), str(final_y)])
        
        # 连点击后的等待时间也加上微小的随机波动 (0.05~0.15秒)
        base_sleep = self.speed.get('click_move', 0.5)
        time.sleep(base_sleep + random.uniform(0.05, 0.15))

    def swipe_up(self):
        """执行上滑操作 (🌟 对齐 Win 版本的锚点逻辑 + 防检测随机)"""
        anchor = self.find_image('refresh_btn.png', conf=0.75)
        
        if anchor:
            # 1. 宽屏修正：X轴往右偏移 700，Y轴起点往上偏移 50 (加点随机)
            start_x = anchor.x + 700 + random.randint(-10, 10)
            start_y = anchor.y - 50 + random.randint(-10, 10)
            
            # 2. 滑动幅度修正：向上滑动 600 像素左右 (加点随机)
            end_x = start_x + random.randint(-5, 5)
            end_y = start_y - random.randint(380, 420)
            
            # duration 决定滑动速度，稍微波动一下
            base_duration = int(self.speed['swipe_drag'] * 1000)
            duration = max(250, base_duration + random.randint(-50, 150))

            self._run_adb(['shell', 'input', 'swipe', 
                           str(int(start_x)), str(int(start_y)), 
                           str(int(end_x)), str(int(end_y)), 
                           str(duration)])
            
            time.sleep(self.speed['wait_after_swipe'])
            return True
        else:
            print("⚠️ 警告：找不到刷新按钮锚点，无法滑动！请确认在商店界面并且画面无遮挡。")
            return False

    def find_image(self, img_name, conf=0.8, region=None, use_cache=False):
        """
        核心方法：截屏并使用 OpenCV 进行模板匹配
        🌟 已启用终极优化：去除 PNG 压缩，直接读取原生 RGBA 像素流！
        """
        if not use_cache or self._cached_screen is None:
            # 1. 🌟 核心修改：去掉 '-p'，直接获取原生未压缩数据！
            screen_bytes = self._run_adb(['exec-out', 'screencap'], raw_output=True)
            if not screen_bytes: 
                return None
            
            # 2. 解析原生数据头 (前 12 或 16 个字节包含宽、高信息)
            width = int.from_bytes(screen_bytes[0:4], byteorder='little')
            height = int.from_bytes(screen_bytes[4:8], byteorder='little')
            
            # 3. 计算像素数据真正的起始位置 (规避不同模拟器头部长度的差异)
            # 每个像素由 RGBA 4个通道组成，所以总大小是 宽 * 高 * 4
            expected_size = width * height * 4
            offset = len(screen_bytes) - expected_size
            
            if offset < 0:
                print(f"❌ [ADB] 原生截图数据解析失败！数据长度异常。")
                return None
                
            # 4. 提取纯像素数据，并用 numpy 瞬间重组成图像矩阵
            raw_pixels = screen_bytes[offset:]
            img_np = np.frombuffer(raw_pixels, dtype=np.uint8)
            img_rgba = img_np.reshape((height, width, 4))
            
            # 5. 转换为灰度图供 OpenCV 匹配，存入缓存
            self._cached_screen = cv2.cvtColor(img_rgba, cv2.COLOR_RGBA2GRAY)

        # ====== 下面的代码保持不变 ======
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
            print(f"❌ [ADB 拦截] 划定的区域(高{sh})比模板图(高{th})还小！已拦截崩溃。")
            return None

        result = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= conf:
            center_x = max_loc[0] + tw // 2 + offset_x
            center_y = max_loc[1] + th // 2 + offset_y
            return Point(center_x, center_y)
            
        return None
