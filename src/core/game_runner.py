#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : game_runner.py
@Author  : Guaig
@Date    : 2026-06-25
@Desc    : 游戏任务调度引擎，负责设备初始化与后台线程管理
"""

import threading
import pyautogui
from pathlib import Path
from src.core.logger import log_manager
from src.core.config import SPEED_PROFILES

class GameRunner:
    def __init__(self, log_cb, shop_stats_cb, general_stats_cb, finish_cb):
        """
        :param log_cb: 打印日志的回调函数
        :param shop_stats_cb: 更新商店战绩的回调函数
        :param general_stats_cb: 更新通用战绩的回调函数
        :param finish_cb: 任务结束时恢复UI按钮状态的回调函数
        """
        self.log_cb = log_cb
        self.shop_stats_cb = shop_stats_cb
        self.general_stats_cb = general_stats_cb
        self.finish_cb = finish_cb
        
        self.is_running = False
        self.current_task = None
        self.base_dir = Path(__file__).resolve().parents[2]

    def start(self, is_adb_mode, speed_gear, adb_serial, selected_task):
        if self.is_running: return
        self.is_running = True
        
        # 启动后台守护线程，防止阻塞 UI
        threading.Thread(
            target=self._run_thread, 
            args=(is_adb_mode, speed_gear, adb_serial, selected_task), 
            daemon=True
        ).start()

    def stop(self):
        self.is_running = False
        if self.current_task:
            self.current_task.stop()

    def _run_thread(self, is_adb_mode, speed_gear, adb_serial, selected_task):
        try:
            current_speed = SPEED_PROFILES[speed_gear].copy()
            self.log_cb(f"已加载挡位: {speed_gear}")
            log_manager.info(f"任务启动，挡位: {speed_gear}")
            
            # ================= 1. 设备初始化 =================
            if not is_adb_mode:  
                image_dir = str(self.base_dir / 'data' / 'images_win')
                from src.core.win_controller import WinController
                device = WinController(current_speed, image_dir)
            else:
                # ADB 速度微调
                for key, value in current_speed.items():
                    if isinstance(value, (int, float)):
                        if key in ['wait_after_swipe', 'wait_refresh_done']:
                            current_speed[key] = value - 0.6
                        else:
                            current_speed[key] = max(0.1, value - 0.2)
                
                image_dir = str(self.base_dir / 'data' / 'images_adb')  
                from src.core.adb_controller import AdbController
                device = AdbController(serial=adb_serial, speed_profile=current_speed, image_dir=image_dir)
            
            # ================= 2. 任务调度分支 =================
            if selected_task == "商店自动刷新":
                from src.tasks.shop_task import ShopTask
                self.current_task = ShopTask(
                    device=device, 
                    speed_config=current_speed, 
                    log_callback=self.log_cb,
                    stats_callback=self.shop_stats_cb
                )
                self.current_task.run()
                
                # 结算日志
                stats = getattr(self.current_task, 'stats', {})
                summary = (
                    "\n📊 === 最终战绩结算 ===\n"
                    f"🔄 刷新商店: {stats.get('refresh', 0)} 次\n"
                    f"🔖 誓约书签 (蓝): {stats.get('blue', 0)} 次\n"
                    f"🏅 神秘奖牌 (红): {stats.get('red', 0)} 次\n"
                    "======================\n"
                )
                self.log_cb(summary)
                
            elif selected_task == "自动NPC竞技场":
                # 预留给 NpcArenaTask
                msg = "🚧 自动NPC竞技场任务正在开发中，敬请期待！"
                self.log_cb(msg)
                log_manager.info(msg)
                
            self.log_cb("✅ 任务执行完毕或已手动停止。")
            
        except pyautogui.FailSafeException:
            msg = "🛑 已触发鼠标防爆死机制，任务已紧急停止！"
            log_manager.warning(msg)
            self.log_cb(msg)
        except Exception as e:
            error_msg = f"❌ 发生异常: {repr(e)}"
            log_manager.error(error_msg, exc_info=True)
            self.log_cb(error_msg)
        finally:
            self.is_running = False
            self.current_task = None
            # 通知 UI 恢复按钮状态
            self.finish_cb()
