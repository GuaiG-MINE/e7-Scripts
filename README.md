
<div align="right">
  <strong>简体中文</strong> | <a href="./README_EN.md">English</a>
</div>

# 🚀 E7 全自动挂机助手 (Epic Seven Auto Script)

基于 Python + pyautogui + CustomTkinter 打造的《第七史诗》桌面端自动化辅助工具。
目前支持核心功能：**全自动刷秘密商店（精准识别并购买誓约书签与神秘奖牌）**。

---

## 🛠️ 环境与依赖准备

请确保你的电脑已安装 [Python 3.8+](https://www.python.org/)。

本项目所需的所有依赖库均已列在 `requirements.txt` 中，主要包含：

- `pyautogui` (用于模拟鼠标点击和滑动)
- `opencv-python` & `numpy` (用于图像识别和精准定位)
- `customtkinter` (用于构建现代化的暗黑风格图形界面)

---

## 📦 快速开始 (保姆级教程)

### 第一步：克隆仓库

将项目代码拉取到本地，并进入项目目录：

```bash
git clone https://github.com/GuaiG-MINE/e7-Scripts.git
cd e7-Scripts
```

### 第二步：创建并激活虚拟环境 (强烈推荐)

为了不弄乱你电脑原本的 Python 环境，建议在项目根目录下创建一个独立的虚拟环境：

```bash
# 创建名为 venv 的虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows 系统请执行此命令)
.\venv\Scripts\activate
```

*(注：激活成功后，你的命令行输入框最前面会出现 `(venv)` 字样)*

### 第三步：一键安装依赖库

确保虚拟环境已激活，然后执行以下命令，系统会自动根据清单安装所有需要的库：

```bash
pip install -r requirements.txt
```

### 第四步：运行程序

一切准备就绪！启动图形化主程序：

```bash
python main.py
```

---

## 📂 项目结构说明

```text
e7-Scripts/
│  main.py                 # 🌟 程序主入口 (直接运行这个即可启动 UI)
│  requirements.txt        # 📦 依赖库清单文件
│  README.md               # 📖 项目说明文档 (你正在看的这个文件)
│
├─archive                  # 🗄️ 历史版本存档 (如第一代原始单文件脚本)
├─data
│  └─images_win            # 🖼️ Windows 桌面端找图所需的模板图片
└─src
    ├─core                 # ⚙️ 核心控制器与全局配置
    │      config.py       # 速度挡位配置 (SLOW/NORMAL/FAST)
    │      win_controller.py # Windows 鼠标键盘与图像识别控制器
    ├─tasks                # 🧠 业务逻辑任务
    │      base_task.py    # 任务基类
    │      shop_task.py    # 刷商店的具体逻辑实现
    └─ui                   # 🖥️ 图形化界面
           desktop_ui.py   # 基于 CustomTkinter 的桌面端可视化界面
```

---

## ⚠️ 注意事项与防爆死机制

1. **紧急停止（防爆死）**：脚本运行期间，如果鼠标失控或想紧急停止，请**将真实鼠标用力甩向电脑屏幕的四个角落中的任意一角**，程序会自动触发安全机制并强行停止。
2. **画面要求**：请确保模拟器画面无遮挡。点击“开始挂机”后，请在 3 秒内将鼠标移至模拟器区域。
3. **挡位建议**：如果你的电脑或模拟器较卡，请在界面中选择 `SLOW` 挡位；如果非常流畅，可选择 `FAST` 挡位以追求极限效率。
