<div align="right">
  <a href="./README.md">简体中文</a> | <strong>English</strong>
</div>

# 🚀 Epic Seven Auto Script (E7 Auto Bot)

A desktop automation tool for *Epic Seven* built with Python, pyautogui, and CustomTkinter.
Current core feature: **Fully automatic Secret Shop refreshing (Accurately identifies and purchases Covenant Bookmarks and Mystic Medals)**.

---

## 🛠️ Environment & Dependencies

Please ensure you have [Python 3.8+](https://www.python.org/) installed on your computer.

All required dependencies are listed in `requirements.txt`, mainly including:

- `pyautogui` (For simulating mouse clicks and swipes)
- `opencv-python` & `numpy` (For image recognition and precise positioning)
- `customtkinter` (For building a modern, dark-themed GUI)

---

## 📦 Quick Start (Step-by-Step Guide for Beginners)

### Step 1: Clone the Repository

Pull the project code to your local machine and enter the project directory:

```bash
git clone https://github.com/GuaiG-MINE/e7-Scripts.git
cd e7-Scripts
```

### Step 2: Create and Activate a Virtual Environment (Highly Recommended)

To avoid messing up your local Python environment, it is highly recommended to create an isolated virtual environment in the project root directory:

```bash
# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment (Run this on Windows)
.\venv\Scripts\activate
```

*(Note: Once activated, you will see `(venv)` at the beginning of your command line prompt)*

### Step 3: Install Dependencies

Ensure your virtual environment is activated, then run the following command. The system will automatically install all required libraries:

```bash
pip install -r requirements.txt
```

### Step 4: Run the Program

Everything is ready! Launch the main GUI program:

```bash
python main.py
```

---

## 📂 Project Structure

```text
e7-Scripts/
│  main.py                 # 🌟 Main entry point (Run this to start the UI)
│  requirements.txt        # 📦 List of dependencies
│  README.md               # 📖 Project documentation (The file you are reading)
│
├─archive                  # 🗄️ Archive of historical versions (e.g., the original single-file script)
├─data
│  └─images_win            # 🖼️ Template images required for Windows desktop image recognition
└─src
    ├─core                 # ⚙️ Core controllers and global configurations
    │      config.py       # Speed gear configuration (SLOW/NORMAL/FAST)
    │      win_controller.py # Windows mouse/keyboard and image recognition controller
    ├─tasks                # 🧠 Business logic tasks
    │      base_task.py    # Base task class
    │      shop_task.py    # Specific logic implementation for shop refreshing
    └─ui                   # 🖥️ Graphical User Interface
           desktop_ui.py   # Desktop GUI based on CustomTkinter
```

---

## ⚠️ Notes & Failsafe Mechanism

1. **Emergency Stop (Failsafe)**: During script execution, if the mouse goes out of control or you want to force stop, **slam your real mouse to any of the four corners of your computer screen**. The program will trigger the failsafe mechanism and force quit.
2. **Screen Requirements**: Ensure the emulator window is not obstructed. After clicking "Start", please move your mouse over the emulator area within 3 seconds.
3. **Speed Gear Suggestion**: If your PC or emulator is a bit laggy, select the `SLOW` gear in the UI; if it's running very smoothly, choose the `FAST` gear for maximum efficiency.
