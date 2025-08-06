# 发布指南

本指南说明如何将 `nonebot-plugin-dst-qq` 发布到 PyPI。

## 准备工作

### 1. 获取 PyPI API 令牌

1. 访问 [PyPI 账户设置](https://pypi.org/manage/account/)
2. 登录您的 PyPI 账户
3. 在 "API tokens" 部分点击 "Add API token"
4. 选择 "Entire account (all projects)" 或 "Specific project"
5. 复制生成的 API 令牌

### 2. 配置认证信息

复制 `.pypirc.example` 为 `.pypirc` 并填入您的 API 令牌：

```bash
cp .pypirc.example .pypirc
```

然后编辑 `.pypirc` 文件，将 `your-pypi-api-token-here` 替换为您的真实 API 令牌。

## 发布步骤

### 1. 更新版本号

在 `pyproject.toml` 中更新版本号：

```toml
[project]
version = "0.2.3"  # 更新为新版本号
```

### 2. 更新更新日志

在 `CHANGELOG.md` 中添加新版本的更新内容。

### 3. 构建包

```bash
python -m build --sdist --wheel
```

### 4. 检查包

```bash
twine check dist/*
```

### 5. 上传到 PyPI

```bash
# 上传到正式 PyPI
twine upload dist/*

# 或者先上传到 TestPyPI 测试
twine upload --repository testpypi dist/*
```

## 验证发布

发布成功后，可以通过以下方式验证：

```bash
# 安装最新版本
pip install nonebot-plugin-dst-qq

# 查看版本信息
pip show nonebot-plugin-dst-qq
```

## 注意事项

- 确保 `.pypirc` 文件已添加到 `.gitignore` 中，避免提交敏感信息
- 每次发布前都要更新版本号
- 建议先在 TestPyPI 上测试，确认无误后再发布到正式 PyPI
- 发布后可以在 [PyPI 项目页面](https://pypi.org/project/nonebot-plugin-dst-qq/) 查看 