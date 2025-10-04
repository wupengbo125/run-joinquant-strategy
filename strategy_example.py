# 简单的聚宽策略示例
# 这是一个测试策略，用于验证脚本功能

def initialize(context):
    """初始化函数"""
    g.stock = '000001.XSHE'  # 设置股票代码
    print("策略初始化完成")

def before_trading_start(context):
    """盘前运行函数"""
    print("盘前运行")

def handle_data(context, data):
    """主要交易逻辑"""
    stock = g.stock

    # 获取当前价格
    current_price = data.current(stock, 'price')

    print(f"当前股票价格: {current_price}")

    # 简单的买入逻辑
    if context.portfolio.cash > 1000:
        print("执行买入操作")
        order_target_percent(stock, 0.5)

    print("策略运行完成")

def after_trading_end(context):
    """盘后运行函数"""
    print("盘后运行")

# 全局变量
g = type('G', (), {})()