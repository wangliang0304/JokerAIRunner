# JokerAIRunner 容器化使用指南

将 JokerAIRunner 打包为容器化的自动化测试执行引擎，支持 API 和 UI 测试。

## 目录

- [快速开始](#快速开始)
- [构建镜像](#构建镜像)
- [容器管理](#容器管理)
- [运行测试](#运行测试)
- [查看报告](#查看报告)
- [环境变量配置](#环境变量配置)
- [常见问题排查](#常见问题排查)

---

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+

### 初始化环境

```bash
# 1. 初始化输出目录
./init-docker.sh

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的配置

# 3. 构建镜像
docker-compose build

# 4. 启动容器
./container.sh start
```

---

## 构建镜像

```bash
# 使用 Docker Compose（推荐）
docker-compose build

# 使用 Docker 命令
docker build -t jokerai-runner:latest .
```

### 镜像信息

- **基础镜像**: python:3.10-slim
- **预期大小**: ~1.2-1.5GB
- **包含组件**:
  - Python 3.10
  - Node.js 18
  - Chromium
  - MidScene CLI
  - ADB 工具
  - Allure CLI
  - HttpRunner + pytest

---

## 容器管理

### 使用管理脚本（推荐）

```bash
# 启动容器（后台运行）
./container.sh start

# 查看状态
./container.sh status

# 查看日志
./container.sh logs

# 进入容器 Shell
./container.sh shell

# 停止容器
./container.sh stop

# 清理资源
./container.sh clean
```

### 使用 Docker Compose 命令

```bash
# 启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f jokerai-runner

# 停止容器
docker-compose down
```

---

## 运行测试

### 方式 1：使用容器脚本（推荐）

```bash
# 启动容器
./container.sh start

# 运行 API 测试
./container.sh test-api

# 运行 UI 测试
./container.sh test-ui

# 运行所有测试
./container.sh test-all

# 生成并查看报告
./container.sh report
```

### 方式 2：使用 Docker 命令

```bash
# 启动容器
docker-compose up -d

# 运行 API 测试
docker exec -it jokerai-test-runner \
  pytest testcases/api/demo/requests_demo_test.py -v

# 运行 UI 测试
docker exec -it jokerai-test-runner \
  pytest testcases/UI/demo/test_midscene_web_demo.yaml -v

# 运行所有 API 测试
docker exec -it jokerai-test-runner pytest testcases/api/ -v

# 运行所有 UI 测试
docker exec -it jokerai-test-runner pytest testcases/UI/ -v
```

### 方式 3：进入容器手动执行

```bash
# 进入容器
./container.sh shell

# 在容器内运行测试
pytest testcases/api/demo/requests_demo_test.py -v
pytest testcases/UI/demo/test_midscene_web_demo.yaml -v

# 退出容器
exit
```

---

## 查看报告

### 生成报告

```bash
# 使用脚本（推荐）
./container.sh report

# 或手动生成
docker exec jokerai-test-runner \
  allure generate /workspace/allure_result -o /workspace/allure_report --clean
```

### 查看报告

报告会自动在浏览器中打开（macOS/Linux），或手动打开：

```bash
# macOS
open output/allure_report/index.html

# Linux
xdg-open output/allure_report/index.html

# Windows
start output/allure_report/index.html
```

### 报告位置

- **Allure 原始结果**: `output/allure_result/`
- **Allure HTML 报告**: `output/allure_report/index.html`
- **MidScene 报告**: `output/midscene_run/report/`

---

## 环境变量配置

### 必需变量（.env 文件）

```bash
# MidScene AI 模型配置
MIDSCENE_MODEL_BASE_URL="https://api.siliconflow.cn/v1"
MIDSCENE_MODEL_API_KEY="your-api-key-here"
MIDSCENE_MODEL_NAME="Qwen/Qwen2.5-VL-32B-Instruct"
MIDSCENE_MODEL_FAMILY="qwen2.5-vl"

# MidScene 执行配置
MIDSCENE_HEADED=false              # 是否显示浏览器
MIDSCENE_KEEP_WINDOW=false         # 保持窗口开启
MIDSCENE_TIMEOUT=120               # 超时时间（秒）

# 测试环境配置
BASE_URL=https://api.example.com
TEST_ENV=development

# Docker 配置
RUN_IN_DOCKER=true

# 业务变量
USERNAME=debugtalk
```

### 临时覆盖环境变量

```bash
# 方式 1：通过 .env 文件永久修改
vim .env

# 方式 2：通过命令行临时覆盖
MIDSCENE_HEADED=true ./container.sh test-ui

# 方式 3：通过 docker-compose 覆盖
MIDSCENE_HEADED=true MIDSCENE_TIMEOUT=300 \
  docker exec -it jokerai-test-runner pytest testcases/UI/ -v
```

---

## Android 设备连接

### 方式 1：WiFi 连接（推荐）

```bash
# 1. Android 设备通过 USB 连接到电脑
adb tcpip 5555

# 2. 查看设备 IP
adb shell ip addr show wlan0

# 3. 在容器中连接
docker exec -it jokerai-test-runner adb connect 192.168.1.100:5555

# 4. 验证连接
docker exec -it jokerai-test-runner adb devices

# 5. 运行 Android 测试
docker exec -it jokerai-test-runner \
  pytest testcases/UI/android/test_android_joker_homepage.yaml -v
```

### 方式 2：Host 网络模式

修改 `docker-compose.yml`：

```yaml
services:
  jokerai-runner:
    network_mode: host  # 使用 host 网络
```

这样容器可以直接访问宿主机的 ADB 连接。

---

## 常见问题排查

### 问题 1：容器启动失败

**症状**：`docker-compose up` 失败

**解决方案**：
```bash
# 查看详细错误
docker-compose up

# 清理旧容器
docker-compose down -v
docker system prune -f

# 重新启动
./container.sh start
```

### 问题 2：测试执行失败

**症状**：测试退出码为 1

**解决方案**：
```bash
# 查看详细日志
./container.sh logs

# 进入容器手动测试
./container.sh shell
pytest -vv testcases/api/demo/requests_demo_test.py --tb=long
```

### 问题 3：找不到 Chrome

**症状**：MidScene 报错找不到 Chrome

**解决方案**：已配置 `PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium`

### 问题 4：网络问题

**症状**：无法访问外部 API

**解决方案**：
```bash
# 使用 host 网络模式
# 在 docker-compose.yml 中添加：
network_mode: host

# 或配置代理
docker-compose run -e HTTP_PROXY=http://proxy:8080 jokerai-runner
```

### 问题 5：磁盘空间不足

**症状**：`No space left on device`

**解决方案**：
```bash
# 清理 Docker 资源
docker system prune -a --volumes

# 清理输出目录
rm -rf output/allure_result/* output/allure_report/*
```

---

## 高级用法

### 自定义测试命令

```bash
# 进入容器
./container.sh shell

# 运行特定测试
pytest testcases/api/ -v -k "test_login"

# 并行运行
pytest testcases/ -v -n auto

# 生成 JUnit 报告
pytest testcases/ -v --junitxml=output/junit.xml
```

### 多环境配置

```bash
# 切换环境
cp .env.development .env
cp .env.staging .env
cp .env.production .env

# 或使用环境变量
TEST_ENV=production ./container.sh test-api
```

### CI/CD 集成

```bash
# GitHub Actions
- name: Run tests
  run: |
    docker-compose build
    ./container.sh test-all

# Jenkins
stage('Test') {
  steps {
    sh './container.sh test-all'
  }
}
```

---

## 文件说明

### 核心文件

- **Dockerfile** - 容器镜像定义
- **docker-compose.yml** - 服务编排配置
- **container.sh** - 容器管理脚本
- **.env** - 环境变量配置
- **init-docker.sh** - 初始化脚本

### 目录结构

```
JokerAIRunner/
├── Dockerfile                  # 镜像构建文件
├── docker-compose.yml          # 服务编排
├── container.sh                # 管理脚本
├── .env                        # 环境变量
├── .env.example               # 环境变量模板
├── init-docker.sh              # 初始化脚本
├── testcases/                  # 测试用例
│   ├── api/                   # API 测试
│   └── UI/                    # UI 测试
│       ├── web/               # Web UI
│       └── android/           # Android UI
├── output/                     # 输出目录
│   ├── allure_result/         # Allure 原始结果
│   ├── allure_report/         # Allure HTML 报告
│   ├── logs/                  # 日志文件
│   └── midscene_run/          # MidScene 报告
├── common/                     # 公共模块
├── config/                     # 配置文件
└── util/                       # 工具类
```

---

## 使用示例

### 场景 1：本地开发调试

```bash
# 1. 启动容器
./container.sh start

# 2. 进入容器
./container.sh shell

# 3. 运行测试
pytest testcases/api/demo/ -v

# 4. 查看报告
./container.sh report
```

### 场景 2：快速验证

```bash
# 一条命令完成测试
docker-compose run --rm jokerai-runner \
  pytest testcases/api/demo/requests_demo_test.py -v
```

### 场景 3：持续测试

```bash
# 启动容器（保持运行）
./container.sh start

# 反复运行测试
./container.sh test-api
./container.sh test-ui

# 最后查看报告
./container.sh report

# 完成
./container.sh stop
```

---

## 最佳实践

1. **首次使用**：
   - 运行 `./init-docker.sh` 初始化
   - 运行 `./container.sh start` 启动容器
   - 运行 `./container.sh test-api` 验证

2. **日常使用**：
   - 保持容器运行：`./container.sh start`
   - 随时执行测试：`./container.sh test-*`
   - 定期查看报告：`./container.sh report`

3. **资源管理**：
   - 定期清理：`./container.sh clean`
   - 停止不用容器：`./container.sh stop`

4. **调试技巧**：
   - 查看日志：`./container.sh logs`
   - 进入容器：`./container.sh shell`
   - 使用 `-vv` 增加输出：`pytest -vv test.py`

---

## 支持与反馈

如有问题或建议，请查看以下文档：
- DOCKER_DEBUG.md - 详细调试指南
- README.md - 项目整体说明

---

**最后更新**: 2026-01-02
**文档版本**: 2.0.0
