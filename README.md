# 聚宽策略自动化脚本

使用独立浏览器实例自动化运行聚宽策略并获取错误信息。

## 文件说明

- `login_save.py` - 首次登录并保存认证状态
- `access_algorithm.py` - 运行策略并获取错误信息
- `browser_utils.py` - 浏览器工具模块
- `browser_manager.py` - 浏览器管理工具
- `strategy_example.py` - 示例策略文件
- `requirements.txt` - 依赖包列表

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 首次登录
```bash
python login_save.py
```
- 打开聚宽网站
- 手动完成登录
- 在控制台输入'y'保存登录状态

### 2. 运行策略
```bash
python access_algorithm.py your_strategy.py
```
- 粘贴策略代码到编辑器
- 点击编译运行
- 等待20秒后获取错误信息
- 自动关闭浏览器

### 3. 浏览器管理
```bash
# 查看浏览器信息
python browser_manager.py info

# 重置浏览器数据
python browser_manager.py reset

# 备份/恢复数据
python browser_manager.py backup
python browser_manager.py restore
```

## 特点

- 🔒 **独立浏览器** - 使用专用数据目录，不影响日常浏览器
- 🌐 **用户Chrome** - 自动检测并使用您自己的Chrome浏览器
- ⚡ **快速运行** - 跳过不必要提示操作
- 🎯 **精确错误** - 只提取错误信息，不包含无关内容
- 🔄 **完全自动化** - 运行后自动关闭浏览器

## 数据目录

浏览器数据保存在 `~/.jq-run/joinquant_browser_data/` 目录，包含：
- 登录状态和Cookie
- 浏览历史和设置
- 专用配置文件

