#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : desktop_ui.py
@Author  : Guaig
@Date    : 2026-06-25
@Desc    : Windows & ADB 双模式桌面应用界面 (彻底解耦版)
"""

import customtkinter as ctk
from src.core.config import get_text as _, set_lang, STRINGS
from src.core.logger import log_manager
from src.core.game_runner import GameRunner  # 🌟 引入刚写好的大脑

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class E7DesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(_("app_title"))  
        self.geometry("600x620")  
        self.resizable(False, False)
        
        # 居中显示
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 300
        y = (self.winfo_screenheight() // 2) - 310
        self.geometry(f"+{x}+{y}")
        
        # 🌟 实例化业务调度器，传入 UI 的更新方法
        self.runner = GameRunner(
            log_cb=lambda msg: self.after(0, self._log, msg),
            shop_stats_cb=self.update_shop_stats_ui,
            general_stats_cb=self.update_general_stats_ui,
            finish_cb=self._on_task_finish
        )
        
        self._build_ui()
    
    # ==================== UI 构建模块化 ====================
    def _build_ui(self):
        self._build_header()
        self._build_config_area()
        self._build_buttons()
        self._build_log_area()
        
    def _build_header(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(pady=10, padx=20, fill="x")
        
        self.title_label = ctk.CTkLabel(frame, text=_("ui_title"), font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(side="left", padx=(120, 0)) 
        
        self.lang_var = ctk.StringVar(value="中文")
        self.lang_menu = ctk.CTkOptionMenu(frame, values=["中文", "English"], variable=self.lang_var, width=80, command=self._on_lang_change)
        self.lang_menu.pack(side="right")
        
    def _build_config_area(self):
        frame = ctk.CTkFrame(self, fg_color="#2B2B2B")
        frame.pack(pady=10, padx=20, fill="x")
        grid = ctk.CTkFrame(frame, fg_color="transparent")
        grid.pack(pady=15)
        
        # 1. 选择任务
        ctk.CTkLabel(grid, text="🎮").grid(row=0, column=0, padx=5, pady=8) 
        self.task_label = ctk.CTkLabel(grid, text="选择任务")
        self.task_label.grid(row=0, column=1, padx=5, pady=8, sticky="w") 
        self.task_var = ctk.StringVar(value="商店自动刷新")  
        self.task_menu = ctk.CTkOptionMenu(grid, values=["商店自动刷新", "自动NPC竞技场"], variable=self.task_var, width=160, command=self._on_task_change)
        self.task_menu.grid(row=0, column=2, padx=5, pady=8)

        # 2. 运行模式
        ctk.CTkLabel(grid, text="💻").grid(row=1, column=0, padx=5, pady=8) 
        self.mode_label = ctk.CTkLabel(grid, text=_("run_mode"))
        self.mode_label.grid(row=1, column=1, padx=5, pady=8, sticky="w") 
        self.mode_var = ctk.StringVar(value=_("mode_adb"))  
        self.mode_menu = ctk.CTkOptionMenu(grid, values=[_("mode_adb"), _("mode_win")], variable=self.mode_var, width=160, command=self._on_mode_change)
        self.mode_menu.grid(row=1, column=2, padx=5, pady=8)

        # 3. ADB 地址
        self.adb_icon = ctk.CTkLabel(grid, text="🔌")
        self.adb_icon.grid(row=2, column=0, padx=5, pady=8)
        self.adb_label = ctk.CTkLabel(grid, text=_("adb_address"))
        self.adb_label.grid(row=2, column=1, padx=5, pady=8, sticky="w")
        self.adb_entry = ctk.CTkEntry(grid, width=160)
        self.adb_entry.insert(0, "127.0.0.1:16384")  
        self.adb_entry.grid(row=2, column=2, padx=5, pady=8)
        
        # 4. 速度挡位
        ctk.CTkLabel(grid, text="⚙️").grid(row=3, column=0, padx=5, pady=8)
        self.gear_label = ctk.CTkLabel(grid, text=_("speed_gear"))
        self.gear_label.grid(row=3, column=1, padx=5, pady=8, sticky="w")
        self.gear_var = ctk.StringVar(value="FAST")
        ctk.CTkOptionMenu(grid, values=["SLOW", "NORMAL", "FAST"], variable=self.gear_var, width=160).grid(row=3, column=2, padx=5, pady=8)

    def _build_buttons(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(pady=10, padx=20)
        self.start_btn = ctk.CTkButton(frame, text=_("btn_start"), command=self.start_task, width=140, height=40, fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(weight="bold"))
        self.start_btn.grid(row=0, column=0, padx=15)
        self.stop_btn = ctk.CTkButton(frame, text=_("btn_stop"), command=self.stop_task, width=140, height=40, fg_color="#e74c3c", hover_color="#c0392b", state="disabled", font=ctk.CTkFont(weight="bold"))
        self.stop_btn.grid(row=0, column=1, padx=15)
        
    def _build_log_area(self):
        frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=10)
        frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.stats_var = ctk.StringVar(value="🏆 战绩: 准备就绪")
        ctk.CTkLabel(frame, textvariable=self.stats_var, font=ctk.CTkFont(size=16, weight="bold"), text_color="#FFD700").pack(pady=(10, 0))
        self.log_text = ctk.CTkTextbox(frame, width=540, height=130, font=ctk.CTkFont(size=12))
        self.log_text.pack(padx=10, pady=10)
        self.log_text.insert("0.0", _("log_ready"))  
        self.log_text.configure(state="disabled")
        
        self.copyright_label = ctk.CTkLabel(self, text=_("copyright"), font=ctk.CTkFont(size=10), text_color="gray")
        self.copyright_label.pack(pady=5)

    # ==================== UI 状态更新与回调 ====================
    def update_shop_stats_ui(self, blue, red, refresh):
        self.after(0, lambda: self.stats_var.set(f"🏆 战绩: 书签 {blue} | 神秘 {red} | 刷新 {refresh}"))
        
    def update_general_stats_ui(self, text):
        self.after(0, lambda: self.stats_var.set(f"🏆 战绩: {text}"))

    def _log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        
    def _on_task_finish(self):
        """任务结束，恢复按钮"""
        self.after(0, lambda: self.start_btn.configure(state="normal"))
        self.after(0, lambda: self.stop_btn.configure(state="disabled"))

    # ==================== 交互事件 ====================
    def _on_lang_change(self, choice):
        set_lang("en" if choice == "English" else "zh")  
        self.title(_("app_title"))
        self.title_label.configure(text=_("ui_title"))
        self.mode_label.configure(text=_("run_mode"))
        self.adb_label.configure(text=_("adb_address"))
        self.gear_label.configure(text=_("speed_gear"))
        self.start_btn.configure(text=_("btn_start"))
        self.stop_btn.configure(text=_("btn_stop"))
        self.copyright_label.configure(text=_("copyright"))
        is_win = (self.mode_var.get() in [STRINGS["zh"]["mode_win"], STRINGS["en"]["mode_win"]])
        self.mode_menu.configure(values=[_("mode_adb"), _("mode_win")])
        self.mode_var.set(_("mode_win") if is_win else _("mode_adb"))

    def _on_mode_change(self, choice):
        if choice == _("mode_win"):  
            self.adb_icon.grid_remove(); self.adb_label.grid_remove(); self.adb_entry.grid_remove()
        else:
            self.adb_icon.grid(); self.adb_label.grid(); self.adb_entry.grid()
            
    def _on_task_change(self, choice):
        if choice == "商店自动刷新": self.update_shop_stats_ui(0, 0, 0)
        else: self.update_general_stats_ui("竞技场准备就绪")

    def start_task(self):
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        task = self.task_var.get()
        self._on_task_change(task) # 重置战绩
        
        is_adb = (self.mode_var.get() != _("mode_win"))
        msg = f">>> 准备执行【{task}】..."
        log_manager.info(msg); self._log(msg)
        
        # 🌟 核心：直接把参数丢给调度器去跑！
        self.runner.start(
            is_adb_mode=is_adb,
            speed_gear=self.gear_var.get(),
            adb_serial=self.adb_entry.get(),
            selected_task=task
        )
    
    def stop_task(self):
        msg = ">>> 收到停止指令！(正在等待当前操作完成...)"
        log_manager.info(msg); self._log(msg)
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        # 🌟 核心：通知调度器停止
        self.runner.stop()

if __name__ == "__main__":
    app = E7DesktopApp()
    app.mainloop()
