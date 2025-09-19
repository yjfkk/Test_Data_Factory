# Python数据工厂 - Demo演示

🏭 **Python数据工厂** 是一个基于插件化架构的测试数据生成平台，让测试人员和开发人员能够快速、简单地生成各种测试数据。

## ✨ 核心特性

- 🔌 **插件化架构** - 业务逻辑开发者只需关注业务逻辑，无需编写前端代码
- 🚀 **动态扩展** - 支持热加载插件，无需重启服务
- 🛡️ **安全隔离** - 插件在隔离环境中执行，确保系统安全
- 🎨 **自动UI生成** - 根据插件配置自动生成前端表单界面
- 🌐 **RESTful API** - 提供完整的HTTP API，支持系统集成
- ⚡ **高性能** - 基于FastAPI异步框架，支持高并发

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动演示程序

```bash
python run_demo.py
```

### 3. 访问Web界面

打开浏览器访问: http://localhost:8000

## 📋 演示插件

本Demo包含两个示例插件：

### 👤 用户数据生成器
- **功能**: 生成测试用户数据
- **参数**: 姓名、性别、年龄、邮箱、描述、生成数量
- **输出**: 包含完整用户信息的JSON数据
- **API**: `POST /dmm/user/generate`

### 🛒 订单数据生成器  
- **功能**: 生成测试订单数据
- **参数**: 用户ID、订单类型、商品数量、金额范围、订单状态、生成数量
- **输出**: 包含商品明细的完整订单数据
- **API**: `POST /dmm/order/generate`

## 🏗️ 项目结构

```
Test_Data_Factory/
├── data_factory/           # 核心框架
│   ├── core/              # 核心模块
│   │   ├── interfaces.py  # 核心接口定义
│   │   └── plugin_manager.py # 插件管理器
│   └── web/               # Web服务
│       └── main.py        # FastAPI应用
├── plugins/               # 插件目录
│   ├── user_demo/         # 用户数据生成插件
│   └── order_demo/        # 订单数据生成插件
├── requirements.txt       # 依赖包
├── run_demo.py           # 启动脚本
└── README.md             # 说明文档
```

## 🔌 插件开发

### 1. 创建插件目录

```bash
mkdir plugins/my_plugin
```

### 2. 实现插件代码

创建 `plugins/my_plugin/main.py`:

```python
from data_factory.core.interfaces import Register, Handler, Module, Widget, WidgetType, Result, ResultStatus

class MyPluginRegister(Register):
    def register(self) -> Module:
        widgets = [
            Widget(
                name="input_param",
                label="输入参数",
                widget_type=WidgetType.INPUT,
                placeholder="请输入参数"
            )
        ]
        
        return Module(
            handler_class=MyPluginHandler,
            group_name="我的插件组",
            module_name="我的插件",
            widgets=widgets,
            author="我的名字"
        )

class MyPluginHandler(Handler):
    def handle(self, data, context=None) -> Result:
        # 实现业务逻辑
        return Result(
            status=ResultStatus.SUCCESS,
            data={"result": "处理成功"},
            message="操作完成"
        )
```

### 3. 重启服务加载插件

插件会在服务启动时自动加载。

## 🌐 API使用示例

### 获取模块列表
```bash
curl http://localhost:8000/api/modules
```

### 执行用户生成
```bash
curl -X POST http://localhost:8000/api/modules/user_demo_UserDemoRegister/execute \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "gender": "male", 
    "age": 25,
    "email": "zhangsan@example.com",
    "generate_count": 3
  }'
```

### 使用HTTP服务接口
```bash
curl -X POST http://localhost:8000/dmm/user/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "李四",
    "gender": "female",
    "age": 28
  }'
```

## 🎯 设计理念

Python数据工厂的设计遵循以下原则：

1. **简单易用** - 插件开发者只需关注业务逻辑
2. **安全可靠** - 插件在隔离环境中执行
3. **灵活扩展** - 支持动态加载和卸载插件
4. **高效性能** - 基于异步框架，支持高并发
5. **标准化** - 统一的接口规范和开发模式

## 📊 功能对比

| 特性 | Java版本 | Python版本 |
|------|----------|------------|
| 开发语言 | Java | Python |
| Web框架 | Spring Boot | FastAPI |
| 前端技术 | JSP/Thymeleaf | Vue.js |
| 类型安全 | ✅ | ✅ (类型提示) |
| API文档 | 手动编写 | 自动生成 |
| 开发效率 | 中等 | 高 |
| 部署复杂度 | 中等 | 简单 |
| 生态丰富度 | 高 | 非常高 |

## 🔧 技术栈

- **后端**: Python 3.8+, FastAPI, Pydantic
- **前端**: Vue.js 3, Element Plus
- **部署**: Docker, Kubernetes
- **监控**: Prometheus, Grafana

## 📝 更多文档

- [需求分析文档](requirements.md) - 详细的功能需求和用户场景
- [技术设计文档](technical_design.md) - 完整的技术架构和实现方案

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License
