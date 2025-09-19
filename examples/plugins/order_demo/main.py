"""
订单演示插件 - 展示订单数据生成功能
"""
import json
import random
import time
from typing import Dict, Any
from decimal import Decimal

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


class OrderDemoRegister(Register):
    """订单演示注册器"""
    
    def register(self) -> Module:
        widgets = [
            Widget(
                name="user_id",
                label="用户ID",
                widget_type=WidgetType.INPUT,
                placeholder="请输入用户ID",
                default_value="user_12345",
                help_text="订单所属用户的ID",
                validation=ValidationRule(required=True)
            ),
            Widget(
                name="order_type",
                label="订单类型",
                widget_type=WidgetType.SELECT,
                options=[
                    SelectOption(display_name="普通订单", value="normal"),
                    SelectOption(display_name="预售订单", value="presale"),
                    SelectOption(display_name="秒杀订单", value="seckill"),
                    SelectOption(display_name="团购订单", value="group")
                ],
                default_value="normal",
                help_text="订单的业务类型"
            ),
            Widget(
                name="product_count",
                label="商品数量",
                widget_type=WidgetType.NUMBER,
                placeholder="订单中的商品种类数量",
                default_value="3",
                help_text="订单包含的商品种类数量",
                validation=ValidationRule(
                    required=True,
                    min_value=1,
                    max_value=20
                )
            ),
            Widget(
                name="min_amount",
                label="最小金额",
                widget_type=WidgetType.NUMBER,
                placeholder="订单最小金额",
                default_value="50",
                help_text="生成订单的最小金额（元）",
                validation=ValidationRule(
                    required=True,
                    min_value=0.01
                )
            ),
            Widget(
                name="max_amount",
                label="最大金额",
                widget_type=WidgetType.NUMBER,
                placeholder="订单最大金额",
                default_value="1000",
                help_text="生成订单的最大金额（元）",
                validation=ValidationRule(
                    required=True,
                    min_value=0.01
                )
            ),
            Widget(
                name="status",
                label="订单状态",
                widget_type=WidgetType.SELECT,
                options=[
                    SelectOption(display_name="待付款", value="pending"),
                    SelectOption(display_name="已付款", value="paid"),
                    SelectOption(display_name="已发货", value="shipped"),
                    SelectOption(display_name="已完成", value="completed"),
                    SelectOption(display_name="已取消", value="cancelled")
                ],
                default_value="paid",
                help_text="订单当前状态"
            ),
            Widget(
                name="generate_count",
                label="生成数量",
                widget_type=WidgetType.NUMBER,
                placeholder="要生成的订单数量",
                default_value="5",
                help_text="要生成的订单数据条数",
                validation=ValidationRule(
                    required=True,
                    min_value=1,
                    max_value=50
                )
            )
        ]
        
        return Module(
            handler_class=OrderDemoHandler,
            group_name="订单管理",
            module_name="订单数据生成器",
            description="生成测试订单数据，包含商品信息、价格、状态等完整订单信息",
            widgets=widgets,
            action_space="order",
            action_name="generate",
            help_msg="订单数据生成器可以创建包含完整商品信息的订单数据，支持不同订单类型和状态。",
            author="数据工厂团队",
            version="1.0.0"
        )


class OrderDemoHandler(Handler):
    """订单演示处理器"""
    
    def __init__(self):
        # 预定义商品数据
        self.products = [
            {"name": "iPhone 15 Pro", "category": "电子产品", "price": 8999.00},
            {"name": "MacBook Air", "category": "电子产品", "price": 7999.00},
            {"name": "AirPods Pro", "category": "电子产品", "price": 1899.00},
            {"name": "Nike Air Max", "category": "运动鞋", "price": 899.00},
            {"name": "Adidas 三叶草", "category": "运动鞋", "price": 699.00},
            {"name": "优衣库T恤", "category": "服装", "price": 99.00},
            {"name": "ZARA外套", "category": "服装", "price": 299.00},
            {"name": "星巴克咖啡豆", "category": "食品", "price": 128.00},
            {"name": "农夫山泉", "category": "饮品", "price": 2.50},
            {"name": "小米电视", "category": "家电", "price": 2999.00},
            {"name": "海尔冰箱", "category": "家电", "price": 3499.00},
            {"name": "戴森吸尘器", "category": "家电", "price": 2199.00}
        ]
    
    def handle(self, data: Dict[str, Any], context: ExecutionContext = None) -> Result:
        try:
            # 获取输入参数
            user_id = data.get("user_id", "").strip()
            order_type = data.get("order_type", "normal")
            product_count = int(data.get("product_count", 3))
            min_amount = float(data.get("min_amount", 50))
            max_amount = float(data.get("max_amount", 1000))
            status = data.get("status", "paid")
            generate_count = int(data.get("generate_count", 1))
            
            # 验证参数
            if not user_id:
                return Result(
                    status=ResultStatus.ERROR,
                    message="用户ID不能为空"
                )
            
            if min_amount >= max_amount:
                return Result(
                    status=ResultStatus.ERROR,
                    message="最小金额必须小于最大金额"
                )
            
            # 生成订单数据
            orders = []
            for i in range(generate_count):
                order_data = self._generate_order_data(
                    user_id, order_type, product_count, 
                    min_amount, max_amount, status, i
                )
                orders.append(order_data)
            
            # 构造结果
            if generate_count == 1:
                result_data = orders[0]
                message = f"成功生成订单: {result_data['order_no']}"
            else:
                total_amount = sum(order['total_amount'] for order in orders)
                result_data = {
                    "orders": orders,
                    "total_count": len(orders),
                    "summary": {
                        "total_amount": round(total_amount, 2),
                        "avg_amount": round(total_amount / len(orders), 2),
                        "order_types": self._count_by_field(orders, 'order_type'),
                        "status_distribution": self._count_by_field(orders, 'status')
                    }
                }
                message = f"成功生成 {len(orders)} 个订单，总金额 ¥{total_amount:.2f}"
            
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
    
    def _generate_order_data(self, user_id: str, order_type: str, product_count: int,
                           min_amount: float, max_amount: float, status: str, index: int) -> Dict[str, Any]:
        """生成单个订单数据"""
        
        # 生成订单号
        order_no = f"ORD{int(time.time())}{index:03d}"
        
        # 随机选择商品
        selected_products = random.sample(self.products, min(product_count, len(self.products)))
        
        # 生成订单商品
        order_items = []
        subtotal = 0
        
        for i, product in enumerate(selected_products):
            quantity = random.randint(1, 5)
            unit_price = product["price"]
            item_total = unit_price * quantity
            subtotal += item_total
            
            order_items.append({
                "item_id": f"item_{i + 1}",
                "product_name": product["name"],
                "category": product["category"],
                "unit_price": unit_price,
                "quantity": quantity,
                "total_price": item_total
            })
        
        # 调整总金额到指定范围
        if subtotal < min_amount:
            # 如果金额太小，增加商品数量
            adjustment_ratio = min_amount / subtotal
            for item in order_items:
                item["quantity"] = int(item["quantity"] * adjustment_ratio) + 1
                item["total_price"] = item["unit_price"] * item["quantity"]
        elif subtotal > max_amount:
            # 如果金额太大，减少商品数量
            adjustment_ratio = max_amount / subtotal
            for item in order_items:
                item["quantity"] = max(1, int(item["quantity"] * adjustment_ratio))
                item["total_price"] = item["unit_price"] * item["quantity"]
        
        # 重新计算总金额
        subtotal = sum(item["total_price"] for item in order_items)
        
        # 计算优惠和运费
        discount = round(subtotal * random.uniform(0, 0.1), 2)  # 0-10%优惠
        shipping_fee = 0 if subtotal > 99 else 10  # 满99包邮
        total_amount = subtotal - discount + shipping_fee
        
        # 生成订单数据
        order_data = {
            "order_no": order_no,
            "user_id": user_id,
            "order_type": order_type,
            "status": status,
            "items": order_items,
            "subtotal": round(subtotal, 2),
            "discount": discount,
            "shipping_fee": shipping_fee,
            "total_amount": round(total_amount, 2),
            "payment_method": random.choice(["alipay", "wechat", "card", "balance"]),
            "shipping_address": self._generate_address(),
            "created_at": int(time.time()) - random.randint(0, 86400 * 30),  # 最近30天内
            "updated_at": int(time.time()),
            "remark": f"订单备注信息 - {order_type}订单"
        }
        
        return order_data
    
    def _generate_address(self) -> Dict[str, str]:
        """生成收货地址"""
        provinces = ["北京市", "上海市", "广东省", "江苏省", "浙江省", "山东省"]
        cities = ["北京市", "上海市", "广州市", "深圳市", "杭州市", "南京市"]
        districts = ["朝阳区", "海淀区", "天河区", "福田区", "西湖区", "玄武区"]
        
        return {
            "province": random.choice(provinces),
            "city": random.choice(cities),
            "district": random.choice(districts),
            "detail": f"{random.choice(['中山路', '人民路', '建设路'])}{random.randint(1, 999)}号",
            "receiver": f"收货人{random.randint(1, 999)}",
            "phone": self._generate_phone()
        }
    
    def _generate_phone(self) -> str:
        """生成随机手机号"""
        prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139']
        prefix = random.choice(prefixes)
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return f"{prefix}{suffix}"
    
    def _count_by_field(self, orders: list, field: str) -> Dict[str, int]:
        """统计字段值分布"""
        counts = {}
        for order in orders:
            value = order.get(field, 'unknown')
            counts[value] = counts.get(value, 0) + 1
        return counts
