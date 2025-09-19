
import sys
import json
import time
import traceback
from pathlib import Path

# 添加插件路径
plugin_path = Path(r"plugins/user_demo")
if str(plugin_path) not in sys.path:
    sys.path.insert(0, str(plugin_path))

try:
    start_time = time.time()
    
    # 导入插件模块
    from main import UserDemoHandler
    
    # 创建处理器实例
    handler = UserDemoHandler()
    
    # 解析输入数据
    input_data = {"name": "测试用户", "gender": "male", "age": 25, "email": "test@example.com", "generate_count": 1}
    
    # 执行处理
    result = handler.handle(input_data)
    
    execution_time = time.time() - start_time
    
    # 输出结果
    output = {
        "success": result.status.value == "success",
        "data": result.data,
        "message": result.message,
        "execution_time": execution_time
    }
    
    print(json.dumps(output, ensure_ascii=False))
    
except Exception as e:
    error_output = {
        "success": False,
        "data": None,
        "message": str(e),
        "traceback": traceback.format_exc()
    }
    print(json.dumps(error_output, ensure_ascii=False))
    sys.exit(1)
