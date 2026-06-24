#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : config.py
@Author  : Guaig
@Date    : 2026-06-23
@Desc    : 全局配置中心，包含脚本速度挡位、系统常量等配置
"""

# ==========================================
# ⚙️ 全局速度挡位配置面板 (基于视频逐帧校准版, 单位: 秒)
# ==========================================
SPEED_PROFILES = {
    'SLOW': {
        # 🐢 稳如老狗：适合电脑卡顿、网络延迟高，宁愿慢绝不漏
        'global_pause': 0.1,      'click_move': 0.2,
        'wait_popup': 0.8,        'wait_buy_done': 1.0,
        'wait_cancel': 0.6,       'swipe_drag': 0.4,
        'wait_after_swipe': 1.5,  # 增加滑动惯性缓冲
        'wait_refresh_pop': 1.0,  # 弹窗弹出充分等待
        'wait_refresh_done': 1.3, # 刷新后商品滑出动画
        'loop_interval': 0.5
    },
    'NORMAL': {
        # 🚗 默认均衡：日常挂机首选，速度与稳定的完美平衡
        'global_pause': 0.05,     'click_move': 0.1,
        'wait_popup': 0.6,        'wait_buy_done': 0.8,
        'wait_cancel': 0.5,       'swipe_drag': 0.3,
        'wait_after_swipe': 1.0,  # 适中的滑动惯性缓冲
        'wait_refresh_pop': 0.8,  # 贴合视频弹窗耗时
        'wait_refresh_done': 1.0, # 刷新后商品滑出动画
        'loop_interval': 0.5
    },
    'FAST': {
        # 🚀 极限狂飙：贴合游戏物理动画极限，一秒都不多等
        'global_pause': 0.02,     'click_move': 0.0,
        'wait_popup': 0.4,        'wait_buy_done': 0.4,
        'wait_cancel': 0.3,       'swipe_drag': 0.2,
        'wait_after_swipe': 0.8,  # 极限抗击滑动惯性
        'wait_refresh_pop': 0.5,  # 极限贴合弹窗弹出耗时
        'wait_refresh_done': 1.0, # 极限贴合商品滑出耗时
        'loop_interval': 0.2
    }
}

# 🎯 在这里切换挡位！只需修改引号里的名字：'SLOW', 'NORMAL', 或 'FAST'
CURRENT_GEAR = 'FAST'  


# ==========================================
# 🌐 国际化 (i18n) 多语言配置
# ==========================================
# 当前语言设置，可修改为 'en' 来切换英文
CURRENT_LANG = 'zh'

STRINGS = {
    "zh": {
        "app_title": "🚀 E7 全自动挂机助手 - v2.0 (ADB支持版)",
        "ui_title": "E7 秘密商店挂机助手",
        "run_mode": "运行模式:",
        "mode_adb": "ADB 模拟器模式",
        "mode_win": "Windows 桌面模式",
        "adb_address": "ADB 地址:",
        "speed_gear": "速度挡位:",
        "btn_start": "▶ 开始挂机",
        "btn_stop": "⏹ 停止挂机",
        "log_ready": "=== 系统就绪 ===\n选择运行模式和挡位后，点击开始...\n\n",
        "copyright": "© 2026 E7 Auto Script | Powered by CustomTkinter"
    },
    "en": {
        "app_title": "🚀 E7 Auto Bot - v2.0 (ADB Supported)",
        "ui_title": "E7 Secret Shop Auto Bot",
        "run_mode": "Run Mode:",
        "mode_adb": "ADB Emulator Mode",
        "mode_win": "Windows Desktop Mode",
        "adb_address": "ADB Address:",
        "speed_gear": "Speed Gear:",
        "btn_start": "▶ Start Bot",
        "btn_stop": "⏹ Stop Bot",
        "log_ready": "=== System Ready ===\nSelect mode and speed, then click Start...\n\n",
        "copyright": "© 2026 E7 Auto Script | Powered by CustomTkinter"
    }
}

def get_text(key):
    """获取对应语言的文本，如果找不到则返回 key 本身"""
    return STRINGS.get(CURRENT_LANG, STRINGS["zh"]).get(key, key)

# 在 config.py 最下方追加这个函数：
def set_lang(lang_code):
    """动态设置当前语言"""
    global CURRENT_LANG
    CURRENT_LANG = lang_code
