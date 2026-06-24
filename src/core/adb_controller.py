#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : adb_controller.py
@Author  : Guaig
@Date    : 2026-06-24
@Desc    : ADB 设备控制器，负责与安卓模拟器进行底层交互 (包含截图、找图、点击、滑动)
"""

import subprocess
import time
import random
import cv2
import numpy as np
import os       # 🌟 新增导入 os
import sys      # 🌟 新增导入 sys
from pathlib import Path

class AdbController:
    """ADB 控制器，接口与 WinController 类似，但底层实现完全不同，专门针对 ADB 设备交互设计"""

    def __init__(self, serial, speed_profile, image_dir):
        self.serial = serial
        self.speed = speed_profile
        
        # 🌟 核心修改：保持与 WinController 一致的 PyInstaller 路径拦截逻辑
        if hasattr(sys, '_MEIPASS'):
            # 如果是打包后的 exe 运行，强制指向系统临时解压目录
            self.image_dir = Path(sys._MEIPASS) / 'data' / 'images_adb'
        else:
            self.image_dir = Path(image_dir)
        
        # 性能优化：创建一个字典当“缓存池”，存已经读过的图片
        self.image_cache = {}
        
        # 测试连接
        self._check_connection()

    def _run_adb(self, cmd_args):
        """执行基础的 ADB 命令并返回输出"""
        base_cmd = ['adb', '-s', self.serial]
        # 如果是字符串，拆分成列表；如果是列表，直接拼接
        if isinstance(cmd_args, str):
            cmd_args = cmd_args.split()
        full_cmd = base_cmd + cmd_args
        
        try:
            # 隐藏命令行黑框 (Windows特有)
            startupinfo = None
            if hasattr(subprocess, 'STARTUPINFO'):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            result = subprocess.run(full_cmd, capture_output=True, startupinfo=startupinfo)
            return result.stdout
        except Exception as e:
            print(f"ADB 命令执行失败: {full_cmd}, 错误: {e}")
            return None

    def _check_connection(self):
        """检查设备是否在线"""
        # 尝试连接设备 (针对模拟器端口)
        subprocess.run(['adb', 'connect', self.serial], capture_output=True)
        # 检查设备列表
        output = subprocess.run(['adb', 'devices'], capture_output=True, text=True).stdout
        if self.serial not in output or 'offline' in output:
            raise ConnectionError(f"无法连接到 ADB 设备: {self.serial}，请检查模拟器是否启动及端口是否正确。")

    def get_screenshot(self):
        """
        获取设备当前屏幕截图
        :return: OpenCV 格式的图像对象 (numpy array)
        """
        # 使用 exec-out 直接将图片流输出到内存，速度比先保存到手机再 pull 快很多
        image_bytes = self._run_adb(['exec-out', 'screencap', '-p'])
        if not image_bytes:
            return None
        
        # 将字节流转换为 cv2 图像
        image_array = np.asarray(bytearray(image_bytes), dtype=np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        return img

    def click(self, x, y):
        """点击指定坐标"""
        self._run_adb(['shell', 'input', 'tap', str(x), str(y)])
        # 点击后的等待时间，从配置的挡位中读取
        time.sleep(self.speed.get('click_move', 0.1))

    def swipe(self, x1, y1, x2, y2, duration_ms=None):
        """滑动屏幕"""
        if duration_ms is None:
            # 根据挡位配置转换滑动时间（配置里是秒，ADB需要毫秒）
            duration_ms = int(self.speed.get('swipe_drag', 0.3) * 1000)
            
        self._run_adb(['shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration_ms)])
        # 滑动后的等待时间
        time.sleep(self.speed.get('wait_after_swipe', 1.0))

    def find_image(self, template_name, confidence=0.8):
        """
        在当前屏幕中寻找目标图片
        :param template_name: 图片文件名 (例如 'start_btn.png')
        :param confidence: 匹配置信度阈值
        :return: 匹配成功返回目标中心点坐标 (x, y)，失败返回 None
        """
        # 1. 获取当前屏幕截图
        screen_img = self.get_screenshot()
        if screen_img is None:
            return None

        # 🌟 2. 性能优化：优先从缓存拿图片，没有的话再去硬盘读
        if template_name not in self.image_cache:
            template_path = self.image_dir / template_name
            if not template_path.exists():
                print(f"⚠️ 找不到模板图片: {template_path}")
                return None

            # 读取模板图片
            img = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
            if img is None:
                print(f"⚠️ 无法读取图片文件: {template_path}")
                return None
            
            # 存入缓存，下次就不用读硬盘了！
            self.image_cache[template_name] = img

        # 直接使用缓存里的图片数据
        template_img = self.image_cache[template_name]

        # 3. 使用 OpenCV 进行模板匹配
        result = cv2.matchTemplate(screen_img, template_img, cv2.TM_CCOEFF_NORMED)
        
        # 解析匹配结果，max_val 是最高相似度，max_loc 是匹配到的左上角坐标
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 4. 判断最高相似度是否达到了我们要求的置信度
        if max_val >= confidence:
            # 获取模板图片的高度 (h) 和宽度 (w)
            h, w = template_img.shape[:2]
            
            # 计算中心点坐标
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            
            # 🌟 防封机制：添加一点随机偏移，模拟真人点击
            offset_x = random.randint(-w//4, w//4)
            offset_y = random.randint(-h//4, h//4)
            
            return (center_x + offset_x, center_y + offset_y)
        
        return None

    def stop(self):
        """停止控制器（预留清理接口）"""
        pass
