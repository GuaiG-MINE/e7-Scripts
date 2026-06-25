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

# 🌐 引入我们在 config.py 中写好的多语言小助手
from src.core.config import get_text as _, set_lang, STRINGS
# 🌟 引入全局日志管理器
from src.core.logger import log_manager

# 设置主题和样式
ctk.set_appearance_mode("dark")      # 暗黑模式
ctk.set_default_color_theme("blue")  # 蓝色主题

class E7DesktopApp(ctk.CTk):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # ==================== 窗口初始化 ====================
        self.title(_("app_title"))  
        self.geometry("600x580")  
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
        
        self.title_label = ctk.CTkLabel(title_frame, text=_("ui_title"),  
                                        font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(side="left", padx=(120, 0)) 
        
        self.lang_var = ctk.StringVar(value="中文")
        self.lang_menu = ctk.CTkOptionMenu(title_frame, values=["中文", "English"], 
                                           variable=self.lang_var, width=80, height=28,
                                           command=self._on_lang_change)
        self.lang_menu.pack(side="right")
        
        # --- 2. 配置信息区 ---
        config_frame = ctk.CTkFrame(self, fg_color="#2B2B2B")
        config_frame.pack(pady=10, padx=20, fill="x")
        
        settings_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        settings_frame.pack(pady=15)
        
        # --- 第一行：运行模式 ---
        self.mode_icon = ctk.CTkLabel(settings_frame, text="💻", font=ctk.CTkFont(size=14))
        self.mode_icon.grid(row=0, column=0, padx=(15, 5), pady=8, sticky="e") 
        
        self.mode_label = ctk.CTkLabel(settings_frame, text=_("run_mode"), font=ctk.CTkFont(size=14))  
        self.mode_label.grid(row=0, column=1, padx=(0, 15), pady=8, sticky="w") 
        
        self.mode_var = ctk.StringVar(value=_("mode_adb"))  
        self.mode_menu = ctk.CTkOptionMenu(settings_frame, values=[_("mode_adb"), _("mode_win")],  
                                           variable=self.mode_var, width=160, command=self._on_mode_change)
        self.mode_menu.grid(row=0, column=2, padx=(0, 10), pady=8, sticky="w")

        # --- 第二行：ADB 地址 ---
        self.adb_icon = ctk.CTkLabel(settings_frame, text="🔌", font=ctk.CTkFont(size=14))
        self.adb_icon.grid(row=1, column=0, padx=(15, 5), pady=8, sticky="e")
        
        self.adb_label = ctk.CTkLabel(settings_frame, text=_("adb_address"), font=ctk.CTkFont(size=14))  
        self.adb_label.grid(row=1, column=1, padx=(0, 15), pady=8, sticky="w")
        
        self.adb_entry = ctk.CTkEntry(settings_frame, width=160)
        self.adb_entry.insert(0, "127.0.0.1:16384")  
        self.adb_entry.grid(row=1, column=2, padx=(0, 10), pady=8, sticky="w")
        
        # --- 第三行：速度挡位 ---
        self.gear_icon = ctk.CTkLabel(settings_frame, text="⚙️", font=ctk.CTkFont(size=14))
        self.gear_icon.grid(row=2, column=0, padx=(15, 5), pady=8, sticky="e")
        
        self.gear_label = ctk.CTkLabel(settings_frame, text=_("speed_gear"), font=ctk.CTkFont(size=14))  
        self.gear_label.grid(row=2, column=1, padx=(0, 15), pady=8, sticky="w")
        
        self.gear_var = ctk.StringVar(value="FAST")
        self.gear_menu = ctk.CTkOptionMenu(settings_frame, values=["SLOW", "NORMAL", "FAST"], 
                                           variable=self.gear_var, width=160)
        self.gear_menu.grid(row=2, column=2, padx=(0, 10), pady=8, sticky="w")
        
        # --- 3. 操作按钮区 ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10, padx=20)
        
        self.start_btn = ctk.CTkButton(btn_frame, text=_("btn_start"), command=self.start_task,  
                                       width=140, height=40, fg_color="#2ecc71", hover_color="#27ae60",
                                       font=ctk.CTkFont(weight="bold"))
        self.start_btn.grid(row=0, column=0, padx=15)
        
        self.stop_btn = ctk.CTkButton(btn_frame, text=_("btn_stop"), command=self.stop_task,  
                                      width=140, height=40, fg_color="#e74c3c", hover_color="#c0392b", 
                                      state="disabled", font=ctk.CTkFont(weight="bold"))
        self.stop_btn.grid(row=0, column=1, padx=15)
        
        # --- 4. 战绩与日志显示区 ---
        log_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=10)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # 🌟 新增：战绩实时显示标签
        self.stats_var = ctk.StringVar(value="🏆 战绩: 书签 0 | 神秘 0 | 刷新 0")
        self.stats_label = ctk.CTkLabel(
            log_frame, 
            textvariable=self.stats_var, 
            font=ctk.CTkFont(family="微软雅黑", size=16, weight="bold"), 
            text_color="#FFD700"  # 亮金色
        )
        self.stats_label.pack(pady=(10, 0))
        
        # 日志框高度稍微调小一点，给上面的战绩让路
        self.log_text = ctk.CTkTextbox(log_frame, width=540, height=130, font=ctk.CTkFont(size=12))
        self.log_text.pack(padx=10, pady=10)
        self.log_text.insert("0.0", _("log_ready"))  
        self.log_text.configure(state="disabled")
        
        # --- 5. 底部版权信息 ---
        self.copyright_label = ctk.CTkLabel(self, text=_("copyright"),  
                                            font=ctk.CTkFont(size=10), text_color="gray")
        self.copyright_label.pack(pady=5)

    # 🌟 线程安全的战绩更新回调
    def update_stats_ui(self, blue, red, refresh):
        new_text = f"🏆 战绩: 书签 {blue} | 神秘 {red} | 刷新 {refresh}"
        self.after(0, lambda: self.stats_var.set(new_text))

    # ==================== 🌐 多语言核心逻辑 ====================
    def _on_lang_change(self, choice):
        lang_code = "en" if choice == "English" else "zh"
        set_lang(lang_code)  
        self._refresh_ui_texts() 

    def _refresh_ui_texts(self):
        self.title(_("app_title"))
        self.title_label.configure(text=_("ui_title"))
        self.mode_label.configure(text=_("run_mode"))
        self.adb_label.configure(text=_("adb_address"))
        self.gear_label.configure(text=_("speed_gear"))
        self.start_btn.configure(text=_("btn_start"))
        self.stop_btn.configure(text=_("btn_stop"))
        self.copyright_label.configure(text=_("copyright"))
        
        current_mode_is_win = (self.mode_var.get() == STRINGS["zh"]["mode_win"] or 
                               self.mode_var.get() == STRINGS["en"]["mode_win"])
        self.mode_menu.configure(values=[_("mode_adb"), _("mode_win")])
        self.mode_var.set(_("mode_win") if current_mode_is_win else _("mode_adb"))

    # ==================== 业务逻辑 ====================
    def _on_mode_change(self, choice):
        if choice == _("mode_win"):  
            self.adb_icon.grid_remove()
            self.adb_label.grid_remove()
            self.adb_entry.grid_remove()
        else:
            self.adb_icon.grid()
            self.adb_label.grid()
            self.adb_entry.grid()

    def start_task(self):
        if self.is_running: return
        
        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        # 🌟 每次点击开始，重置 UI 上的战绩显示
        self.update_stats_ui(0, 0, 0)
        
        run_mode = self.mode_var.get()
        if run_mode == _("mode_win"):  
            msg = ">>> [Windows模式] 正在启动，请将鼠标移至模拟器区域..."
            log_manager.info(msg)
            self._log(msg)
        else:
            msg = f">>> [ADB模式] 正在连接设备 {self.adb_entry.get()}..."
            log_manager.info(msg)
            self._log(msg)
        
        speed_gear = self.gear_var.get()
        adb_serial = self.adb_entry.get()
        
        self.task_thread = threading.Thread(target=self._run_game_task, args=(run_mode, speed_gear, adb_serial), daemon=True)
        self.task_thread.start()
    
    def stop_task(self):
        if not self.is_running: return
        self.is_running = False
        
        msg = ">>> 收到停止指令！(正在等待当前操作完成...)"
        log_manager.info(msg)
        self._log(msg)
        
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        if self.current_task:
            self.current_task.stop()
    
    def _run_game_task(self, run_mode, speed_gear, adb_serial):
        try:
            from src.core.config import SPEED_PROFILES
            from src.tasks.shop_task import ShopTask
            
            current_speed = SPEED_PROFILES[speed_gear].copy()
            BASE_DIR = Path(__file__).resolve().parents[3]
            
            self.after(0, self._log, f"已加载挡位: {speed_gear}")
            log_manager.info(f"任务启动，已加载速度挡位: {speed_gear}")
            
            if run_mode == _("mode_win"):  
                IMAGE_DIR = str(BASE_DIR / 'data' / 'images_win')
                from src.core.win_controller import WinController
                device = WinController(current_speed, IMAGE_DIR)
            else:
                for key, value in current_speed.items():
                    if isinstance(value, (int, float)):
                        if key in ['wait_after_swipe', 'wait_refresh_done']:
                            current_speed[key] = value - 0.6
                        else:
                            current_speed[key] = max(0.1, value - 0.2)
                            
                msg = "⚡ 已应用 ADB 专属速度微调（保护动画完整性）！"
                self.after(0, self._log, msg)
                log_manager.info(msg)

                IMAGE_DIR = str(BASE_DIR / 'data' / 'images_adb')  
                from src.core.adb_controller import AdbController
                device = AdbController(serial=adb_serial, speed_profile=current_speed, image_dir=IMAGE_DIR)
            
            # 🌟 传入 log_callback 和 stats_callback
            self.current_task = ShopTask(
                device=device, 
                speed_config=current_speed, 
                log_callback=lambda msg: self.after(0, self._log, msg),
                stats_callback=self.update_stats_ui  # 👈 这里传给 Task
            )
            
            self.current_task.run()
            
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
            log_manager.info(f"任务结束结算: 刷新 {refreshes} 次, 蓝 {blue_count} 次, 红 {red_count} 次")
            self.after(0, self._log, summary)
            self.after(0, self._log, "✅ 任务执行完毕或已手动停止。")
            
        except pyautogui.FailSafeException:
            msg = "🛑 已触发鼠标防爆死机制，任务已紧急停止！"
            log_manager.warning(msg)
            self.after(0, self._log, msg)
        except Exception as e:
            error_msg = f"❌ 发生异常: {repr(e)}"
            # 🌟 关键：exc_info=True 会把具体的报错行号和堆栈追踪写进文件里！
            log_manager.error(error_msg, exc_info=True)
            self.after(0, self._log, error_msg)
        finally:
            self.is_running = False
            self.current_task = None
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            self.after(0, lambda: self.stop_btn.configure(state="disabled"))
    
    def _log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

if __name__ == "__main__":
    app = E7DesktopApp()
    app.mainloop()
