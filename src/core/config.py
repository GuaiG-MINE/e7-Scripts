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
        'wait_cancel': 0.3,       'swipe_drag': 0.15,
        'wait_after_swipe': 0.8,  # 极限抗击滑动惯性
        'wait_refresh_pop': 0.5,  # 极限贴合视频弹窗弹出耗时
        'wait_refresh_done': 1.0, # 极限贴合视频商品滑出耗时
        'loop_interval': 0.2
    }
}

# 🎯 在这里切换挡位！只需修改引号里的名字：'SLOW', 'NORMAL', 或 'FAST'
CURRENT_GEAR = 'FAST'  
