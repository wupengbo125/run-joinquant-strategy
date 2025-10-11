#!/usr/bin/env python3
"""
路径配置模块：统一管理 ~/.jq-run 目录下的所有路径
"""

import os

def get_jq_run_dir():
    """获取 ~/.jq-run 目录路径"""
    return os.path.expanduser("~/.jq-run")

def get_auth_state_file():
    """获取认证状态文件路径"""
    return os.path.join(get_jq_run_dir(), "auth_state.json")

def get_browser_data_dir():
    """获取浏览器数据目录路径"""
    return os.path.join(get_jq_run_dir(), "browser_data")

def get_browser_backup_dir():
    """获取浏览器备份目录路径"""
    return os.path.join(get_jq_run_dir(), "backups")

def ensure_jq_run_dirs():
    """确保所有必要的目录存在"""
    dirs = [
        get_jq_run_dir(),
        get_browser_data_dir(),
        get_browser_backup_dir()
    ]

    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

    # 浏览器数据子目录
    browser_subdirs = ["Default", "Extensions", "Policy"]
    for subdir in browser_subdirs:
        os.makedirs(os.path.join(get_browser_data_dir(), subdir), exist_ok=True)

    return dirs

def print_jq_run_info():
    """打印 ~/.jq-run 目录信息"""
    jq_run_dir = get_jq_run_dir()
    auth_file = get_auth_state_file()
    browser_dir = get_browser_data_dir()
    backup_dir = get_browser_backup_dir()

    print("\n" + "="*60)
    print("🏠 JoinQuant 运行环境目录信息")
    print("="*60)
    print(f"📁 主目录: {jq_run_dir}")
    print(f"🔐 认证文件: {auth_file}")
    print(f"🌐 浏览器数据: {browser_dir}")
    print(f"💾 备份目录: {backup_dir}")

    print(f"\n📊 状态:")
    print(f"  📁 主目录存在: {'是' if os.path.exists(jq_run_dir) else '否'}")
    print(f"  🔐 认证文件存在: {'是' if os.path.exists(auth_file) else '否'}")
    print(f"  🌐 浏览器数据存在: {'是' if os.path.exists(browser_dir) else '否'}")
    print(f"  💾 备份目录存在: {'是' if os.path.exists(backup_dir) else '否'}")

    print("\n✨ 特点:")
    print("  ✅ 集中管理所有配置和数据")
    print("  ✅ 与项目代码完全分离")
    print("  ✅ 不会污染用户主目录")
    print("  ✅ 便于备份和迁移")

    print("\n🧹 如果需要重置:")
    print(f"  rm -rf {jq_run_dir}")

    print("="*60)

def migrate_from_current_dir():
    """从当前目录迁移数据到 ~/.jq-run"""
    current_auth_file = "auth_state.json"
    current_browser_dir = "joinquant_browser_data"

    migrated = False

    # 迁移认证文件
    if os.path.exists(current_auth_file):
        try:
            import shutil
            ensure_jq_run_dirs()
            shutil.move(current_auth_file, get_auth_state_file())
            print(f"✅ 已迁移认证文件: {current_auth_file} -> {get_auth_state_file()}")
            migrated = True
        except Exception as e:
            print(f"❌ 迁移认证文件失败: {e}")

    # 迁移浏览器数据
    if os.path.exists(current_browser_dir):
        try:
            import shutil
            ensure_jq_run_dirs()
            shutil.move(current_browser_dir, get_browser_data_dir())
            print(f"✅ 已迁移浏览器数据: {current_browser_dir} -> {get_browser_data_dir()}")
            migrated = True
        except Exception as e:
            print(f"❌ 迁移浏览器数据失败: {e}")

    if not migrated:
        print("📝 没有找到需要迁移的数据")

    return migrated