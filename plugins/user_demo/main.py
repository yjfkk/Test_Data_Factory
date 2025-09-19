"""
用户演示插件 - 展示如何创建数据工厂插件
"""
import json
import random
import time
from typing import Dict, Any

# 导入数据工厂核心接口
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from data_factory.core.interfaces import (
    Register, Handler, Module, Widget, WidgetType, SelectOption, 
    ValidationRule, Result, ResultStatus, ExecutionContext
)


class UserDemoRegister(Register):
    """用户演示注册器"""
    
    def register(self) -> Module:
        # 定义表单控件
        widgets = [
            Widget(
                name="name",
                label="姓名",
                widget_type=WidgetType.INPUT,
                placeholder="请输入用户姓名",
                default_value="张三",
                help_text="用户的真实姓名",
                validation=ValidationRule(
                    required=True,
                    min_length=2,
                    max_length=20
                )
            ),
            Widget(
                name="gender",
                label="性别",
                widget_type=WidgetType.SELECT,
                options=[
                    SelectOption(display_name="女", value="female"),
                    SelectOption(display_name="男", value="male"),
                    SelectOption(display_name="其他", value="other")
                ],
                default_value="female",
                help_text="用户性别"
            ),
            Widget(
                name="age",
                label="年龄",
                widget_type=WidgetType.NUMBER,
                placeholder="请输入年龄",
                default_value="25",
                help_text="用户年龄（岁）",
                validation=ValidationRule(
                    required=True,
                    min_value=0,
                    max_value=150
                )
            ),
            Widget(
                name="email",
                label="邮箱",
                widget_type=WidgetType.INPUT,
                placeholder="请输入邮箱地址",
                default_value="zhangsan@example.com",
                help_text="用户邮箱地址",
                validation=ValidationRule(
                    pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                )
            ),
            Widget(
                name="description",
                label="个人描述",
                widget_type=WidgetType.TEXTAREA,
                placeholder="请输入个人描述信息",
                default_value="这是一个测试用户",
                help_text="用户的个人描述信息",
                validation=ValidationRule(
                    max_length=500
                )
            ),
            Widget(
                name="generate_count",
                label="生成数量",
                widget_type=WidgetType.NUMBER,
                placeholder="请输入要生成的用户数量",
                default_value="1",
                help_text="要生成的用户数据条数",
                validation=ValidationRule(
                    required=True,
                    min_value=1,
                    max_value=100
                )
            )
        ]
        
        return Module(
            handler_class=UserDemoHandler,
            group_name="用户管理",
            module_name="用户数据生成器",
            description="生成测试用户数据，支持自定义用户属性和批量生成",
            widgets=widgets,
            action_space="user",
            action_name="generate",
            help_msg="这是一个用户数据生成的演示插件，展示了如何使用数据工厂创建测试数据。支持单个和批量生成用户数据。",
            author="数据工厂团队",
            version="1.0.0"
        )


class UserDemoHandler(Handler):
    """用户演示处理器"""
    
    def handle(self, data: Dict[str, Any], context: ExecutionContext = None) -> Result:
        try:
            # 模拟处理时间
            time.sleep(0.1)
            
            # 获取输入参数
            name = data.get("name", "").strip()
            gender = data.get("gender", "female")
            age = data.get("age")
            email = data.get("email", "").strip()
            description = data.get("description", "").strip()
            generate_count = int(data.get("generate_count", 1))
            
            # 验证必填参数
            if not name:
                return Result(
                    status=ResultStatus.ERROR,
                    message="姓名不能为空"
                )
            
            if age is None or age < 0 or age > 150:
                return Result(
                    status=ResultStatus.ERROR,
                    message="年龄必须在0-150之间"
                )
            
            # 生成用户数据
            users = []
            for i in range(generate_count):
                user_data = self._generate_user_data(
                    name, gender, age, email, description, i
                )
                users.append(user_data)
            
            # 构造结果
            if generate_count == 1:
                result_data = users[0]
                message = f"成功生成用户数据: {result_data['name']}"
            else:
                result_data = {
                    "users": users,
                    "total_count": len(users),
                    "summary": {
                        "male_count": len([u for u in users if u['gender'] == 'male']),
                        "female_count": len([u for u in users if u['gender'] == 'female']),
                        "other_count": len([u for u in users if u['gender'] == 'other']),
                        "avg_age": sum(u['age'] for u in users) / len(users)
                    }
                }
                message = f"成功生成 {len(users)} 条用户数据"
            
            return Result(
                status=ResultStatus.SUCCESS,
                data=result_data,
                message=message
            )
            
        except Exception as e:
            return Result(
                status=ResultStatus.ERROR,
                message=f"处理失败: {str(e)}",
                error_code="PROCESSING_ERROR"
            )
    
    def _generate_user_data(self, base_name: str, base_gender: str, base_age: int, 
                           base_email: str, base_description: str, index: int) -> Dict[str, Any]:
        """生成单个用户数据"""
        
        # 姓名变化
        if index == 0:
            name = base_name
        else:
            name = f"{base_name}_{index + 1}"
        
        # 年龄随机变化
        age = max(1, min(150, base_age + random.randint(-5, 5)))
        
        # 邮箱变化
        if base_email and '@' in base_email:
            email_parts = base_email.split('@')
            if index == 0:
                email = base_email
            else:
                email = f"{email_parts[0]}_{index + 1}@{email_parts[1]}"
        else:
            email = f"user_{index + 1}@example.com"
        
        # 生成额外的用户属性
        user_data = {
            "id": f"user_{int(time.time())}_{index}",
            "name": name,
            "gender": base_gender,
            "age": age,
            "email": email,
            "description": base_description,
            "phone": self._generate_phone(),
            "address": self._generate_address(),
            "created_at": int(time.time()),
            "is_active": True,
            "tags": self._generate_tags(base_gender, age)
        }
        
        return user_data
    
    def _generate_phone(self) -> str:
        """生成随机手机号"""
        prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                   '150', '151', '152', '153', '155', '156', '157', '158', '159',
                   '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
        prefix = random.choice(prefixes)
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return f"{prefix}{suffix}"
    
    def _generate_address(self) -> str:
        """生成随机地址"""
        cities = ['北京市', '上海市', '广州市', '深圳市', '杭州市', '南京市', '武汉市', '成都市']
        districts = ['朝阳区', '海淀区', '西城区', '东城区', '丰台区', '石景山区', '通州区', '昌平区']
        streets = ['中山路', '人民路', '解放路', '建设路', '和平路', '友谊路', '光明路', '胜利路']
        
        city = random.choice(cities)
        district = random.choice(districts)
        street = random.choice(streets)
        number = random.randint(1, 999)
        
        return f"{city}{district}{street}{number}号"
    
    def _generate_tags(self, gender: str, age: int) -> list:
        """根据性别和年龄生成标签"""
        tags = []
        
        # 年龄相关标签
        if age < 18:
            tags.append("未成年")
        elif age < 30:
            tags.append("青年")
        elif age < 60:
            tags.append("中年")
        else:
            tags.append("老年")
        
        # 性别相关标签
        if gender == "male":
            tags.append("男性用户")
        elif gender == "female":
            tags.append("女性用户")
        else:
            tags.append("其他性别用户")
        
        # 随机添加一些标签
        optional_tags = ["VIP用户", "活跃用户", "新用户", "老用户", "高价值用户"]
        tags.extend(random.sample(optional_tags, random.randint(1, 3)))
        
        return tags
