"""
插件管理器
"""
import os
import sys
import importlib.util
import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .interfaces import Register, Handler, Module, Result, ResultStatus, ExecutionContext


@dataclass
class PluginInfo:
    """插件信息"""
    id: str
    name: str
    path: str
    module: Any
    modules: List[Module]
    loaded_at: float


class SimpleIsolator:
    """简单隔离器 - 使用子进程执行"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def execute(self, plugin_info: PluginInfo, handler_class_name: str, 
                data: Dict[str, Any], context: ExecutionContext = None) -> Result:
        """在隔离环境中执行处理器"""
        
        # 创建执行脚本
        script_content = self._generate_script(plugin_info, handler_class_name, data)
        script_file = self.temp_dir / f"exec_{plugin_info.id}_{int(time.time())}.py"
        
        try:
            script_file.write_text(script_content, encoding='utf-8')
            
            # 执行脚本
            result = subprocess.run(
                [sys.executable, str(script_file)],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=plugin_info.path
            )
            
            if result.returncode == 0:
                try:
                    output_data = json.loads(result.stdout.strip())
                    return Result(
                        status=ResultStatus.SUCCESS if output_data['success'] else ResultStatus.ERROR,
                        data=output_data.get('data'),
                        message=output_data.get('message', ''),
                        execution_time=output_data.get('execution_time')
                    )
                except json.JSONDecodeError:
                    return Result(
                        status=ResultStatus.ERROR,
                        message=f"输出解析失败: {result.stdout}",
                        error_code='OUTPUT_PARSE_ERROR'
                    )
            else:
                return Result(
                    status=ResultStatus.ERROR,
                    message=result.stderr if result.stderr else "执行失败",
                    error_code='EXECUTION_ERROR'
                )
                
        except subprocess.TimeoutExpired:
            return Result(
                status=ResultStatus.ERROR,
                message=f"执行超时 ({self.timeout}秒)",
                error_code='TIMEOUT_ERROR'
            )
        except Exception as e:
            return Result(
                status=ResultStatus.ERROR,
                message=str(e),
                error_code='UNKNOWN_ERROR'
            )
        finally:
            # 清理临时文件
            if script_file.exists():
                script_file.unlink()
    
    def _generate_script(self, plugin_info: PluginInfo, handler_class_name: str, 
                        data: Dict[str, Any]) -> str:
        """生成执行脚本"""
        data_json = json.dumps(data, ensure_ascii=False)
        
        return f'''
import sys
import json
import time
import traceback
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 添加插件路径
plugin_path = Path(r"{plugin_info.path}")
if str(plugin_path) not in sys.path:
    sys.path.insert(0, str(plugin_path))

try:
    start_time = time.time()
    
    # 导入插件模块
    from main import {handler_class_name}
    
    # 创建处理器实例
    handler = {handler_class_name}()
    
    # 解析输入数据
    input_data = {data_json}
    
    # 执行处理
    result = handler.handle(input_data)
    
    execution_time = time.time() - start_time
    
    # 输出结果
    output = {{
        'success': result.status.value == 'success',
        'data': result.data,
        'message': result.message,
        'execution_time': execution_time
    }}
    
    print(json.dumps(output, ensure_ascii=False))
    
except Exception as e:
    error_output = {{
        'success': False,
        'data': None,
        'message': str(e),
        'traceback': traceback.format_exc()
    }}
    print(json.dumps(error_output, ensure_ascii=False))
    sys.exit(1)
'''


class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugins_dir: str = "examples/plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.loaded_plugins: Dict[str, PluginInfo] = {}
        self.modules: Dict[str, Module] = {}  # module_id -> Module
        self.isolator = SimpleIsolator()
        
        # 确保插件目录存在
        self.plugins_dir.mkdir(exist_ok=True)
    
    def scan_plugins(self) -> List[Module]:
        """扫描并加载所有插件"""
        modules = []
        
        if not self.plugins_dir.exists():
            return modules
        
        for plugin_path in self.plugins_dir.iterdir():
            if plugin_path.is_dir() and not plugin_path.name.startswith('.'):
                try:
                    plugin_modules = self._load_plugin(plugin_path)
                    if plugin_modules:
                        modules.extend(plugin_modules)
                except Exception as e:
                    print(f"加载插件失败 {plugin_path.name}: {e}")
        
        return modules
    
    def _load_plugin(self, plugin_path: Path) -> Optional[List[Module]]:
        """加载单个插件"""
        main_file = plugin_path / "main.py"
        if not main_file.exists():
            return None
        
        # 动态导入插件模块
        spec = importlib.util.spec_from_file_location(
            f"plugin_{plugin_path.name}", main_file
        )
        if not spec or not spec.loader:
            return None
        
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        
        # 查找实现Register接口的类
        modules = []
        plugin_info = None
        
        for attr_name in dir(plugin_module):
            attr = getattr(plugin_module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, Register) and 
                attr != Register):
                
                try:
                    register_instance = attr()
                    module = register_instance.register()
                    
                    # 生成模块ID
                    module_id = f"{plugin_path.name}_{attr_name}"
                    
                    # 保存模块信息
                    self.modules[module_id] = module
                    modules.append(module)
                    
                    # 创建插件信息（第一次创建）
                    if not plugin_info:
                        plugin_info = PluginInfo(
                            id=plugin_path.name,
                            name=plugin_path.name,
                            path=str(plugin_path),
                            module=plugin_module,
                            modules=[],
                            loaded_at=time.time()
                        )
                        self.loaded_plugins[plugin_path.name] = plugin_info
                    
                    plugin_info.modules.append(module)
                    
                except Exception as e:
                    print(f"注册模块失败 {attr_name}: {e}")
        
        return modules if modules else None
    
    def get_module(self, module_id: str) -> Optional[Module]:
        """获取模块信息"""
        return self.modules.get(module_id)
    
    def list_modules(self) -> List[Dict[str, Any]]:
        """列出所有模块"""
        result = []
        for module_id, module in self.modules.items():
            result.append({
                "id": module_id,
                "group_name": module.group_name,
                "module_name": module.module_name,
                "description": module.description,
                "author": module.author,
                "version": module.version,
                "widgets": [self._widget_to_dict(w) for w in module.widgets]
            })
        return result
    
    def _widget_to_dict(self, widget) -> Dict[str, Any]:
        """将Widget对象转换为字典"""
        return {
            "name": widget.name,
            "label": widget.label,
            "widget_type": widget.widget_type.value,
            "placeholder": widget.placeholder,
            "default_value": widget.default_value,
            "help_text": widget.help_text,
            "options": [
                {
                    "display_name": opt.display_name,
                    "value": opt.value,
                    "disabled": opt.disabled
                } for opt in widget.options
            ],
            "validation": {
                "required": widget.validation.required,
                "min_length": widget.validation.min_length,
                "max_length": widget.validation.max_length,
                "pattern": widget.validation.pattern,
                "min_value": widget.validation.min_value,
                "max_value": widget.validation.max_value
            }
        }
    
    def execute_module(self, module_id: str, data: Dict[str, Any], 
                      context: ExecutionContext = None) -> Result:
        """执行模块"""
        module = self.modules.get(module_id)
        if not module:
            return Result(
                status=ResultStatus.ERROR,
                message=f"模块不存在: {module_id}",
                error_code="MODULE_NOT_FOUND"
            )
        
        # 找到对应的插件
        plugin_info = None
        for plugin in self.loaded_plugins.values():
            if module in plugin.modules:
                plugin_info = plugin
                break
        
        if not plugin_info:
            return Result(
                status=ResultStatus.ERROR,
                message=f"找不到模块对应的插件: {module_id}",
                error_code="PLUGIN_NOT_FOUND"
            )
        
        # 执行处理器
        handler_class_name = module.handler_class.__name__
        return self.isolator.execute(plugin_info, handler_class_name, data, context)
