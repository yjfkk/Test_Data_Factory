"""
核心接口定义
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class WidgetType(Enum):
    """控件类型枚举"""
    INPUT = "input"
    SELECT = "select"
    TEXTAREA = "textarea"
    NUMBER = "number"
    DATE = "date"
    CHECKBOX = "checkbox"
    PARAGRAPH = "paragraph"


class ResultStatus(Enum):
    """结果状态"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


@dataclass
class SelectOption:
    """选择项配置"""
    display_name: str
    value: str
    disabled: bool = False


@dataclass
class ValidationRule:
    """验证规则"""
    required: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None


@dataclass
class Widget:
    """控件定义"""
    name: str                                    # 控件名称(JSON key)
    label: str                                   # 显示标签
    widget_type: WidgetType                      # 控件类型
    placeholder: str = ""                        # 占位符
    default_value: str = ""                      # 默认值
    help_text: str = ""                          # 帮助文本
    options: List[SelectOption] = field(default_factory=list)  # 选择项
    validation: ValidationRule = field(default_factory=ValidationRule)  # 验证规则


@dataclass
class Module:
    """模块定义"""
    handler_class: type                          # 处理器类
    group_name: str = ""                         # 业务组名
    module_name: str = ""                        # 模块名称
    description: str = ""                        # 模块描述
    widgets: List[Widget] = field(default_factory=list)  # 控件列表
    action_space: str = ""                       # HTTP服务命名空间
    action_name: str = ""                        # HTTP服务动作名
    help_msg: str = ""                           # 帮助信息
    author: str = ""                             # 作者
    version: str = "1.0.0"                       # 版本号


@dataclass
class ExecutionContext:
    """执行上下文"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    client_ip: Optional[str] = None


@dataclass
class Result:
    """执行结果"""
    status: ResultStatus
    data: Any = None
    message: str = ""
    error_code: Optional[str] = None
    execution_time: Optional[float] = None


class Register(ABC):
    """注册接口"""
    
    @abstractmethod
    def register(self) -> Module:
        """注册数据工厂服务"""
        pass


class Handler(ABC):
    """业务处理器接口"""
    
    @abstractmethod
    def handle(self, data: Dict[str, Any], context: ExecutionContext = None) -> Result:
        """处理业务逻辑"""
        pass
