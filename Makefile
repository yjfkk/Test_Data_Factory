.PHONY: help install install-dev test test-cov lint format clean run demo docs

# Default target
help:
	@echo "Python数据工厂 - 可用命令:"
	@echo ""
	@echo "  install      - 安装项目依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  test         - 运行测试"
	@echo "  test-cov     - 运行测试并生成覆盖率报告"
	@echo "  lint         - 代码检查"
	@echo "  format       - 代码格式化"
	@echo "  clean        - 清理临时文件"
	@echo "  run          - 启动开发服务器"
	@echo "  demo         - 运行Demo测试"
	@echo "  docs         - 构建文档"

# 安装依赖
install:
	pip install -r requirements.txt

install-dev:
	pip install -e ".[dev]"

# 测试
test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ -v --cov=data_factory --cov-report=html --cov-report=term

# 代码质量
lint:
	flake8 data_factory/ tests/
	mypy data_factory/

format:
	black data_factory/ tests/ scripts/
	isort data_factory/ tests/ scripts/

# 清理
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/

# 运行
run:
	python -m uvicorn data_factory.web.main:app --host 0.0.0.0 --port 8000 --reload

demo:
	python scripts/run_demo.py

# 测试Demo功能
test-demo:
	python scripts/demo_test.py

# 文档
docs:
	@echo "构建文档功能待实现"

# 开发环境设置
setup-dev: install-dev
	pre-commit install

# 构建分发包
build:
	python -m build

# 发布到PyPI
publish: build
	python -m twine upload dist/*

# Docker相关
docker-build:
	docker build -t python-data-factory:latest .

docker-run:
	docker run -p 8000:8000 python-data-factory:latest

# 检查项目健康度
health-check: lint test
	@echo "✅ 项目健康检查通过"
