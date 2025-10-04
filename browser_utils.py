#!/usr/bin/env python3
"""
浏览器工具模块：提供连接现有浏览器的多种方法
"""

import asyncio
import os
import subprocess
import sys
from playwright.async_api import async_playwright

async def create_isolated_browser(playwright, browser_type="chromium"):
    """
    创建独立的浏览器实例，使用用户自己的Chrome浏览器

    Args:
        playwright: playwright实例
        browser_type: 浏览器类型 ('chromium', 'chrome', 'firefox')

    Returns:
        context: 浏览器上下文实例
    """
    try:
        # 创建专用的浏览器数据目录
        persistent_dir = os.path.join(os.getcwd(), "joinquant_browser_data")
        os.makedirs(persistent_dir, exist_ok=True)

        # 创建子目录
        for subdir in ["Default", "Extensions", "Policy"]:
            os.makedirs(os.path.join(persistent_dir, subdir), exist_ok=True)

        print(f"🔧 创建独立浏览器实例，使用您的Chrome浏览器")
        print(f"📁 数据将保存在: {persistent_dir}")

        # 查找用户Chrome可执行文件路径
        chrome_exe = get_user_chrome_executable()
        if chrome_exe:
            print(f"🌐 使用Chrome: {chrome_exe}")
            # 使用用户自己的Chrome浏览器
            context = await playwright.chromium.launch_persistent_context(
                user_data_dir=persistent_dir,
                headless=False,
                viewport={"width": 1920, "height": 1080},
                executable_path=chrome_exe,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-extensions-except",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-features=TranslateUI",
                    "--disable-ipc-flooding-protection",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-site-isolation-trials",
                    "--no-first-run",
                    "--disable-default-apps",
                    "--disable-sync",
                    "--metrics-recording-only",
                    "--disable-default-browser-check"
                ]
            )
            print("✅ 使用您的Chrome浏览器创建实例成功")
        else:
            print("⚠️ 未找到Chrome，使用Playwright内置的Chromium")
            context = await playwright.chromium.launch_persistent_context(
                user_data_dir=persistent_dir,
                headless=False,
                viewport={"width": 1920, "height": 1080},
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-extensions-except",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-features=TranslateUI",
                    "--disable-ipc-flooding-protection",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-site-isolation-trials",
                    "--no-first-run",
                    "--disable-default-apps",
                    "--disable-sync",
                    "--metrics-recording-only",
                    "--disable-default-browser-check"
                ]
            )
            print("✅ 使用Chromium创建实例成功")

        print("🔒 这是专用实例，与您的日常浏览器配置分离")
        return context

    except Exception as e:
        print(f"✗ 创建独立浏览器失败: {e}")
        # 如果失败，尝试创建普通浏览器
        print("尝试创建普通浏览器实例...")
        return await playwright.chromium.launch(headless=False)

def get_user_chrome_executable():
    """获取用户Chrome可执行文件路径"""
    chrome_paths = []

    if sys.platform == "win32":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
    elif sys.platform == "darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ]
    else:  # Linux
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/google-chrome-beta",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
            os.path.expanduser("~/.local/bin/google-chrome"),
            os.path.expanduser("~/bin/google-chrome"),
            "google-chrome",
            "google-chrome-stable",
            "chromium-browser",
            "chromium",
        ]

    # 检查每个路径
    for path in chrome_paths:
        if os.path.exists(path):
            return path
        else:
            # 尝试使用which命令
            try:
                result = subprocess.run(["which", path], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            except:
                continue

    return None

def get_isolated_browser_info():
    """获取独立浏览器信息"""
    persistent_dir = os.path.join(os.getcwd(), "joinquant_browser_data")

    info = {
        "data_dir": persistent_dir,
        "profile_dir": os.path.join(persistent_dir, "Default"),
        "extensions_dir": os.path.join(persistent_dir, "Extensions"),
        "is_initialized": os.path.exists(persistent_dir) and os.path.exists(os.path.join(persistent_dir, "Default"))
    }

    return info

def print_isolated_browser_info():
    """打印独立浏览器信息"""
    info = get_isolated_browser_info()

    print("\n" + "="*60)
    print("🔒 独立浏览器实例信息")
    print("="*60)
    print(f"📁 数据目录: {info['data_dir']}")
    print(f"👤 配置目录: {info['profile_dir']}")
    print(f"🧩 扩展目录: {info['extensions_dir']}")
    print(f"🔄 已初始化: {'是' if info['is_initialized'] else '否'}")

    print("\n✨ 特点:")
    print("  ✅ 与日常浏览器完全分离")
    print("  ✅ 专用的数据存储")
    print("  ✅ 独立的登录状态")
    print("  ✅ 不会影响您的Chrome配置")
    print("  ✅ 可以重复使用保存的登录信息")

    print("\n🧹 如果需要重置:")
    print(f"  rm -rf {info['data_dir']}")

    print("="*60)

def get_chrome_user_data_dir():
    """获取Chrome用户数据目录"""
    if sys.platform == "win32":
        return os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    elif sys.platform == "darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/Google/Chrome")
    else:  # Linux
        home = os.path.expanduser("~")
        possible_dirs = [
            f"{home}/.config/google-chrome",
            f"{home}/.config/chromium",
            f"{home}/.config/google-chrome-beta",
            f"{home}/snap/chromium/common/chromium"
        ]
        for dir_path in possible_dirs:
            if os.path.exists(dir_path):
                return dir_path
        return possible_dirs[0]  # 返回默认路径

def start_chrome_with_debugging():
    """启动Chrome并开启远程调试"""
    chrome_cmd = None

    if sys.platform == "win32":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
        ]
    elif sys.platform == "darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium"
        ]
    else:  # Linux
        chrome_paths = [
            "google-chrome",
            "google-chrome-stable",
            "chromium-browser",
            "chromium",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium"
        ]

    # 找到可执行的Chrome
    chrome_executable = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_executable = path
            break
        else:
            # 尝试which命令
            try:
                result = subprocess.run(["which", path],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    chrome_executable = result.stdout.strip()
                    break
            except:
                continue

    if not chrome_executable:
        return False, "未找到Chrome浏览器"

    # 启动Chrome并开启远程调试
    try:
        args = [
            chrome_executable,
            "--remote-debugging-port=9222",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--user-data-dir=" + os.path.join(os.getcwd(), "chrome_debug")
        ]

        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, "Chrome已启动，等待连接..."
    except Exception as e:
        return False, f"启动Chrome失败: {e}"

def print_browser_setup_instructions():
    """打印浏览器设置说明"""
    print("\n" + "="*60)
    print("如何使用现有浏览器:")
    print("="*60)

    print("\n方法1: 手动启动Chrome并开启远程调试")
    print("1. 完全关闭Chrome浏览器")
    print("2. 使用以下命令启动Chrome:")

    if sys.platform == "win32":
        print('   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')
    elif sys.platform == "darwin":
        print('   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222')
    else:  # Linux
        print('   google-chrome --remote-debugging-port=9222')
        print('   或 chromium-browser --remote-debugging-port=9222')

    print("3. 保持Chrome打开，然后运行脚本")

    print("\n方法2: 使用持久化浏览器数据")
    print("脚本会自动使用持久化数据目录，保存历史记录、密码等")

    print("\n方法3: 让脚本自动启动Chrome")
    print("脚本可以自动启动Chrome并配置好调试模式")

    print("\n" + "="*60)