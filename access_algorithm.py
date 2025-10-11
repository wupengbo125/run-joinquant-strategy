#!/usr/bin/env python3
"""
第二个脚本：使用第一个脚本保存的登录信息访问指定的算法页面，
运行策略代码并获取执行结果
"""

import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright
from browser_utils import create_isolated_browser, print_isolated_browser_info
from path_config import get_auth_state_file

async def read_strategy_file(strategy_file):
    """读取策略文件内容"""
    try:
        with open(strategy_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✓ 成功读取策略文件: {strategy_file}")
        print(f"策略代码长度: {len(content)} 字符")
        return content
    except Exception as e:
        print(f"✗ 读取策略文件失败: {e}")
        return None

async def paste_strategy_to_editor(page, strategy_content):
    """将策略代码粘贴到代码编辑框"""
    try:
        print("正在查找代码编辑框...")

        # 方法1: 尝试通过隐藏的textarea设置Ace Editor内容
        print("尝试方法1: 通过隐藏textarea设置Ace Editor内容...")
        try:
            result = await page.evaluate("""
                (code) => {
                    // 查找隐藏的textarea（通常是Ace Editor的同步目标）
                    const hiddenTextarea = document.getElementById('code');
                    if (hiddenTextarea) {
                        // 设置textarea的值
                        hiddenTextarea.value = code;
                        // 触发input事件
                        hiddenTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                        hiddenTextarea.dispatchEvent(new Event('change', { bubbles: true }));

                        // 尝试查找Ace Editor实例并更新
                        const aceEditors = document.querySelectorAll('.ace_editor');
                        for (let aceEl of aceEditors) {
                            // Ace Editor通常会在元素上存储editor实例
                            if (aceEl.env && aceEl.env.editor) {
                                const editor = aceEl.env.editor;
                                if (editor.session) {
                                    editor.session.setValue(code);
                                    editor.clearSelection();
                                    return { success: true, method: 'hidden_textarea_and_ace_api' };
                                }
                            }
                            // 尝试其他可能的存储位置
                            if (aceEl.ace_editor) {
                                const editor = aceEl.ace_editor;
                                if (editor.session) {
                                    editor.session.setValue(code);
                                    editor.clearSelection();
                                    return { success: true, method: 'ace_editor_property' };
                                }
                            }
                        }
                        return { success: true, method: 'hidden_textarea_only' };
                    }
                    return { success: false, error: 'Hidden textarea not found' };
                }
            """, strategy_content)

            if result['success']:
                print(f"✓ 方法1成功: {result['method']}")
                await page.wait_for_timeout(1000)
                return True
            else:
                print(f"✗ 方法1失败: {result['error']}")

        except Exception as e:
            print(f"✗ 方法1执行失败: {e}")

        # 方法2: 直接操作Ace Editor的ace_text-input
        print("尝试方法2: 通过ace_text-input...")
        try:
            ace_inputs = await page.query_selector_all(".ace_text-input")
            for ace_input in ace_inputs:
                if await ace_input.is_visible():
                    await ace_input.click()
                    await page.wait_for_timeout(500)

                    # 全选并清空
                    await page.keyboard.press('Control+a')
                    await page.wait_for_timeout(200)
                    await page.keyboard.press('Delete')
                    await page.wait_for_timeout(200)

                    # 输入新代码
                    await page.keyboard.type(strategy_content)
                    print("✓ 方法2成功: 通过ace_text-input键盘输入")
                    await page.wait_for_timeout(1000)
                    return True
        except Exception as e:
            print(f"✗ 方法2执行失败: {e}")

        # 方法3: 直接填充隐藏textarea
        print("尝试方法3: 直接填充隐藏textarea...")
        try:
            hidden_textarea = await page.wait_for_selector("#code", timeout=3000)
            if hidden_textarea:
                await hidden_textarea.fill(strategy_content)
                print("✓ 方法3成功: 直接填充隐藏textarea")
                await page.wait_for_timeout(1000)
                return True
        except:
            print("✗ 方法3: 未找到隐藏textarea")

        # 方法4: 通过剪贴板粘贴
        print("尝试方法4: 通过剪贴板粘贴...")
        try:
            # 设置剪贴板内容
            await page.evaluate("""
                (text) => {
                    navigator.clipboard.writeText(text).then(() => {
                        console.log('Clipboard set successfully');
                    }).catch(err => {
                        console.error('Failed to set clipboard:', err);
                    });
                }
            """, strategy_content)

            # 点击编辑器并粘贴
            ace_inputs = await page.query_selector_all(".ace_text-input")
            for ace_input in ace_inputs:
                if await ace_input.is_visible():
                    await ace_input.click()
                    await page.wait_for_timeout(500)
                    await page.keyboard.press('Control+v')
                    print("✓ 方法4成功: 通过剪贴板粘贴")
                    await page.wait_for_timeout(1000)
                    return True
        except Exception as e:
            print(f"✗ 方法4执行失败: {e}")

        print("✗ 所有方法都失败了")
        return False

    except Exception as e:
        print(f"✗ 粘贴策略代码失败: {e}")
        return False

async def click_compile_and_run(page):
    """点击编译运行按钮"""
    try:
        print("正在查找编译运行按钮...")

        # 编译运行按钮的可能选择器（基于您提供的HTML结构）
        compile_selectors = [
            "#buildBtn",
            "#buildBtn span",
            "#buildBtn .active-text",
            "span[title='编译运行(Ctrl+Alt+B)']",
            "span:has-text('编译运行')",
            "button:has-text('编译运行')",
            "button:has-text('运行')",
            "button:has-text('执行')",
            "button:has-text('Run')",
            "button:has-text('Compile')",
            ".compile-btn",
            ".run-btn",
            "[data-testid='compile-run']",
            "[data-testid='run']",
            "button.run-button",
            "button.compile-button",
            ".btn-primary:has-text('运行')",
            ".btn-success:has-text('运行')",
            "button.btn.run"
        ]

        for selector in compile_selectors:
            try:
                button = await page.wait_for_selector(selector, timeout=2000)
                if button:
                    print(f"✓ 找到编译运行按钮: {selector}")
                    await button.click()
                    print("✓ 成功点击编译运行按钮")
                    return True
            except:
                continue

        print("✗ 未找到编译运行按钮")
        return False

    except Exception as e:
        print(f"✗ 点击编译运行按钮失败: {e}")
        return False

async def read_execution_logs(page):
    """读取右下角的日志输出"""
    try:
        print("等待20秒让代码执行...")
        await page.wait_for_timeout(20000)

        print("正在读取执行日志...")

        # 专门查找纯错误信息的JavaScript方法
        try:
            error_logs = await page.evaluate("""
                () => {
                    // 查找包含错误的日志容器
                    const errorContainers = [
                        '#daily-logs-tab',
                        '#daily-logs-container',
                        '#log',
                        '#log pre',
                        '.logs-container',
                        '.logs-container pre'
                    ];

                    let errorText = '';

                    // 方法1: 从错误容器中查找
                    errorContainers.forEach(selector => {
                        const container = document.querySelector(selector);
                        if (container) {
                            const text = container.textContent || '';

                            // 提取错误部分
                            const errorMatch = text.match(/(?:ERROR|错误|Traceback|AttributeError)[\\s\\S]*?(?=\\n\\n|正在加载日志|结束\\.|$)/);
                            if (errorMatch) {
                                errorText = errorMatch[0].trim();
                            }
                        }
                    });

                    // 方法2: 如果没找到，从整个页面查找错误
                    if (!errorText) {
                        const allElements = document.querySelectorAll('div, pre, code');
                        for (let el of allElements) {
                            const text = el.textContent || '';

                            // 查找包含关键错误信息的文本
                            if (text.includes('Traceback') || text.includes('AttributeError') ||
                                text.includes('ERROR') || text.includes('错误')) {

                                // 提取错误堆栈
                                const errorMatch = text.match(/(?:Traceback[\s\S]*?)(?=\\n\\n|$)/);
                                if (errorMatch) {
                                    errorText = errorMatch[0].trim();
                                    break;
                                }
                            }
                        }
                    }

                    return errorText;
                }
            """)

            if error_logs and error_logs.strip():
                print("✓ 成功提取错误信息")
                return error_logs.strip()
            else:
                return "run successful"

        except Exception as e:
            print(f"错误查找失败: {e}")
            return "错误信息提取失败"


    except Exception as e:
        print(f"✗ 读取日志失败: {e}")
        return f"读取日志时出错: {e}"

async def access_algorithm_page(strategy_file=None):
    # 检查认证状态文件是否存在
    auth_file = get_auth_state_file()
    if not os.path.exists(auth_file):
        print(f"错误: 找不到认证状态文件 {auth_file}")
        print("请先运行 login_save.py 进行登录并保存认证信息")
        return

    # 读取策略文件
    if strategy_file:
        strategy_content = await read_strategy_file(strategy_file)
        if not strategy_content:
            return
    else:
        print("⚠ 未提供策略文件，将只访问页面不执行代码")
        strategy_content = None

    async with async_playwright() as p:
        # 创建独立的浏览器实例
        context = await create_isolated_browser(p, "chromium")
        print("🔒 使用独立浏览器实例，与日常浏览器完全分离")

        # 加载保存的认证状态
        with open(auth_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        await context.add_cookies(state.get("cookies", []))

        # 创建新页面
        page = await context.new_page()

        try:
            # 访问算法页面
            algorithm_url = "https://joinquant.com/algorithm/index/edit?algorithmId=c639f7b5fba58e5d1d18c693e713e87b"
            print(f"正在访问算法页面: {algorithm_url}")

            await page.goto(algorithm_url)

            # 等待页面加载
            await page.wait_for_load_state("networkidle")

            print("页面加载完成，等待3秒以便完全渲染...")
            await page.wait_for_timeout(3000)

            # 已有状态的浏览器不需要点击跳过和不再提示按钮
            print("✅ 已有登录状态，跳过提示操作")

            # 如果有策略代码，执行相关操作
            if strategy_content:
                # 粘贴策略代码到编辑框
                paste_success = await paste_strategy_to_editor(page, strategy_content)
                if not paste_success:
                    print("✗ 无法粘贴策略代码，退出执行")
                    return

                # 等待一下确保代码已经粘贴
                await page.wait_for_timeout(1000)

                # 直接在编辑页面点击编译运行按钮
                print("在编辑页面查找编译运行按钮...")
                compile_success = await click_compile_and_run(page)
                if not compile_success:
                    print("✗ 无法点击编译运行，尝试其他方法...")

                    # 尝试按Ctrl+Alt+B快捷键
                    print("尝试快捷键运行...")
                    await page.keyboard.press('Control+Alt+B')
                    await page.wait_for_timeout(2000)

                    # 或者尝试Ctrl+Enter
                    await page.keyboard.press('Control+Enter')
                    await page.wait_for_timeout(2000)

                # 读取执行日志
                execution_logs = await read_execution_logs(page)

                print("\n" + "="*30)
                print("log message")
                print("="*30)
                print(execution_logs)
                print("="*30)


        except Exception as e:
            print(f"✗ 执行过程中出现错误: {e}")

        finally:
            # 自动关闭浏览器
            if 'browser' in locals():
                await browser.close()

if __name__ == "__main__":
    strategy_file = None
    if len(sys.argv) > 1:
        strategy_file = sys.argv[1]
        print(f"使用策略文件: {strategy_file}")
    else:
        print("未提供策略文件参数")
        print("用法: python access_algorithm.py [strategy_file.py]")

    asyncio.run(access_algorithm_page(strategy_file))
