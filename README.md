# yuyan

## 产品介绍
御言是一款专为文本内容风控设计的智能解决方案，旨在帮助企业和平台高效管理用户生成内容 (UGC)。通过全面的策略体系、智能算法和灵活配置能力，御言能够精准识别和处理违规、涉政、涉黄等敏感内容，有效保障社区环境的健康与合规。

御言以“掌控语言、守护秩序”为核心理念，不仅提供灵活的文本过滤方案，还能无缝集成多种第三方平台，满足复杂场景下的内容审核需求。

---

## 核心功能

### 1. **名单管理**
- **白名单**：
  允许通过的安全内容，配置灵活可控，确保正常内容不受干扰。
- **忽略名单**：
  对特定的用户或内容进行豁免处理，减少误判率。
- **黑名单**：
  针对已知违规内容的强力过滤，快速响应风险。

### 2. **策略模型**
提供多维度的风控策略，支持以下功能：
- **账号策略**：基于账号历史行为进行筛查。
- **IP策略**：对来源IP进行限制和风险评估。
- **上下文策略**：结合前后文语义分析，提升违规识别准确性。
- **刷屏策略**：检测和限制重复、频繁发布的内容。
- 其他定制化策略，满足多样化场景需求。

### 3. **AI智能检测**
集成先进的AI模型，对用户文本进行实时分析与风险识别，包括但不限于：
- 敏感词检测
- 涉政涉黄内容识别
- 仇恨言论、欺诈信息等行为的智能判断

### 4. **配置选项**
所有模块均支持启用/关闭配置，灵活适配不同业务场景需求。

---

## 适用场景
- 应用内用户互动内容的合规审核
- 社区论坛、社交媒体的文本过滤
- 实时聊天应用中的敏感内容监控
- 电商平台评论区、用户反馈的违规内容识别

御言不仅是一个风控工具，更是一位“文字的守护者”，助您打造安全、健康的数字空间。

## 启动

1. 安装依赖：

```
pip install -r yuyan/requirements.txt
```

2. 启动服务（开发）：

```
uvicorn app.main:app --host 0.0.0.0 --port 22560
```

3. 启动服务（生产）：

```
gunicorn -k uvicorn.workers.UvicornWorker -w 8 --timeout 180 -b 0.0.0.0:22560 app.main:app
```

4. 环境变量示例（可选）：

```
# Linux/Mac
export deploy=inlandTest

# Windows PowerShell
$env:deploy="inlandTest"
```

5. 数据库初始化与迁移（开发）：

- 开发环境默认会自动 `create_all()` 建表（`ENVIRONMENT != production`）。
- 如需显式控制，可设置：

```
AUTO_CREATE_TABLES=true
```

- MySQL 连接示例（默认配置）：

```
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:2255@localhost:3306/yuyan
```

- 首次使用请先创建数据库：

```
CREATE DATABASE yuyan CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

- Alembic 迁移（推荐）：

```
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## 测试

1. 安装测试依赖：

```
pip install -r yuyan/requirements-dev.txt
```

2. 运行测试：

```
pytest yuyan/tests
```

## 配置说明

- 默认读取 `app/config/setting.py` 与 `app/config/secure.py`
- 可通过环境变量 `deploy` 切换环境
- 黑名单 IP 文件仍使用 `app/config/black_client_ip.txt`
