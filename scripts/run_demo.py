#!/usr/bin/env python3
"""
运行数据工厂演示程序
"""
import os
import sys
import subprocess

def main():
    """启动演示程序"""
    print("🚀 启动Python数据工厂演示程序...")
    print()
    
    # 检查依赖
    print("📦 检查依赖包...")
    try:
        import fastapi
        import uvicorn
        print("✅ 依赖包已安装")
    except ImportError:
        print("❌ 缺少依赖包，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装完成")
    
    print()
    print("🏭 数据工厂功能演示:")
    print("  📋 用户数据生成器 - 生成测试用户数据")
    print("  🛒 订单数据生成器 - 生成测试订单数据")
    print("  📁 插件位置: examples/plugins/")
    print()
    print("🌐 启动Web服务...")
    print("  访问地址: http://localhost:8000")
    print("  API文档: http://localhost:8000/docs")
    print()
    print("💡 使用说明:")
    print("  1. 打开浏览器访问 http://localhost:8000")
    print("  2. 在左侧选择要使用的模块")
    print("  3. 填写表单参数")
    print("  4. 点击'执行'按钮生成数据")
    print()
    print("🔗 HTTP API示例:")
    print("  用户生成: POST http://localhost:8000/dmm/user/generate")
    print("  订单生成: POST http://localhost:8000/dmm/order/generate")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    
    # 启动FastAPI应用
    os.system(f"{sys.executable} -m uvicorn data_factory.web.main:app --host 0.0.0.0 --port 8000 --reload")

if __name__ == "__main__":
    main()
