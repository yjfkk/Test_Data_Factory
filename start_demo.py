#!/usr/bin/env python3
"""
一键启动数据工厂Demo
"""
import os
import sys


def main():
    """启动Demo"""
    print("🚀 启动Python数据工厂Demo...")
    print("=" * 50)
    print()
    print("📋 可用功能:")
    print("  👤 用户数据生成器 - 生成测试用户数据")
    print("  🛒 订单数据生成器 - 生成测试订单数据")
    print()
    print("🌐 访问方式:")
    print("  Web界面: http://localhost:8000")
    print("  API文档: http://localhost:8000/docs")
    print()
    print("🔗 直接API测试:")
    print("  用户生成: POST http://localhost:8000/dmm/user/generate")
    print("  订单生成: POST http://localhost:8000/dmm/order/generate")
    print()
    print("💡 API测试示例:")
    print("  curl -X POST http://localhost:8000/dmm/user/generate \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"name\": \"张三\", \"age\": 25, \"gender\": \"male\"}'")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    
    # 启动服务
    os.system(f"{sys.executable} -m uvicorn data_factory.web.main:app --host 0.0.0.0 --port 8000 --reload")


if __name__ == "__main__":
    main()
