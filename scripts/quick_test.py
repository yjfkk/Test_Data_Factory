#!/usr/bin/env python3
"""
快速测试脚本 - 验证插件和Web服务是否正常工作
"""
import subprocess
import sys
import time
import urllib.request
import json


def test_plugins():
    """测试插件加载"""
    print("🔌 测试插件加载...")
    try:
        from data_factory.core.plugin_manager import PluginManager
        pm = PluginManager()
        modules = pm.scan_plugins()
        
        if modules:
            print(f"✅ 成功加载 {len(modules)} 个插件:")
            for module in modules:
                print(f"   - {module.group_name}/{module.module_name}")
            return True
        else:
            print("❌ 没有找到任何插件")
            return False
    except Exception as e:
        print(f"❌ 插件加载失败: {e}")
        return False


def test_web_service():
    """测试Web服务"""
    print("\n🌐 测试Web服务...")
    
    # 启动服务
    proc = subprocess.Popen([
        sys.executable, '-m', 'uvicorn', 
        'data_factory.web.main:app', 
        '--host', '127.0.0.1', 
        '--port', '8000'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    try:
        # 等待服务启动
        time.sleep(3)
        
        if proc.poll() is None:
            print("✅ Web服务启动成功")
            
            # 测试API
            try:
                with urllib.request.urlopen('http://127.0.0.1:8000/api/modules') as response:
                    modules = json.loads(response.read().decode())
                    
                if modules:
                    print(f"✅ API返回 {len(modules)} 个模块")
                    return True
                else:
                    print("❌ API返回空模块列表")
                    return False
                    
            except Exception as e:
                print(f"❌ API调用失败: {e}")
                return False
        else:
            print("❌ Web服务启动失败")
            return False
            
    finally:
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=2)


def main():
    """主函数"""
    print("🚀 Python数据工厂 - 快速测试")
    print("=" * 40)
    
    # 运行测试
    plugin_ok = test_plugins()
    web_ok = test_web_service()
    
    print("\n" + "=" * 40)
    print("📊 测试结果:")
    print(f"   插件系统: {'✅ 正常' if plugin_ok else '❌ 异常'}")
    print(f"   Web服务:  {'✅ 正常' if web_ok else '❌ 异常'}")
    
    if plugin_ok and web_ok:
        print("\n🎉 所有测试通过！可以启动Demo了")
        print("   运行命令: python scripts/run_demo.py")
        print("   或使用:   make demo")
        return True
    else:
        print("\n⚠️ 存在问题，请检查配置")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
