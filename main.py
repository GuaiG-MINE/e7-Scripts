#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : main.py
@Author  : Guaig
@Date    : 2026-06-23
@Desc    : 脚本总入口，支持 GUI (默认) 和 CLI 命令行双模式
"""

import sys
from pathlib import Path

# 确保项目根目录在 Python 模块搜索路径中
# __file__ 是 main.py，.parent 直接就是项目根目录 (e7)
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))  # sys.path 需要字符串格式

def run_cli_mode():
    """原本的纯文本命令行模式"""
    from src.core.config import SPEED_PROFILES, CURRENT_GEAR
    from src.core.win_controller import WinController
    from src.tasks.shop_task import ShopTask

    print("=============================")
    print("🚀 欢迎使用 E7 全自动挂机助手 (CLI模式)")
    print("=============================")
    print("1. 自动刷秘密商店")
    print("2. 自动讨伐 (敬请期待)")
    
    choice = input("👉 请输入要执行的功能序号 (直接回车默认选1): ")
    
    if choice == '' or choice == '1':
        print(f"\n>>> 初始化配置中... 当前挡位：【{CURRENT_GEAR}】")
        
        # 🌟 优雅的路径拼接
        IMAGE_DIR = str(BASE_DIR / 'data' / 'images_win')
        SPEED_CONFIG = SPEED_PROFILES[CURRENT_GEAR]
        
        # 实例化手脚和大脑
        device = WinController(SPEED_CONFIG, IMAGE_DIR)
        task = ShopTask(device, SPEED_CONFIG)
        
        # 开始干活！
        task.run()
    else:
        print("敬请期待！")

def run_gui_mode():
    """全新的图形化界面模式"""
    print("正在启动 E7 挂机助手图形界面...")
    try:
        from src.ui.desktop_app.desktop_ui import E7DesktopApp
        app = E7DesktopApp()
        app.mainloop()
    except ImportError as e:
        print(f"❌ 启动失败，缺少依赖库或路径错误: {e}")
        print("💡 请确认已激活虚拟环境，并执行: pip install -r requirements.txt")
        print("💡 临时回退到命令行模式，请运行: python main.py --cli")

def main():
    # 如果运行命令带了 --cli 参数，就走老逻辑
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        run_cli_mode()
    else:
        # 默认启动图形界面
        run_gui_mode()

if __name__ == "__main__":
    main()
