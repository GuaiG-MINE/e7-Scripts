import pyautogui
import time

# 安全机制：遇到程序失控，快速把鼠标移动到屏幕四个角落的任意一个，程序会立刻报错停止！
pyautogui.FAILSAFE = True 

def click_target(image_path, threshold=0.8):
    """
    在屏幕上寻找目标图片并点击
    :param image_path: 按钮图片的路径
    :param threshold: 相似度阈值（0.8表示80%相似即可）
    :return: 是否成功点击
    """
    try:
        # confidence=threshold 需要 opencv-python 的支持
        location = pyautogui.locateCenterOnScreen(image_path, confidence=threshold)
        if location is not None:
            print(f"[{time.strftime('%H:%M:%S')}] 找到目标 {image_path}，执行点击！")
            # 移动鼠标并点击，duration=0.2 让移动看起来稍微自然一点
            pyautogui.moveTo(location.x, location.y, duration=0.2)
            pyautogui.click()
            return True
    except Exception as e:
        # 如果没找到，pyautogui 可能会抛出异常，我们直接忽略继续找
        pass 
    return False

def main():
    print("🤖 手游脚本已启动！")
    print("👉 请在 3 秒内将游戏模拟器放在屏幕最前面...")
    print("⚠️ 提示：如果想强行停止脚本，请快速将鼠标甩到屏幕最角落！")
    time.sleep(3)
    
    print("开始循环检测屏幕...")
    # 游戏主循环
    while True:
        # 场景 1：如果看到“开始游戏”按钮
        if click_target('start_btn.png', threshold=0.85):
            time.sleep(2) # 点击后等待2秒，防止游戏响应慢导致重复点击
            continue      # 直接进入下一轮检测
            
        # 场景 2：如果看到“跳过剧情”按钮
        if click_target('skip_btn.png', threshold=0.8):
            time.sleep(1)
            continue
            
        # 场景 3：如果看到“领取奖励”按钮
        if click_target('reward_btn.png', threshold=0.85):
            time.sleep(2)
            continue
            
        # 如果什么都没找到，稍微休息 0.5 秒继续找，防止把电脑 CPU 占满
        time.sleep(0.5)

if __name__ == "__main__":
    main()
