#!/bin/bash

# JokerAIRunner Docker 环境初始化脚本
# 用于创建容器运行所需的输出目录

set -e

echo "=========================================="
echo "JokerAIRunner Docker 初始化"
echo "=========================================="
echo ""

# 创建输出目录
echo "创建输出目录..."
mkdir -p output/allure_result
mkdir -p output/allure_report
mkdir -p output/logs
mkdir -p output/midscene_run/report

# 清理旧的测试结果
echo "清理旧的测试结果..."
rm -rf output/allure_result/* 2>/dev/null || true
rm -rf output/allure_report/* 2>/dev/null || true

echo "✓ 输出目录创建成功"
echo ""

# 显示目录结构
echo "输出目录结构："
tree -L 2 output/ 2>/dev/null || find output/ -type d -maxdepth 2 | sed 's|[^/]*/| |g'

echo ""
echo "=========================================="
echo "初始化完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 构建镜像: docker-compose build"
echo "2. 运行测试: docker-compose run --rm jokerai-runner"
echo "3. 查看报告: docker-compose --profile report up allure-report"
echo ""

