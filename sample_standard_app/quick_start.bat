@echo off

:: 忽略管道错误
SETLOCAL ENABLEEXTENSIONS

:: 检查是否安装了Python，如果没有安装则进行安装，或者Python的版本小于3.10
python --version 2>nul | findstr /r "^Python 3\.1[0-9]" >nul
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or the version is less than 3.10. Installing Python...

    :: 检查是否安装了Conda
    conda --version >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        echo conda is not installed. Installing conda...
        md %USERPROFILE%\miniconda3
        curl -o %USERPROFILE%\miniconda3\miniconda.exe https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py39_24.3.0-0-Windows-x86_64.exe
        %USERPROFILE%\miniconda3\miniconda.exe /InstallationType=JustMe /RegisterPython=0 /AddToPath=0 /S /D=%USERPROFILE%\miniconda3
        CALL %USERPROFILE%\miniconda3\Scripts\conda.exe init
        SETX PATH "%USERPROFILE%\miniconda3\Scripts;%USERPROFILE%\miniconda3;%PATH%"
        DEL %USERPROFILE%\miniconda3\miniconda.exe
        :: 配置清华镜像源
        conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
        conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
        conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
        conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
    )

    :: 创建并激活Python 3.10环境
    conda create -n python_au3.10 python=3.10 -y
    conda config --set default_env python_au3.10
    SET PATH=%USERPROFILE%\miniconda3\envs\python_au3.10\Scripts;%USERPROFILE%\miniconda3\envs\python_au3.10;%PATH%
    echo Python 3.10 environment created and activated.
    python --version
)

python --version 2>nul | findstr /r "^Python 3\.1[0-9]" >nul
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Python version is not 3.10. Please install Python 3.10 and try again.
    exit /b 1
)

:: 判断是否已安装 agentUniverse
pip list 2>nul | findstr /r "^agentUniverse" >nul
IF %ERRORLEVEL% NEQ 0 (
    pip install agentUniverse
)

:: 检查 custom_key 文件是否存在，如果不存在，从示例复制
IF NOT EXIST "config\custom_key.toml" (
    copy config\custom_key.toml.sample config\custom_key.toml
)

:: 设置 PYTHONPATH 为当前工作目录的父目录
SET PYTHONPATH=%CD%\..\..

:: 启动服务
cd app\bootstrap
python -u server_application.py
