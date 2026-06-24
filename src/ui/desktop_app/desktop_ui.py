#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : desktop_ui.py
@Author  : Guaig
@Date    : 2026-06-24
@Desc    : Windows & ADB 双模式桌面应用界面 (CustomTkinter)
"""

import threading
import customtkinter as ctk
import pyautogui
from pathlib import Path

# 设置主题和样式
ctk.set_appearance_mode("dark")      # 暗黑模式
ctk.set_default_color_theme("blue")  # 蓝色主题

class E7DesktopApp(ctk.CTk):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # ==================== 窗口初始化 ====================
        self.title("🚀 E7 全自动挂机助手 - v2.0 (ADB支持版)")
        self.geometry("600x580")  # 稍微加高了一点点，以容纳新选项
        self.resizable(False, False)
        
        # 窗口居中显示
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 300
        y = (self.winfo_screenheight() // 2) - 290
        self.geometry(f"+{x}+{y}")
        
        # ==================== 状态变量 ====================
        self.is_running = False
        self.task_thread = None
        self.current_task = None  
        
        # ==================== 创建组件 ====================
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面上的所有可视化组件"""
        
        # --- 1. 顶部标题区 ---
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(pady=10, padx=20, fill="x")
        
        self.title_label = ctk.CTkLabel(title_frame, text="E7 秘密商店挂机助手", 
                                        font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack()
        
        # --- 2. 配置信息区 ---
        config_frame = ctk.CTkFrame(self, fg_color="#2B2B2B")
        config_frame.pack(pady=10, padx=20, fill="x")
        
        # 🟢 创建一个统一的网格容器，采用三列布局：图标 | 文字 | 控件
        settings_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        settings_frame.pack(pady=15)
        
        # --- 第一行：运行模式 ---
        self.mode_icon = ctk.CTkLabel(settings_frame, text="💻", font=ctk.CTkFont(size=14))
        self.mode_icon.grid(row=0, column=0, padx=(15, 5), pady=8, sticky="e") # 图标靠右
        
        self.mode_label = ctk.CTkLabel(settings_frame, text="运行模式:", font=ctk.CTkFont(size=14))
        self.mode_label.grid(row=0, column=1, padx=(0, 15), pady=8, sticky="w") # 文字靠左
        
        self.mode_var = ctk.StringVar(value="ADB 模拟器模式")
        self.mode_menu = ctk.CTkOptionMenu(settings_frame, values=["ADB 模拟器模式", "Windows 桌面模式"], 
                                           variable=self.mode_var, width=160, command=self._on_mode_change)
        self.mode_menu.grid(row=0, column=2, padx=(0, 10), pady=8, sticky="w")

        # --- 第二行：ADB 地址 ---
        self.adb_icon = ctk.CTkLabel(settings_frame, text="🔌", font=ctk.CTkFont(size=14))
        self.adb_icon.grid(row=1, column=0, padx=(15, 5), pady=8, sticky="e")
        
        self.adb_label = ctk.CTkLabel(settings_frame, text="ADB 地址:", font=ctk.CTkFont(size=14))
        self.adb_label.grid(row=1, column=1, padx=(0, 15), pady=8, sticky="w")
        
        self.adb_entry = ctk.CTkEntry(settings_frame, width=160)
        self.adb_entry.insert(0, "127.0.0.1:7555")  # 默认沐沐模拟器端口
        self.adb_entry.grid(row=1, column=2, padx=(0, 10), pady=8, sticky="w")
        
        # --- 第三行：速度挡位 ---
        self.gear_icon = ctk.CTkLabel(settings_frame, text="⚙️", font=ctk.CTkFont(size=14))
        self.gear_icon.grid(row=2, column=0, padx=(15, 5), pady=8, sticky="e")
        
        self.gear_label = ctk.CTkLabel(settings_frame, text="速度挡位:", font=ctk.CTkFont(size=14))
        self.gear_label.grid(row=2, column=1, padx=(0, 15), pady=8, sticky="w")
        
        self.gear_var = ctk.StringVar(value="FAST")
        self.gear_menu = ctk.CTkOptionMenu(settings_frame, values=["SLOW", "NORMAL", "FAST"], 
                                           variable=self.gear_var, width=160)
        self.gear_menu.grid(row=2, column=2, padx=(0, 10), pady=8, sticky="w")
        
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
        
        self.log_text = ctk.CTkTextbox(log_frame, width=540, height=160, font=ctk.CTkFont(size=12))
        self.log_text.pack(padx=10, pady=10)
        self.log_text.insert("0.0", "=== 系统就绪 ===\n选择运行模式和挡位后，点击开始...\n\n")
        self.log_text.configure(state="disabled")
        
        # --- 5. 底部版权信息 ---
        ctk.CTkLabel(self, text="© 2026 E7 Auto Script | Powered by CustomTkinter", 
                     font=ctk.CTkFont(size=10), text_color="gray").pack(pady=5)

    def _on_mode_change(self, choice):
        """当运行模式改变时，动态显示或隐藏 ADB 地址输入框"""
        if choice == "Windows 桌面模式":
            self.adb_icon.grid_remove()
            self.adb_label.grid_remove()
            self.adb_entry.grid_remove()
        else:
            self.adb_icon.grid()
            self.adb_label.grid()
            self.adb_entry.grid()

    
    def start_task(self):
        """点击开始按钮的响应逻辑"""
        if self.is_running: return
        
        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        run_mode = self.mode_var.get()
        if run_mode == "Windows 桌面模式":
            self._log(">>> [Windows模式] 正在启动，请将鼠标移至模拟器区域...")
        else:
            self._log(f">>> [ADB模式] 正在连接设备 {self.adb_entry.get()}...")
        
        speed_gear = self.gear_var.get()
        adb_serial = self.adb_entry.get()
        
        # 开启新线程运行核心逻辑
        self.task_thread = threading.Thread(target=self._run_game_task, args=(run_mode, speed_gear, adb_serial), daemon=True)
        self.task_thread.start()
    
    def stop_task(self):
        """点击停止按钮的响应逻辑"""
        if not self.is_running: return
        
        self.is_running = False
        self._log(">>> 收到停止指令！(正在等待当前操作完成...)")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        if self.current_task:
            self.current_task.stop()
    
    def _run_game_task(self, run_mode, speed_gear, adb_serial):
        """后台运行刷店逻辑"""
        try:
            from src.core.config import SPEED_PROFILES
            from src.tasks.shop_task import ShopTask
            
            current_speed = SPEED_PROFILES[speed_gear]
            BASE_DIR = Path(__file__).resolve().parents[3]
            IMAGE_DIR = str(BASE_DIR / 'data' / 'images_win')  # 假设暂时共用同一套图
            
            self.after(0, self._log, f"已加载挡位: {speed_gear}")
            
            # ✅ 根据用户选择的模式，实例化不同的控制器
            if run_mode == "Windows 桌面模式":
                from src.core.win_controller import WinController
                device = WinController(current_speed, IMAGE_DIR)
            else:
                from src.core.adb_controller import AdbController
                # 这里将 ADB 参数传进去
                device = AdbController(serial=adb_serial, speed_profile=current_speed, image_dir=IMAGE_DIR)
            
            self.current_task = ShopTask(
                device=device, 
                speed_config=current_speed, 
                log_callback=lambda msg: self.after(0, self._log, msg)
            )
            
            # 开始执行任务，线程会在这里阻塞直到任务结束
            self.current_task.run()
            
            # 🌟 任务结束，提取战绩并打印结算面板
            stats = getattr(self.current_task, 'stats', {})
            refreshes = stats.get('refresh', 0)
            blue_count = stats.get('blue', 0)
            red_count = stats.get('red', 0)
            
            summary = (
                "\n"
                "📊 === 最终战绩结算 ===\n"
                f"🔄 刷新商店: {refreshes} 次\n"
                f"🔖 誓约书签 (蓝): {blue_count} 次\n"
                f"🏅 神秘奖牌 (红): {red_count} 次\n"
                "======================\n"
            )
            self.after(0, self._log, summary)
            self.after(0, self._log, "✅ 任务执行完毕或已手动停止。")
            
        except pyautogui.FailSafeException:
            self.after(0, self._log, "🛑 已触发鼠标防爆死机制，任务已紧急停止！")
        except Exception as e:
            error_msg = f"❌ 发生异常: {repr(e)}"
            self.after(0, self._log, error_msg)
        finally:
            self.is_running = False
            self.current_task = None
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            self.after(0, lambda: self.stop_btn.configure(state="disabled"))
    
    def _log(self, message):
        """向 UI 文本框追加日志信息"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

if __name__ == "__main__":
    app = E7DesktopApp()
    app.mainloop()
