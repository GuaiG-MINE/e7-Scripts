import pyautogui
import time
import os

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
SPEED_CONFIG = SPEED_PROFILES[CURRENT_GEAR]
# ==========================================

pyautogui.FAILSAFE = True
pyautogui.PAUSE = SPEED_CONFIG['global_pause']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(BASE_DIR, 'data', 'images')
stats = {'blue': 0, 'red': 0}

def get_img_path(img_name):
    return os.path.join(IMAGE_DIR, img_name)

def safe_locate(img_name, conf=0.85, region=None):
    """🛡️ 安全查找图片"""
    img_path = get_img_path(img_name)
    if not os.path.exists(img_path):
        return None
    try:
        if region:
            return pyautogui.locateCenterOnScreen(img_path, confidence=conf, region=region)
        return pyautogui.locateCenterOnScreen(img_path, confidence=conf)
    except Exception:
        return None

def find_and_buy(icon_img_name):
    """【精准双重锁定版】左边认图标，右边认 1/1购买 -> 弹窗认全图"""
    icon_center = safe_locate(icon_img_name, conf=0.8)
    
    if icon_center:
        item_name = "誓约书签(蓝)" if "blue" in icon_img_name else "神秘奖牌(红)"
        print(f"🎯 发现目标图标 [{item_name}]！正在寻找购买按钮...")
        
        # 划定搜索区域：精准锁定下半区！
        # 起点Y：图标中心往上 15 像素
        # 高度：100 像素 (完美包裹当前按钮，绝对不越界)
        screen_w, screen_h = pyautogui.size()
        search_region = (0, max(0, int(icon_center.y - 15)), screen_w, 100)

        # 找新的带有 1/1 的购买按钮
        buy_center = safe_locate('buy_btn.png', conf=0.75, region=search_region)
        
        if buy_center:
            pyautogui.click(buy_center.x, buy_center.y, duration=SPEED_CONFIG['click_move'])
            time.sleep(SPEED_CONFIG['wait_popup'])  
            
            # 🌟 动态决定要找哪张完整的确认图
            if "blue" in icon_img_name:
                confirm_img = 'confirm_buy_blue.png'
            else:
                confirm_img = 'confirm_buy_red.png'
                
            # 寻找对应的完整弹窗确认按钮
            confirm_center = safe_locate(confirm_img, conf=0.8)
            
            if confirm_center:
                pyautogui.click(confirm_center.x, confirm_center.y, duration=SPEED_CONFIG['click_move'])
                print(f"✅ 成功进货 1 次 {item_name}！")
                time.sleep(SPEED_CONFIG['wait_buy_done'])
                return True
            else:
                print(f"⚠️ 没找到弹窗的确认按钮({confirm_img})，点空白处防卡死...")
                pyautogui.click(icon_center.x, icon_center.y - 200, duration=SPEED_CONFIG['click_move'])
                time.sleep(SPEED_CONFIG['wait_cancel'])
        else:
            print("⚠️ 找到图标了，但没找到右侧的 [1/1 购买] 按钮？")
            
    return False



def swipe_up():
    """滑动屏幕"""
    screen_width, screen_height = pyautogui.size()
    center_x = screen_width // 2
    center_y = screen_height // 2
    
    pyautogui.moveTo(center_x, center_y + 200)
    pyautogui.dragTo(center_x, center_y - 250, duration=SPEED_CONFIG['swipe_drag'], button='left')
    time.sleep(SPEED_CONFIG['wait_after_swipe'])

def refresh_shop():
    """刷新商店"""
    refresh_center = safe_locate('refresh_btn.png', conf=0.85)
    if refresh_center:
        pyautogui.click(refresh_center.x, refresh_center.y, duration=SPEED_CONFIG['click_move'])
        time.sleep(SPEED_CONFIG['wait_refresh_pop'])
        
        confirm_center = safe_locate('confirm_refresh_btn.png', conf=0.85)
        if confirm_center:
            pyautogui.click(confirm_center.x, confirm_center.y, duration=SPEED_CONFIG['click_move'])
            time.sleep(SPEED_CONFIG['wait_refresh_done'])

def main():
    print(f"🚀 第七史诗刷店脚本已启动！当前挡位：【{CURRENT_GEAR}】")
    print("请在 3 秒内切换到模拟器画面...")
    time.sleep(3)
    
    loop_count = 1
    while True:
        print(f"\n--- 第 {loop_count} 次巡逻 ---")
        
        # 每一轮刷新后，重置购买状态
        blue_bought = False
        red_bought = False
        
        # 1️⃣ 上半区搜寻
        if find_and_buy('icon_blue.png'):
            stats['blue'] += 1
            blue_bought = True
            
        if find_and_buy('icon_red.png'):
            stats['red'] += 1
            red_bought = True
            
        # 2️⃣ 判断是否需要滑动（如果两个都买到了，直接跳过滑动，进入刷新！）
        if not (blue_bought and red_bought):
            swipe_up()
            
            # 3️⃣ 下半区搜寻 (只找上半区没买到的东西！)
            if not blue_bought and find_and_buy('icon_blue.png'):
                stats['blue'] += 1
                
            if not red_bought and find_and_buy('icon_red.png'):
                stats['red'] += 1
        else:
            print("🎉 天胡开局！上半区已全收，直接刷新！")
            
        print(f"🏆 战绩: 蓝票 {stats['blue']} | 红票 {stats['red']}")
        
        # 4️⃣ 刷新商店
        refresh_shop()
        
        loop_count += 1
        time.sleep(SPEED_CONFIG['loop_interval'])

if __name__ == "__main__":
    main()
