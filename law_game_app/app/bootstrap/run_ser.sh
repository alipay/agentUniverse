#!/bin/bash

# 检查是否提供了应用程序名称作为参数
if [ -z "$1" ]; then
    echo "请提供 Python 脚本的名称作为参数。"
    exit 1
fi

# 定义应用程序的名字
APP_NAME="$1"

# 检查应用程序是否正在运行
is_running() {
    pgrep -f "$APP_NAME" > /dev/null
    return $?
}

# 启动应用程序
start_app() {
    if is_running; then
        echo "应用 '$APP_NAME' 已经在运行。"
    else
        nohup python "$APP_NAME" > /dev/null 2>&1 &
        echo "应用 '$APP_NAME' 已启动。"
    fi
}

# 关闭应用程序
stop_app() {
    if is_running; then
        pkill -9 -f "$APP_NAME"
        echo "应用 '$APP_NAME' 已停止。"
    else
        echo "应用 '$APP_NAME' 没有在运行。"
    fi
}

# 重启应用程序
restart_app() {
    stop_app
    start_app
}

# 根据传入的第一个参数执行相应的动作
case "$2" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    *)
        echo "用法: $0 <脚本名称> {start|stop|restart}"
        exit 1
        ;;
esac
