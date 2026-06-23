# 基础任务#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : base_task.py
@Author  : Guaig
@Date    : 2026-06-23
@Desc    : 任务基类，定义了所有业务任务（如刷商店、讨伐等）的标准接口模板
"""

class BaseTask:
    """
    所有具体任务（如 ShopTask, HuntTask）都必须继承此类。
    这样可以保证主程序在调用时，不管是什么任务，都可以统一调用 run() 方法。
    """
    def __init__(self, device, speed_config):
        self.device = device  # 传入的控制器（WinController 或 AdbController）
        self.speed = speed_config  # 传入的速度配置

    def run(self):
        """执行任务的主入口，子类必须重写此方法"""
        raise NotImplementedError("必须在子类中实现 run() 方法！")
