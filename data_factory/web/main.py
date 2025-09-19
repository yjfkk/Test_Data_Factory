"""
FastAPI主应用
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import os
from pathlib import Path

from ..core.plugin_manager import PluginManager
from ..core.interfaces import ExecutionContext

# 创建FastAPI应用
app = FastAPI(
    title="Python数据工厂",
    description="基于插件化架构的测试数据生成平台",
    version="0.1.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局插件管理器
plugin_manager = PluginManager("examples/plugins")

# 挂载静态文件
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.on_event("startup")
async def startup_event():
    """应用启动时扫描插件"""
    modules = plugin_manager.scan_plugins()
    print(f"🚀 数据工厂启动成功，加载了 {len(modules)} 个插件模块")
    for module in modules:
        print(f"  - {module.group_name}/{module.module_name} (作者: {module.author})")


@app.get("/", response_class=HTMLResponse)
async def index():
    """首页"""
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python数据工厂</title>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/element-plus/dist/index.css">
    <script src="https://unpkg.com/element-plus/dist/index.full.js"></script>
    <style>
        body { margin: 0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
        .header { background: #409EFF; color: white; padding: 20px; text-align: center; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .module-card { margin-bottom: 20px; }
        .form-container { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .result-container { margin-top: 20px; }
        .success-result { color: #67c23a; }
        .error-result { color: #f56c6c; }
        pre { background: #f5f7fa; padding: 15px; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <div id="app">
        <div class="header">
            <h1>🏭 Python数据工厂</h1>
            <p>基于插件化架构的测试数据生成平台</p>
        </div>
        
        <div class="container">
            <el-row :gutter="20">
                <el-col :span="8">
                    <el-card class="module-list">
                        <template #header>
                            <span>📋 可用模块</span>
                        </template>
                        <el-menu @select="selectModule" v-if="modules.length > 0">
                            <el-menu-item 
                                v-for="module in modules" 
                                :key="module.id"
                                :index="module.id"
                            >
                                <span>{{ module.group_name }}/{{ module.module_name }}</span>
                            </el-menu-item>
                        </el-menu>
                        <el-empty v-else description="暂无可用模块" />
                    </el-card>
                </el-col>
                
                <el-col :span="16">
                    <el-card v-if="selectedModule" class="form-container">
                        <template #header>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span>{{ selectedModule.group_name }}/{{ selectedModule.module_name }}</span>
                                <el-tag>{{ selectedModule.author || '未知作者' }}</el-tag>
                            </div>
                        </template>
                        
                        <p v-if="selectedModule.description">{{ selectedModule.description }}</p>
                        
                        <el-form :model="formData" label-width="120px" @submit.prevent="executeModule">
                            <el-form-item 
                                v-for="widget in selectedModule.widgets"
                                :key="widget.name"
                                :label="widget.label"
                            >
                                <!-- 输入框 -->
                                <el-input 
                                    v-if="widget.widget_type === 'input'"
                                    v-model="formData[widget.name]"
                                    :placeholder="widget.placeholder"
                                />
                                
                                <!-- 选择框 -->
                                <el-select 
                                    v-else-if="widget.widget_type === 'select'"
                                    v-model="formData[widget.name]"
                                    :placeholder="widget.placeholder || '请选择'"
                                    style="width: 100%"
                                >
                                    <el-option
                                        v-for="option in widget.options"
                                        :key="option.value"
                                        :label="option.display_name"
                                        :value="option.value"
                                    />
                                </el-select>
                                
                                <!-- 文本域 -->
                                <el-input
                                    v-else-if="widget.widget_type === 'textarea'"
                                    v-model="formData[widget.name]"
                                    type="textarea"
                                    :placeholder="widget.placeholder"
                                    :rows="4"
                                />
                                
                                <!-- 数字输入 -->
                                <el-input-number
                                    v-else-if="widget.widget_type === 'number'"
                                    v-model="formData[widget.name]"
                                    :placeholder="widget.placeholder"
                                    style="width: 100%"
                                />
                            </el-form-item>
                            
                            <el-form-item>
                                <el-button type="primary" @click="executeModule" :loading="loading">
                                    🚀 执行
                                </el-button>
                                <el-button @click="resetForm">重置</el-button>
                            </el-form-item>
                        </el-form>
                        
                        <!-- 执行结果 -->
                        <div v-if="result" class="result-container">
                            <el-card>
                                <template #header>
                                    <span>📊 执行结果</span>
                                </template>
                                <div v-if="result.status === 'success'" class="success-result">
                                    <p><strong>✅ 执行成功</strong></p>
                                    <pre>{{ formatResult(result.data) }}</pre>
                                    <p v-if="result.execution_time">
                                        ⏱️ 执行耗时: {{ result.execution_time.toFixed(3) }}秒
                                    </p>
                                </div>
                                <div v-else class="error-result">
                                    <p><strong>❌ 执行失败</strong></p>
                                    <pre>{{ result.message }}</pre>
                                </div>
                            </el-card>
                        </div>
                    </el-card>
                    
                    <el-card v-else>
                        <el-empty description="请选择一个模块开始使用" />
                    </el-card>
                </el-col>
            </el-row>
        </div>
    </div>

    <script>
        const { createApp } = Vue;
        const ElementPlus = window.ElementPlus;

        createApp({
            data() {
                return {
                    modules: [],
                    selectedModule: null,
                    formData: {},
                    result: null,
                    loading: false
                }
            },
            async mounted() {
                await this.loadModules();
            },
            methods: {
                async loadModules() {
                    try {
                        const response = await fetch('/api/modules');
                        this.modules = await response.json();
                    } catch (error) {
                        this.$message.error('加载模块列表失败');
                        console.error(error);
                    }
                },
                selectModule(moduleId) {
                    this.selectedModule = this.modules.find(m => m.id === moduleId);
                    this.initFormData();
                    this.result = null;
                },
                initFormData() {
                    this.formData = {};
                    if (this.selectedModule) {
                        this.selectedModule.widgets.forEach(widget => {
                            this.formData[widget.name] = widget.default_value || '';
                        });
                    }
                },
                async executeModule() {
                    if (!this.selectedModule) return;
                    
                    this.loading = true;
                    try {
                        const response = await fetch(`/api/modules/${this.selectedModule.id}/execute`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(this.formData)
                        });
                        
                        this.result = await response.json();
                        
                        if (this.result.status === 'success') {
                            this.$message.success('执行成功');
                        } else {
                            this.$message.error('执行失败');
                        }
                    } catch (error) {
                        this.$message.error('执行失败');
                        console.error(error);
                    } finally {
                        this.loading = false;
                    }
                },
                resetForm() {
                    this.initFormData();
                    this.result = null;
                },
                formatResult(data) {
                    if (typeof data === 'string') {
                        try {
                            return JSON.stringify(JSON.parse(data), null, 2);
                        } catch {
                            return data;
                        }
                    }
                    return JSON.stringify(data, null, 2);
                }
            }
        }).use(ElementPlus).mount('#app');
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/modules")
async def list_modules() -> List[Dict[str, Any]]:
    """获取模块列表"""
    return plugin_manager.list_modules()


@app.get("/api/modules/{module_id}")
async def get_module(module_id: str) -> Dict[str, Any]:
    """获取模块详情"""
    modules = plugin_manager.list_modules()
    module = next((m for m in modules if m["id"] == module_id), None)
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    return module


@app.post("/api/modules/{module_id}/execute")
async def execute_module(module_id: str, data: Dict[str, Any], request: Request) -> Dict[str, Any]:
    """执行模块"""
    # 创建执行上下文
    context = ExecutionContext(
        client_ip=request.client.host,
        request_id=request.headers.get("x-request-id")
    )
    
    # 直接执行模块（绕过子进程）
    module = plugin_manager.get_module(module_id)
    if not module:
        return {
            "status": "error",
            "data": None,
            "message": f"模块不存在: {module_id}",
            "error_code": "MODULE_NOT_FOUND",
            "execution_time": None
        }
    
    try:
        import time
        start_time = time.time()
        
        # 直接实例化处理器
        handler = module.handler_class()
        result = handler.handle(data, context)
        
        execution_time = time.time() - start_time
        
        return {
            "status": result.status.value,
            "data": result.data,
            "message": result.message,
            "error_code": result.error_code,
            "execution_time": execution_time
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "data": None,
            "message": f"执行失败: {str(e)}",
            "error_code": "EXECUTION_ERROR",
            "execution_time": None,
            "traceback": traceback.format_exc()
        }


@app.api_route("/dmm/{action_space}/{action_name}", methods=["GET", "POST"])
async def http_service(action_space: str, action_name: str, request: Request):
    """HTTP服务接口"""
    # 查找对应的模块
    modules = plugin_manager.list_modules()
    target_module = None
    
    for module_data in modules:
        module = plugin_manager.get_module(module_data["id"])
        if module and module.action_space == action_space and module.action_name == action_name:
            target_module = module_data
            break
    
    if not target_module:
        raise HTTPException(status_code=404, detail="服务不存在")
    
    # 获取请求数据
    if request.method == "POST":
        try:
            data = await request.json()
        except:
            data = {}
    else:
        data = dict(request.query_params)
    
    # 直接执行模块（绕过子进程）
    context = ExecutionContext(
        client_ip=request.client.host,
        request_id=request.headers.get("x-request-id")
    )
    
    module = plugin_manager.get_module(target_module["id"])
    if not module:
        raise HTTPException(status_code=500, detail="模块加载失败")
    
    try:
        import time
        start_time = time.time()
        
        # 直接实例化处理器
        handler = module.handler_class()
        result = handler.handle(data, context)
        
        execution_time = time.time() - start_time
        
        return {
            "status": result.status.value,
            "data": result.data,
            "message": result.message,
            "execution_time": execution_time
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "data": None,
            "message": f"执行失败: {str(e)}",
            "execution_time": None,
            "traceback": traceback.format_exc()
        }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "modules": len(plugin_manager.modules)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
