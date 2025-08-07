.PHONY: help install test lint format clean build publish docker-build docker-run

# 默认目标
help:
	@echo "可用的命令:"
	@echo "  install     - 安装项目依赖"
	@echo "  test        - 运行测试"
	@echo "  lint        - 代码检查"
	@echo "  format      - 代码格式化"
	@echo "  clean       - 清理构建文件"
	@echo "  build       - 构建包"
	@echo "  publish     - 发布到PyPI"
	@echo "  docker-build - 构建Docker镜像"
	@echo "  docker-run  - 运行Docker容器"

# 安装依赖
install:
	pip install -r requirements.txt
	pip install -e .

# 安装开发依赖
install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 isort mypy
	pip install -e .

# 运行测试
test:
	pytest tests/ -v --cov=docx_image_extractor_mcp --cov-report=html --cov-report=term

# 代码检查
lint:
	flake8 .
	mypy docx_image_extractor_mcp/

# 代码格式化
format:
	black .
	isort .

# 检查代码格式
check-format:
	black --check .
	isort --check-only .

# 清理构建文件
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 构建包
build: clean
	python -m build

# 发布到PyPI
publish: build
	twine upload dist/*

# 发布到测试PyPI
publish-test: build
	twine upload --repository testpypi dist/*

# 构建Docker镜像
docker-build:
	docker build -t docx-image-extractor-mcp .

# 运行Docker容器
docker-run:
	docker run -it --rm -v $(PWD)/extracted_images:/app/extracted_images docx-image-extractor-mcp

# 使用Docker Compose启动服务
docker-up:
	docker-compose up -d

# 停止Docker Compose服务
docker-down:
	docker-compose down

# 查看Docker日志
docker-logs:
	docker-compose logs -f

# 运行所有检查
check: lint test check-format

# 准备发布
prepare-release: check build
	@echo "准备发布完成！"