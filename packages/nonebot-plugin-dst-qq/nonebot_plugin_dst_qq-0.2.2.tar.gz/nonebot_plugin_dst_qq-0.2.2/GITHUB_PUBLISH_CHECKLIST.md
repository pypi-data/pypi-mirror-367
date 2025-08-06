# GitHub 发布检查清单

## 发布前检查

### ✅ 代码质量
- [ ] 代码已通过 linting 检查
- [ ] 代码已通过类型检查
- [ ] 代码已格式化（black + isort）
- [ ] 所有测试通过

### ✅ 文档完整性
- [ ] README.md 内容完整且准确
- [ ] 插件元数据填写正确
- [ ] 安装说明清晰
- [ ] 配置说明详细
- [ ] 使用示例完整

### ✅ 项目结构
- [ ] 项目名称符合规范（nonebot-plugin-xxx）
- [ ] 模块名称符合规范（nonebot_plugin_xxx）
- [ ] 插件元数据正确填写
- [ ] 依赖项正确配置

### ✅ 发布准备
- [ ] 版本号已更新
- [ ] CHANGELOG.md 已更新
- [ ] 标签已创建
- [ ] 发布说明已准备

## 发布步骤

### 1. 本地测试
```bash
# 安装开发依赖
pip install -e .[dev]

# 运行测试
pytest

# 检查代码质量
black --check .
isort --check-only .
flake8 .
mypy .
```

### 2. 构建包
```bash
# 使用 hatchling 构建
python -m build

# 或使用 setuptools 构建
python setup.py sdist bdist_wheel
```

### 3. 测试构建的包
```bash
# 安装构建的包进行测试
pip install dist/nonebot-plugin-dst-qq-*.whl
```

### 4. 发布到 PyPI
```bash
# 使用 twine 发布
twine upload dist/*
```

### 5. 创建 GitHub Release
- 创建新的 Release
- 上传构建的文件
- 填写发布说明
- 添加 CHANGELOG 内容

## 发布后检查

### ✅ 验证发布
- [ ] PyPI 页面显示正确
- [ ] 包可以正常安装
- [ ] 插件可以正常加载
- [ ] 功能测试通过

### ✅ 文档更新
- [ ] 更新版本号
- [ ] 更新安装说明
- [ ] 更新使用示例

## 常见问题

### 发布失败
- 检查版本号是否已存在
- 检查包名是否正确
- 检查认证信息是否正确

### 安装失败
- 检查依赖项配置
- 检查 Python 版本要求
- 检查包结构是否正确

### 插件加载失败
- 检查插件元数据
- 检查导入路径
- 检查配置文件 