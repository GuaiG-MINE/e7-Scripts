#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : main.py
@Author  : Guaig
@Date    : 2026-06-23
@Desc    : 脚本总入口，负责加载配置、初始化设备控制器并启动对应任务 (未来的App主页雏形)
"""

import os
from src.core.config import SPEED_PROFILES, CURRENT_GEAR
from src.core.win_controller import WinController
from src.tasks.shop_task import ShopTask

def main():
    print("=============================")
    print("🚀 欢迎使用 E7 全自动挂机助手")
    print("=============================")
    print("1. 自动刷秘密商店")
    print("2. 自动讨伐 (敬请期待)")
    
    choice = input("👉 请输入要执行的功能序号 (直接回车默认选1): ")
    
    if choice == '' or choice == '1':
        print(f"\n>>> 初始化配置中... 当前挡位：【{CURRENT_GEAR}】")
        
        # 1. 确定工作目录和配置
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        IMAGE_DIR = os.path.join(BASE_DIR, 'data', 'images_win')
        SPEED_CONFIG = SPEED_PROFILES[CURRENT_GEAR]
        
        # 2. 实例化手脚 (装配 Windows 鼠标键盘控制器)
        device = WinController(SPEED_CONFIG, IMAGE_DIR)
        
        # 3. 实例化大脑 (装载 刷商店 逻辑，并把控制器交接给它)
        task = ShopTask(device, SPEED_CONFIG)
        
        # 4. 开始干活！
        task.run()
    else:
        print("敬请期待！")

if __name__ == "__main__":
    main()
