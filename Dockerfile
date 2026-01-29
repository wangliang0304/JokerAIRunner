# ========================================
# Stage 1: 基础环境
# ========================================
FROM python:3.10-slim AS base

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Node.js 环境
    NODE_VERSION=18 \
    # MidScene 配置
    MIDSCENE_HEADED=false \
    MIDSCENE_KEEP_WINDOW=false \
    MIDSCENE_TIMEOUT=120 \
    # 工作目录
    WORKSPACE=/workspace \
    # Allure 报告路径
    ALLURE_RESULT_DIR=/workspace/allure_result \
    ALLURE_REPORT_DIR=/workspace/allure_report

# 设置工作目录
WORKDIR $WORKSPACE

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Chrome 依赖
    wget \
    gnupg \
    # Chrome 运行时库
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    # Android ADB 工具
    android-tools-adb \
    android-tools-fastboot \
    # 其他工具
    curl \
    git \
    vim \
    # X11（用于有头模式）
    xvfb \
    # 清理缓存
    && rm -rf /var/lib/apt/lists/*

# ========================================
# Stage 2: 安装 Node.js
# ========================================
FROM base AS node-installer

# 安装 Node.js 18（使用 NodeSource 仓库）
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    node --version && \
    npm --version

# ========================================
# Stage 3: 安装 Chromium
# ========================================
FROM node-installer AS chrome-installer

# 安装 Chromium 及其依赖（Debian 官方维护，更稳定）
RUN apt-get update && \
    apt-get install -y chromium chromium-driver && \
    chromium --version && \
    # 设置 Chromium 作为默认浏览器
    update-alternatives --install /usr/bin/google-chrome google-chrome /usr/bin/chromium 100 && \
    # 清理缓存
    rm -rf /var/lib/apt/lists/*

# ========================================
# Stage 4: 安装 Python 依赖
# ========================================
FROM chrome-installer AS python-deps

# 复制 requirements.txt
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Java JRE（Allure 需要）
RUN apt-get update && \
    apt-get install -y default-jre-headless && \
    java -version && \
    rm -rf /var/lib/apt/lists/*

# 设置 JAVA_HOME 环境变量
ENV JAVA_HOME=/usr/lib/jvm/default-java

# 安装 Allure 命令行工具
RUN curl -o allure-2.29.0.tgz -L https://github.com/allure-framework/allure2/releases/download/2.29.0/allure-2.29.0.tgz && \
    tar -zxvf allure-2.29.0.tgz && \
    mv allure-2.29.0 /opt/allure && \
    ln -s /opt/allure/bin/allure /usr/local/bin/allure && \
    rm allure-2.29.0.tgz && \
    allure --version

# ========================================
# Stage 5: 安装 MidScene CLI
# ========================================
FROM python-deps AS midscene-installer

# 全局安装 MidScene CLI
RUN npm install -g @midscene/cli && \
    midscene --version

# ========================================
# Stage 6: 最终镜像
# ========================================
FROM midscene-installer AS final

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p /workspace/allure_result \
    /workspace/allure_report \
    /workspace/midscene_run/report \
    /workspace/logs \
    /workspace/testcases

# 创建非 root 用户（安全性）
RUN useradd -m -u 1000 -s /bin/bash testrunner && \
    chown -R testrunner:testrunner /workspace

# 切换到非 root 用户
USER testrunner

# 暴露端口（Allure 报告服务）
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import pytest; print('OK')" || exit 1

# 设置默认命令
CMD ["/bin/bash"]

# ========================================
# 镜像元数据
# ========================================
LABEL maintainer="your-email@example.com" \
      version="1.0.0" \
      description="JokerAIRunner - API & UI Automation Testing Engine" \
      python.version="3.10" \
      node.version="18" \
      chromium.version="stable"
