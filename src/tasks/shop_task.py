#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : shop_task.py
@Author  : Guaig
@Date    : 2026-06-24
@Desc    : 秘密商店自动刷新与购买逻辑实现 (脚本的"大脑")
"""

import time
from src.tasks.base_task import BaseTask
from src.core.logger import log_manager 

class ShopTask(BaseTask):
    def __init__(self, device, speed_config, log_callback=None, stats_callback=None):
        super().__init__(device, speed_config)        
        self.stats = {'blue': 0, 'red': 0, 'refresh': 0}
        self.log_callback = log_callback
        self.stats_callback = stats_callback 

    def log(self, message, level="info"):
        """统一日志输出出口"""
        if level == "debug": log_manager.debug(message)
        elif level == "warning": log_manager.warning(message)
        elif level == "error": log_manager.error(message)
        else: log_manager.info(message)
            
        if self.log_callback and level != "debug":
            self.log_callback(message)

    def _notify_stats_update(self):
        if self.stats_callback:
            self.stats_callback(self.stats['blue'], self.stats['red'], self.stats['refresh'])

    # 🌟 保留：动态等待工具，极速响应弹窗
    def wait_for_image(self, img_name, timeout=3.0, conf=0.8):
        """动态等待：不断截图寻找目标，找到了立刻返回，超时才放弃"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self._running: return None
            pos = self.device.find_image(img_name, conf=conf, use_cache=False)
            if pos: return pos
            time.sleep(0.1) 
        return None

    def find_and_buy(self, icon_img_name, use_cache=False):
        """【精准双重锁定版】左边认图标，右边认 1/1购买 -> 弹窗认全图"""
        if not self._running: return False
        
        icon_center = self.device.find_image(icon_img_name, conf=0.8, use_cache=use_cache)
        
        if icon_center:
            item_name = "誓约书签(蓝)" if "blue" in icon_img_name else "神秘奖牌(红)"
            self.log(f"🎯 发现目标 [{item_name}]！正在寻找购买按钮...", level="debug")
            
            is_adb = self.device.is_adb
            if is_adb:
                _, screen_h = self.device.get_screen_size()
                # 🌟 修复1：放宽顶部偏移，从 0.03 改为 0.05，防止切掉按钮上边缘
                offset_y = max(50, int(screen_h * 0.05))
                # 🌟 修复2：放宽整体高度，从 0.08 改为 0.14，给足上下冗余，但依然不会跨行
                safe_height_limit = max(130, int(screen_h * 0.14))
            else:
                offset_y = 40
                safe_height_limit = 120
                
            screen_w, screen_h = self.device.get_screen_size()
            top_y = max(0, int(icon_center.y - offset_y))
            left_x = int(icon_center.x)
            safe_width = screen_w - left_x
            safe_height = min(safe_height_limit, screen_h - top_y) 
            
            search_region = (left_x, top_y, safe_width, safe_height)

            # 🌟 修复3：将 conf 从 0.9 稍微降到 0.85，防止背景纹理干扰
            buy_center = self.device.find_image('buy_btn.png', conf=0.85, region=search_region, use_cache=True)
            
            if buy_center:
                self.device.click(buy_center.x, buy_center.y)
                
                confirm_img = 'confirm_buy_blue.png' if "blue" in icon_img_name else 'confirm_buy_red.png'
                confirm_center = self.wait_for_image(confirm_img, timeout=2.5)
                
                if confirm_center:
                    self.device.click(confirm_center.x, confirm_center.y)
                    self.log(f"✅ 成功进货 1 次 {item_name}！")
                    time.sleep(self.speed['wait_buy_done'])
                    return True
                else:
                    self.log(f"⚠️ 点了购买但没出弹窗，直接跳过防误触...", level="warning")
                    time.sleep(self.speed['wait_cancel'])
            else:
                self.log("⚠️ 找到图标了，但没找到右侧的 [1/1 购买] 按钮？", level="warning")
                
        return False

    def refresh_shop(self):
        """刷新商店并确认。返回 True 表示真的刷了一次新商品。"""
        if not self._running: return False
        
        refresh_center = self.device.find_image('refresh_btn.png', conf=0.85, use_cache=False)
        if not refresh_center:
            return False
            
        self.device.click(refresh_center.x, refresh_center.y)
        
        # 🌟 使用动态等待
        confirm_center = self.wait_for_image('confirm_refresh_btn.png', timeout=2.5, conf=0.85)
        if confirm_center:
            self.device.click(confirm_center.x, confirm_center.y)
            self.stats['refresh'] += 1
            self._notify_stats_update()
            time.sleep(self.speed['wait_refresh_done'])
            return True
        else:
            time.sleep(self.speed['wait_cancel'])
            return False

    def _check_shop_present(self):
        """真实截图检测是否还在商店页面（含加载中重试）"""
        for attempt in range(3):
            if self.device.find_image('refresh_btn.png', conf=0.75, use_cache=False):
                return True
            if attempt < 2:
                self.log(f"⏳ 未检测到商店界面，可能正在加载... (重试 {attempt+1}/2)", level="debug")
                time.sleep(1.5)
        return False

    def run(self):
        """任务主循环"""
        self.log("⏳ 请在 3 秒内确保画面停留在【秘密商店】...")
        
        # 🌟 保留：终极防爆死装甲
        try:
            for _ in range(3):
                if not self._running: return
                time.sleep(1)
                
            if not self._check_shop_present():
                self.log("⚠️ 警告：未检测到商店界面！请确认画面无遮挡且停留在秘密商店。", level="warning")
            else:
                self.log("✅ 成功识别到商店界面，开始执行任务！")
            
            loop_count = 1
            consecutive_swipe_fails = 0  
            max_refreshes = 2000 

            while self._running and self.stats['refresh'] < max_refreshes:
                self.log(f"\n--- 第 {loop_count} 次巡逻 ---", level="debug")
                
                blue_bought = False
                red_bought = False
                
                # ================= 上半区 =================
                blue_bought_top = False
                if self.find_and_buy('icon_blue.png', use_cache=False):
                    self.stats['blue'] += 1
                    blue_bought = True
                    blue_bought_top = True
                    self._notify_stats_update()  
                    
                use_cache_for_red_top = not blue_bought_top
                if self.find_and_buy('icon_red.png', use_cache=use_cache_for_red_top):
                    self.stats['red'] += 1
                    red_bought = True
                    self._notify_stats_update()  
                    
                if not self._running: break
                    
                if not (blue_bought and red_bought):
                    # ================= 滑动 =================
                    swipe_success = self.device.swipe_up()
                    if not self._running: break
                    
                    if not swipe_success:
                        consecutive_swipe_fails += 1
                        self.log(f"⚠️ 找不到刷新按钮锚点！(连续失败 {consecutive_swipe_fails}/8)", level="warning")
                        
                        if consecutive_swipe_fails >= 8:
                            if not self._check_shop_present():
                                self.log("❌ 商店界面丢失，停止任务。", level="error")
                                self._running = False
                                break
                            else:
                                self.log("ℹ️ 商店还在，可能是网络波动，重置计数继续。", level="warning")
                                consecutive_swipe_fails = 0
                        time.sleep(3)
                        continue
                    else:
                        consecutive_swipe_fails = 0  
                    
                    # ================= 下半区 =================
                    blue_bought_bottom = False
                    first_check_bottom = True 
                    
                    if not blue_bought:
                        if self.find_and_buy('icon_blue.png', use_cache=False):
                            self.stats['blue'] += 1
                            blue_bought = True
                            blue_bought_bottom = True
                            self._notify_stats_update()  
                        first_check_bottom = False
                        
                    if not red_bought:
                        use_cache_for_red_bottom = (not first_check_bottom) and (not blue_bought_bottom)
                        if self.find_and_buy('icon_red.png', use_cache=use_cache_for_red_bottom):
                            self.stats['red'] += 1
                            red_bought = True
                            self._notify_stats_update()  
                else:
                    self.log("🎉 天胡开局！上半区已全收，直接刷新！")
                    
                if blue_bought or red_bought:
                    self.log(f"🏆 战绩更新: 书签 {self.stats['blue']} | 神秘 {self.stats['red']} | 刷新 {self.stats['refresh']}")
                else:
                    self.log(f"🏆 当前战绩: 书签 {self.stats['blue']} | 神秘 {self.stats['red']} | 刷新 {self.stats['refresh']}", level="debug")
                
                if not self._running: break
                
                # 🌟 刷新
                if self.refresh_shop():
                    consecutive_swipe_fails = 0  
                else:
                    consecutive_swipe_fails += 1
                    self.log(f"⚠️ 刷新失败！(连续 {consecutive_swipe_fails}/8)", level="warning")
                    
                    if consecutive_swipe_fails >= 8:
                        if not self._check_shop_present():
                            self.log("❌ 商店界面丢失，停止任务。", level="error")
                            self._running = False
                            break
                        else:
                            self.log("ℹ️ 商店还在，可能是网络波动，重置计数继续。", level="warning")
                            consecutive_swipe_fails = 0
                
                loop_count += 1
                
                wait_time = self.speed['loop_interval']
                for _ in range(int(wait_time * 10)):
                    if not self._running: break
                    time.sleep(0.1)
                    
            if self.stats['refresh'] >= max_refreshes:
                self.log(f"🛑 达到最大安全刷新次数 ({max_refreshes})，任务自动停止防爆死。")
                
        except Exception as e:
            error_msg = f"❌ 任务发生致命崩溃: {str(e)}"
            self.log(error_msg, level="error")
            
        finally:
            self._running = False
            self.log("⏹ 任务已彻底停止。")
            if hasattr(self, 'finish_cb') and self.finish_cb:
                self.finish_cb()
