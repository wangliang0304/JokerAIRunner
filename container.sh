#!/bin/bash

# ========================================
# JokerAIRunner 容器管理脚本
# ========================================

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 显示帮助
show_help() {
    cat << EOF
${GREEN}JokerAIRunner 容器管理工具${NC}

用法:
    ./container.sh [命令]

命令:
    start       启动容器（后台运行）
    stop        停止容器
    restart     重启容器
    status      查看容器状态
    logs        查看容器日志
    shell       进入容器 Shell
    test-api    运行 API 测试
    test-ui     运行 UI 测试
    test-all    运行所有测试
    report      生成并查看 Allure 报告
    clean       清理容器和资源

示例:
    ./container.sh start          # 启动容器
    ./container.sh test-api       # 运行 API 测试
    ./container.sh shell          # 进入容器
    ./container.sh logs           # 查看日志

EOF
}

# 启动容器
start_container() {
    echo -e "${BLUE}启动 JokerAIRunner 容器...${NC}"
    docker-compose up -d jokerai-runner
    echo -e "${GREEN}✓ 容器已启动${NC}"
    echo ""
    echo "容器信息:"
    docker-compose ps jokerai-runner
    echo ""
    echo "下一步:"
    echo "  ./container.sh shell        # 进入容器"
    echo "  ./container.sh test-api     # 运行 API 测试"
    echo "  ./container.sh logs         # 查看日志"
}

# 停止容器
stop_container() {
    echo -e "${BLUE}停止容器...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ 容器已停止${NC}"
}

# 重启容器
restart_container() {
    echo -e "${BLUE}重启容器...${NC}"
    docker-compose restart jokerai-runner
    echo -e "${GREEN}✓ 容器已重启${NC}"
    docker-compose ps jokerai-runner
}

# 查看状态
show_status() {
    echo -e "${BLUE}容器状态:${NC}"
    echo ""
    docker-compose ps
    echo ""

    # 检查容器是否在运行
    if docker-compose ps | grep -q "jokerai-runner.*Up"; then
        echo -e "${GREEN}✓ 容器正在运行${NC}"
        echo ""
        echo "快速命令:"
        echo "  docker exec -it jokerai-test-runner bash"
    else
        echo -e "${YELLOW}⚠ 容器未运行${NC}"
        echo ""
        echo "启动容器: ./container.sh start"
    fi
}

# 查看日志
show_logs() {
    echo -e "${BLUE}查看容器日志（Ctrl+C 退出）...${NC}"
    echo ""
    docker-compose logs -f jokerai-runner
}

# 进入容器
enter_shell() {
    echo -e "${BLUE}进入容器 Shell...${NC}"
    echo ""
    docker exec -it jokerai-test-runner bash
}

# 运行 API 测试
run_api_test() {
    echo -e "${BLUE}运行 API 测试...${NC}"
    echo ""
    docker exec -it jokerai-test-runner \
        pytest testcases/api/demo/requests_demo_test.py -v
}

# 运行 UI 测试
run_ui_test() {
    echo -e "${BLUE}运行 UI 测试...${NC}"
    echo ""
    docker exec -it jokerai-test-runner \
        pytest testcases/UI/demo/test_midscene_web_demo.yaml -v
}

# 运行所有测试
run_all_tests() {
    echo -e "${BLUE}运行所有测试...${NC}"
    echo ""
    docker exec -it jokerai-test-runner \
        pytest testcases/api/demo/requests_demo_test.py \
               testcases/UI/demo/test_midscene_web_demo.yaml -v
}

# 生成并查看报告
show_report() {
    echo -e "${BLUE}生成 Allure 报告...${NC}"
    echo ""

    # 生成报告
    docker exec jokerai-test-runner \
        allure generate /workspace/allure_result -o /workspace/allure_report --clean

    echo -e "${GREEN}✓ 报告已生成${NC}"
    echo ""
    echo "报告位置: output/allure_report/index.html"
    echo ""

    # 在 macOS 上打开报告
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open output/allure_report/index.html
    elif command -v xdg-open &> /dev/null; then
        xdg-open output/allure_report/index.html
    else
        echo "请手动打开报告: output/allure_report/index.html"
    fi
}

# 清理资源
clean_resources() {
    echo -e "${BLUE}清理容器和资源...${NC}"
    docker-compose down -v
    docker system prune -f
    echo -e "${GREEN}✓ 清理完成${NC}"
}

# ========================================
# 主函数
# ========================================
main() {
    case "${1:-help}" in
        start)
            start_container
            ;;
        stop)
            stop_container
            ;;
        restart)
            restart_container
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        shell)
            enter_shell
            ;;
        test-api)
            run_api_test
            ;;
        test-ui)
            run_ui_test
            ;;
        test-all)
            run_all_tests
            ;;
        report)
            show_report
            ;;
        clean)
            clean_resources
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${YELLOW}未知命令: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
