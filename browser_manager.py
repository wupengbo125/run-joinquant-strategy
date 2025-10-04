#!/usr/bin/env python3
"""
独立浏览器管理工具
"""

import os
import shutil
import sys
from browser_utils import get_isolated_browser_info, print_isolated_browser_info

def show_browser_info():
    """显示浏览器信息"""
    print_isolated_browser_info()

def reset_browser():
    """重置浏览器数据"""
    info = get_isolated_browser_info()

    if not info['is_initialized']:
        print("🔍 独立浏览器尚未初始化")
        return

    print("⚠️  这将删除所有独立浏览器数据，包括登录状态")
    confirm = input("确定要重置吗？(输入 'yes' 确认): ").strip().lower()

    if confirm == 'yes':
        try:
            shutil.rmtree(info['data_dir'])
            print(f"✅ 已删除独立浏览器数据: {info['data_dir']}")
        except Exception as e:
            print(f"❌ 删除失败: {e}")
    else:
        print("❌ 取消重置")

def open_browser_data_dir():
    """打开浏览器数据目录"""
    info = get_isolated_browser_info()

    if not os.path.exists(info['data_dir']):
        print("🔍 独立浏览器尚未初始化")
        return

    try:
        if sys.platform == "win32":
            os.startfile(info['data_dir'])
        elif sys.platform == "darwin":
            os.system(f"open '{info['data_dir']}'")
        else:
            os.system(f"xdg-open '{info['data_dir']}'")
        print(f"📁 已打开数据目录: {info['data_dir']}")
    except Exception as e:
        print(f"❌ 打开目录失败: {e}")

def backup_browser_data():
    """备份浏览器数据"""
    info = get_isolated_browser_info()

    if not info['is_initialized']:
        print("🔍 独立浏览器尚未初始化，没有数据可备份")
        return

    backup_dir = os.path.join(os.getcwd(), "joinquant_browser_backup")
    timestamp = backup_dir + "_" + str(int(os.time()))

    try:
        shutil.copytree(info['data_dir'], timestamp)
        print(f"✅ 已备份数据到: {timestamp}")
    except Exception as e:
        print(f"❌ 备份失败: {e}")

def restore_browser_data():
    """恢复浏览器数据"""
    import glob

    backup_pattern = os.path.join(os.getcwd(), "joinquant_browser_backup_*")
    backup_dirs = glob.glob(backup_pattern)

    if not backup_dirs:
        print("🔍 未找到备份数据")
        return

    print("📋 找到的备份数据:")
    for i, backup_dir in enumerate(backup_dirs, 1):
        timestamp = backup_dir.split('_')[-1]
        print(f"  {i}. {backup_dir} (时间戳: {timestamp})")

    try:
        choice = int(input("选择要恢复的备份编号: ")) - 1
        if 0 <= choice < len(backup_dirs):
            selected_backup = backup_dirs[choice]

            # 先删除现有数据
            info = get_isolated_browser_info()
            if info['is_initialized']:
                shutil.rmtree(info['data_dir'])

            # 恢复备份数据
            shutil.copytree(selected_backup, info['data_dir'])
            print(f"✅ 已从 {selected_backup} 恢复数据")
        else:
            print("❌ 无效选择")
    except (ValueError, IndexError):
        print("❌ 无效输入")
    except Exception as e:
        print(f"❌ 恢复失败: {e}")

def clean_browser_data():
    """清理浏览器缓存等临时文件"""
    info = get_isolated_browser_info()

    if not info['is_initialized']:
        print("🔍 独立浏览器尚未初始化")
        return

    patterns_to_clean = [
        os.path.join(info['data_dir'], "**", "Cache"),
        os.path.join(info['data_dir'], "**", "GPUCache"),
        os.path.join(info['data_dir'], "**", "Code Cache"),
        os.path.join(info['data_dir'], "**", "Temp"),
    ]

    cleaned_size = 0
    for pattern in patterns_to_clean:
        import glob
        for path in glob.glob(pattern, recursive=True):
            try:
                if os.path.isdir(path):
                    size = sum(os.path.getsize(os.path.join(dirpath, filename))
                             for dirpath, dirnames, filenames in os.walk(path)
                             for filename in filenames)
                    shutil.rmtree(path)
                    cleaned_size += size
                    print(f"🧹 已清理: {path}")
            except Exception as e:
                print(f"⚠️  清理失败 {path}: {e}")

    if cleaned_size > 0:
        print(f"✅ 清理完成，释放空间: {cleaned_size / 1024 / 1024:.2f} MB")
    else:
        print("📝 没有找到可清理的文件")

def main():
    print("="*60)
    print("🔒 独立浏览器管理工具")
    print("="*60)

    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python browser_manager.py <command>")
        print("\n命令:")
        print("  info    - 显示浏览器信息")
        print("  reset   - 重置浏览器数据")
        print("  open    - 打开数据目录")
        print("  backup  - 备份浏览器数据")
        print("  restore - 恢复浏览器数据")
        print("  clean   - 清理缓存和临时文件")
        print("\n示例:")
        print("  python browser_manager.py info")
        print("  python browser_manager.py reset")
        return

    command = sys.argv[1].lower()

    if command == "info":
        show_browser_info()
    elif command == "reset":
        reset_browser()
    elif command == "open":
        open_browser_data_dir()
    elif command == "backup":
        backup_browser_data()
    elif command == "restore":
        restore_browser_data()
    elif command == "clean":
        clean_browser_data()
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()