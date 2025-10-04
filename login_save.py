#!/usr/bin/env python3
"""
第一个脚本：打开joinquant.com，等待用户登录，然后保存登录信息
"""

import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright
from browser_utils import create_isolated_browser, print_isolated_browser_info

# 存储认证状态的文件
STATE_FILE = "auth_state.json"

async def save_login_state():
    # 打印独立浏览器信息
    print_isolated_browser_info()

    async with async_playwright() as p:
        # 创建独立的浏览器实例
        context = await create_isolated_browser(p, "chromium")
        print("🔒 使用独立浏览器实例，与日常浏览器完全分离")

        # 创建新页面
        page = await context.new_page()

        print("正在打开 https://joinquant.com/ ...")
        await page.goto("https://joinquant.com/")

        print("请在浏览器中完成登录操作...")
        print("登录完成后，请在控制台输入 'y' 继续...")

        # 等待用户输入
        while True:
            user_input = input("是否已完成登录？(输入 'y' 继续): ").strip()
            if user_input == "y":
                break

        # 保存认证状态
        print("正在保存登录状态...")
        state = await context.storage_state()

        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        print(f"登录状态已保存到 {STATE_FILE}")


if __name__ == "__main__":
    asyncio.run(save_login_state())
