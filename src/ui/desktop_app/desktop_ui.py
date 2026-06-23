#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : desktop_ui.py
@Author  : Guaig
@Date    : 2026-06-23
@Desc    : Windows 桌面应用基础界面 (CustomTkinter)
"""

import os
import sys
import threading
import customtkinter as ctk
import pyautogui 

# 设置主题和样式
ctk.set_appearance_mode("dark")      # 暗黑模式
ctk.set_default_color_theme("blue")  # 蓝色主题

class E7DesktopApp(ctk.CTk):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # ==================== 窗口初始化 ====================
        self.title("🚀 E7 全自动挂机助手 - v1.0")
        self.geometry("600x520")
        self.resizable(False, False)
        
        # 窗口居中显示
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 300
        y = (self.winfo_screenheight() // 2) - 260
        self.geometry(f"+{x}+{y}")
        
        # ==================== 状态变量 ====================
        self.is_running = False
        self.task_thread = None
        self.current_task = None  # ✅ 新增：用来记录当前正在跑的任务，这样才能叫停它！
        
        # ==================== 创建组件 ====================
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面上的所有可视化组件"""
        
        # --- 1. 顶部标题区 ---
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(pady=15, padx=20, fill="x")
        
        self.title_label = ctk.CTkLabel(title_frame, text="E7 秘密商店挂机助手", 
                                        font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack()
        
        # --- 2. 配置信息区 ---
        config_frame = ctk.CTkFrame(self, fg_color="#2B2B2B")
        config_frame.pack(pady=10, padx=20, fill="x")
        
        # 挡位选择
        gear_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        gear_frame.pack(pady=10)
        
        ctk.CTkLabel(gear_frame, text="⚙️ 速度挡位:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=10)
        
        self.gear_var = ctk.StringVar(value="FAST")
        self.gear_menu = ctk.CTkOptionMenu(gear_frame, values=["SLOW", "NORMAL", "FAST"], 
                                           variable=self.gear_var, width=120)
        self.gear_menu.grid(row=0, column=1, padx=10)
        
        # --- 3. 操作按钮区 ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10, padx=20)
        
        self.start_btn = ctk.CTkButton(btn_frame, text="▶ 开始挂机", command=self.start_task, 
                                       width=140, height=40, fg_color="#2ecc71", hover_color="#27ae60",
                                       font=ctk.CTkFont(weight="bold"))
        self.start_btn.grid(row=0, column=0, padx=15)
        
        self.stop_btn = ctk.CTkButton(btn_frame, text="⏹ 停止挂机", command=self.stop_task, 
                                      width=140, height=40, fg_color="#e74c3c", hover_color="#c0392b", 
                                      state="disabled", font=ctk.CTkFont(weight="bold"))
        self.stop_btn.grid(row=0, column=1, padx=15)
        
        # --- 4. 战绩与日志显示区 ---
        log_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=10)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.log_text = ctk.CTkTextbox(log_frame, width=540, height=180, font=ctk.CTkFont(size=12))
        self.log_text.pack(padx=10, pady=10)
        self.log_text.insert("0.0", "=== 系统就绪 ===\n请确保模拟器画面无遮挡，选择挡位后点击开始...\n\n")
        self.log_text.configure(state="disabled")
        
        # --- 5. 底部版权信息 ---
        ctk.CTkLabel(self, text="© 2026 E7 Auto Script | Powered by CustomTkinter", 
                     font=ctk.CTkFont(size=10), text_color="gray").pack(pady=5)
    
    def start_task(self):
        """点击开始按钮的响应逻辑"""
        if self.is_running: return
        
        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self._log(">>> 正在启动任务，请将鼠标移至模拟器区域...")
        
        # 获取用户选择的挡位
        speed_gear = self.gear_var.get()
        
        # 开启新线程运行核心逻辑，防止 UI 卡死
        self.task_thread = threading.Thread(target=self._run_game_task, args=(speed_gear,), daemon=True)
        self.task_thread.start()
    
    def stop_task(self):
        """点击停止按钮的响应逻辑"""
        if not self.is_running: return
        
        self.is_running = False
        self._log(">>> 收到停止指令！(正在等待当前操作完成...)")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        # ✅ 新增：真正去按 ShopTask 的停止开关！
        if self.current_task:
            self.current_task.stop()
    
    def _run_game_task(self, speed_gear):
        """后台运行刷店逻辑"""
        try:
            # 动态导入核心模块，避免启动 UI 时卡顿
            from src.core.config import SPEED_PROFILES
            from src.core.win_controller import WinController
            from src.tasks.shop_task import ShopTask
            
            # 获取配置和路径
            current_speed = SPEED_PROFILES[speed_gear]
            
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            IMAGE_DIR = os.path.join(BASE_DIR, 'data', 'images_win')
            
            self.after(0, self._log, f"已加载挡位: {speed_gear}")
            
            # 初始化手脚和大脑
            device = WinController(current_speed, IMAGE_DIR)
            
            # ✅ 修改：把实例化出来的任务赋值给 self.current_task，而不是局部的 task 变量
            self.current_task = ShopTask(device, current_speed)
            
            # 执行任务
            self.current_task.run()
            
            self.after(0, self._log, "✅ 任务执行完毕或已手动停止。")
            
        except pyautogui.FailSafeException:
            self.after(0, self._log, "🛑 已触发鼠标防爆死机制，任务已紧急停止！")
        except Exception as e:
            error_msg = f"❌ 发生异常: {str(e)}"
            self.after(0, self._log, error_msg)
        finally:
            # 恢复按钮状态
            self.is_running = False
            self.current_task = None  # ✅ 新增：任务跑完了，把记录清空
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            self.after(0, lambda: self.stop_btn.configure(state="disabled"))
    
    def _log(self, message):
        """向 UI 文本框追加日志信息"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")  # 自动滚动到底部
        self.log_text.configure(state="disabled")

if __name__ == "__main__":
    app = E7DesktopApp()
    app.mainloop()
