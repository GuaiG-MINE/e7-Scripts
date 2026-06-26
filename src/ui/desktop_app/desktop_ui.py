#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : desktop_ui.py
@Author  : Guaig
@Date    : 2026-06-25
@Desc    : Windows & ADB 双模式桌面应用界面 (深邃紫中控台版)
"""

import customtkinter as ctk
from src.core.config import get_text as _, set_lang, STRINGS
from src.core.logger import log_manager
from src.core.game_runner import GameRunner

# ==================== 全局自定义配色 ====================
ctk.set_appearance_mode("dark")
# 抛弃默认主题，全量自定义颜色
BG_MAIN = "#13131A"         # 极暗深空背景
CARD_BG = "#1C1C26"         # 卡片底色 (带点紫灰)
ACCENT_PURPLE = "#8B5CF6"   # 优雅主色调：紫色
BTN_START = "#10B981"       # 祖母绿
BTN_STOP = "#F43F5E"        # 玫瑰红
TEXT_MAIN = "#E2E8F0"       # 亮灰白文字
TEXT_SUB = "#94A3B8"        # 暗灰文字

class E7DesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(_("app_title"))  
        # 尺寸更加紧凑方正，比例更舒服
        self.geometry("680x600")  
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 340
        y = (self.winfo_screenheight() // 2) - 300
        self.geometry(f"+{x}+{y}")
        
        # 🌟 新增：用于缓存当前的战绩字符串后缀，防止停止时被清空
        self.current_stats_str = ""
        
        self.runner = GameRunner(
            log_cb=lambda msg: self.after(0, self._log, msg),
            shop_stats_cb=self.update_shop_stats_ui,
            general_stats_cb=self.update_general_stats_ui,
            finish_cb=self._on_task_finish
        )
        
        # 让底部日志区自动扩展
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self._build_ui()
    
    def _build_ui(self):
        self._build_header()
        self._build_control_deck()
        self._build_log_area()
        
    # ==================== 顶部：标题与语言 ====================
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 10))
        header.grid_columnconfigure(1, weight=1)
        
        # 标题
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_box, text="E7 Assistant", font=ctk.CTkFont(family="Verdana", size=24, weight="bold"), text_color=ACCENT_PURPLE).pack(anchor="w")
        self.title_label = ctk.CTkLabel(title_box, text=_("ui_title"), font=ctk.CTkFont(size=12), text_color=TEXT_SUB)
        self.title_label.pack(anchor="w")
        
        # 语言下拉框
        self.lang_var = ctk.StringVar(value="中文")
        self.lang_menu = ctk.CTkOptionMenu(
            header, values=["中文", "English"], variable=self.lang_var, width=90,
            fg_color=CARD_BG, button_color=CARD_BG, button_hover_color="#2D2D3B", text_color=TEXT_MAIN,
            command=self._on_lang_change
        )
        self.lang_menu.grid(row=0, column=2, sticky="e")

    # ==================== 中部：中控台 (设置 + 按钮 并排) ====================
    def _build_control_deck(self):
        deck = ctk.CTkFrame(self, fg_color="transparent")
        deck.grid(row=1, column=0, sticky="ew", padx=25, pady=10)
        deck.grid_columnconfigure(0, weight=3) # 左侧配置区占 3 份宽度
        deck.grid_columnconfigure(1, weight=2) # 右侧按钮区占 2 份宽度
        
        # --- 左侧：配置面板 ---
        config_card = ctk.CTkFrame(deck, fg_color=CARD_BG, corner_radius=12)
        config_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        # 使用 grid 排列设置项，整齐划一
        config_card.grid_columnconfigure(1, weight=1)
        
        label_font = ctk.CTkFont(size=13)
        menu_kwargs = {"fg_color": BG_MAIN, "button_color": BG_MAIN, "button_hover_color": "#2D2D3B", "text_color": TEXT_MAIN}

        # 任务
        ctk.CTkLabel(config_card, text="任务类型", font=label_font, text_color=TEXT_SUB).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        self.task_var = ctk.StringVar(value="商店自动刷新")  
        self.task_menu = ctk.CTkOptionMenu(config_card, values=["商店自动刷新", "自动NPC竞技场"], variable=self.task_var, command=self._on_task_change, **menu_kwargs)
        self.task_menu.grid(row=0, column=1, padx=15, pady=(15, 10), sticky="ew")

        # 模式
        self.mode_label = ctk.CTkLabel(config_card, text=_("run_mode"), font=label_font, text_color=TEXT_SUB)
        self.mode_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.mode_var = ctk.StringVar(value=_("mode_adb"))  
        self.mode_menu = ctk.CTkOptionMenu(config_card, values=[_("mode_adb"), _("mode_win")], variable=self.mode_var, command=self._on_mode_change, **menu_kwargs)
        self.mode_menu.grid(row=1, column=1, padx=15, pady=10, sticky="ew")

        # ADB / 速度
        self.adb_label = ctk.CTkLabel(config_card, text=_("adb_address"), font=label_font, text_color=TEXT_SUB)
        self.adb_label.grid(row=2, column=0, padx=15, pady=(10, 15), sticky="w")
        self.adb_entry = ctk.CTkEntry(config_card, fg_color=BG_MAIN, border_width=0, text_color=TEXT_MAIN)
        self.adb_entry.insert(0, "127.0.0.1:16384")  
        self.adb_entry.grid(row=2, column=1, padx=15, pady=(10, 15), sticky="ew")
        
        self.gear_var = ctk.StringVar(value="FAST")
        self.gear_menu = ctk.CTkOptionMenu(config_card, values=["SLOW", "NORMAL", "FAST"], variable=self.gear_var, **menu_kwargs)

        # --- 右侧：大按钮控制区 ---
        btn_card = ctk.CTkFrame(deck, fg_color=CARD_BG, corner_radius=12)
        btn_card.grid(row=0, column=1, sticky="nsew")
        btn_card.grid_columnconfigure(0, weight=1)
        btn_card.grid_rowconfigure((0, 1), weight=1)
        
        btn_font = ctk.CTkFont(size=16, weight="bold")
        self.start_btn = ctk.CTkButton(btn_card, text="▶  " + _("btn_start"), command=self.start_task, font=btn_font,
                                       fg_color=BTN_START, hover_color="#059669", text_color="#FFFFFF")
        self.start_btn.grid(row=0, column=0, sticky="nsew", padx=15, pady=(15, 7))
        
        self.stop_btn = ctk.CTkButton(btn_card, text="⏹  " + _("btn_stop"), command=self.stop_task, font=btn_font, state="disabled",
                                      fg_color=BTN_STOP, hover_color="#E11D48", text_color="#FFFFFF")
        self.stop_btn.grid(row=1, column=0, sticky="nsew", padx=15, pady=(7, 15))

    # ==================== 底部：状态栏与日志 ====================
    def _build_log_area(self):
        log_container = ctk.CTkFrame(self, fg_color="transparent")
        log_container.grid(row=2, column=0, sticky="nsew", padx=25, pady=(5, 20))
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(1, weight=1)
        
        # 状态战绩条 (紧凑型)
        self.stats_bar = ctk.CTkFrame(log_container, fg_color=ACCENT_PURPLE, corner_radius=6, height=32)
        self.stats_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.stats_bar.pack_propagate(False)
        
        self.stats_label = ctk.CTkLabel(self.stats_bar, text="等待系统指令...", font=ctk.CTkFont(size=13, weight="bold"), text_color="#FFFFFF")
        self.stats_label.pack(side="left", padx=15)

        # 终端日志
        self.log_text = ctk.CTkTextbox(log_container, fg_color="#0B0B0F", text_color="#CBD5E1", font=ctk.CTkFont(family="Consolas", size=12), corner_radius=8, border_width=1, border_color="#2D2D3B")
        self.log_text.grid(row=1, column=0, sticky="nsew")
        self.log_text.insert("0.0", _("log_ready") + "\n")  
        self.log_text.configure(state="disabled")

    # ==================== UI 状态更新与回调 ====================
    def update_shop_stats_ui(self, blue, red, refresh):
        # 🌟 核心修改：将战绩部分分离出来缓存
        self.current_stats_str = f"   |   🔖 誓约书签: {blue}    🏅 神秘奖牌: {red}    🔄 刷新次数: {refresh}"
        text = f"运行状态: 刷店中{self.current_stats_str}"
        self.after(0, lambda: self.stats_label.configure(text=text))
        
    def update_general_stats_ui(self, text):
        self.current_stats_str = ""
        self.after(0, lambda: self.stats_label.configure(text=f"运行状态: {text}"))

    def _log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        
    def _on_task_finish(self):
        self.after(0, lambda: self.start_btn.configure(state="normal"))
        self.after(0, lambda: self.stop_btn.configure(state="disabled"))
        # 🌟 核心修改：停止时拼接缓存的战绩字符串
        self.after(0, lambda: self.stats_label.configure(text=f"任务已停止{self.current_stats_str}"))
        self.after(0, lambda: self.stats_bar.configure(fg_color="#475569")) # 停止时变灰

    # ==================== 交互事件 ====================
    def _on_lang_change(self, choice):
        set_lang("en" if choice == "English" else "zh")  
        self.title(_("app_title"))
        self.title_label.configure(text=_("ui_title"))
        self.mode_label.configure(text=_("run_mode"))
        self.adb_label.configure(text=_("adb_address"))
        self.start_btn.configure(text="▶  " + _("btn_start"))
        self.stop_btn.configure(text="⏹  " + _("btn_stop"))
        is_win = (self.mode_var.get() in [STRINGS["zh"]["mode_win"], STRINGS["en"]["mode_win"]])
        self.mode_menu.configure(values=[_("mode_adb"), _("mode_win")])
        self.mode_var.set(_("mode_win") if is_win else _("mode_adb"))

    def _on_mode_change(self, choice):
        if choice == _("mode_win"):  
            self.adb_label.grid_remove()
            self.adb_entry.grid_remove()
            # 替换为速度挡位
            self.adb_label.configure(text=_("speed_gear"))
            self.adb_label.grid(row=2, column=0, padx=15, pady=(10, 15), sticky="w")
            self.gear_menu.grid(row=2, column=1, padx=15, pady=(10, 15), sticky="ew")
        else:
            self.gear_menu.grid_remove()
            self.adb_label.configure(text=_("adb_address"))
            self.adb_label.grid(row=2, column=0, padx=15, pady=(10, 15), sticky="w")
            self.adb_entry.grid(row=2, column=1, padx=15, pady=(10, 15), sticky="ew")
            
    def _on_task_change(self, choice):
        if choice == "商店自动刷新": 
            self.update_shop_stats_ui(0, 0, 0)
            self.stats_bar.configure(fg_color=ACCENT_PURPLE)
        else: 
            self.update_general_stats_ui("竞技场准备就绪")
            self.stats_bar.configure(fg_color=ACCENT_PURPLE)

    def start_task(self):
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.stats_bar.configure(fg_color=BTN_START) # 运行时变绿
        
        task = self.task_var.get()
        self._on_task_change(task) 
        
        is_adb = (self.mode_var.get() != _("mode_win"))
        msg = f">>> 准备执行【{task}】..."
        log_manager.info(msg); self._log(msg)
        
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
        self.stats_label.configure(text=f"正在停止...{self.current_stats_str}")
        self.stats_bar.configure(fg_color=BTN_STOP) # 停止中变红
        self.runner.stop()

if __name__ == "__main__":
    app = E7DesktopApp()
    app.mainloop()
