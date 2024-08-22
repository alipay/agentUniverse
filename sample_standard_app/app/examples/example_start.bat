@echo off

REM 忽略管道错误
setlocal EnableDelayedExpansion
set "PATH=%PATH%;%USERPROFILE%\miniconda3\Scripts;%USERPROFILE%\miniconda3"

REM 判断conda命令是否存在，如果不存在，则判断%USERPROFILE%\miniconda3\Scripts是否存在
where conda >nul 2>nul
if %errorlevel% neq 0 (
    if exist "%USERPROFILE%\miniconda3\Scripts" (
        echo conda已安装，将%USERPROFILE%\miniconda3\Scripts添加到PATH...
        set "PATH=%USERPROFILE%\miniconda3\Scripts;%PATH%"
    ) else (
        echo conda未安装...
    )
) else (
    echo conda已在环境变量中
)

REM 定义安装conda的函数
:install_conda
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo conda未安装，正在安装conda...
    mkdir "%USERPROFILE%\miniconda3"
    if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
        powershell -Command "Invoke-WebRequest -Uri https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py39_24.3.0-0-Windows-x86_64.exe -OutFile %USERPROFILE%\miniconda3\miniconda.exe"
    ) else (
        powershell -Command "Invoke-WebRequest -Uri https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py39_24.3.0-0-Windows-x86_64.exe -OutFile %USERPROFILE%\miniconda3\miniconda.exe"
    )
    "%USERPROFILE%\miniconda3\miniconda.exe" /InstallationType=JustMe /RegisterPython=0 /AddToPath=0 /S /D=%USERPROFILE%\miniconda3
    call "%USERPROFILE%\miniconda3\Scripts\conda.exe" init bash
    call "%USERPROFILE%\miniconda3\Scripts\conda.exe" init powershell
    set "PATH=%USERPROFILE%\miniconda3\Scripts;%PATH%"
    del "%USERPROFILE%\miniconda3\miniconda.exe"
    call conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
    call conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
    call conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
    call conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
    echo conda安装完成
)

REM 检查是否安装Python，如果没有，安装Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 未检测到Python，正在安装...
    call :install_conda
)

REM 检查Python版本
for /f "tokens=2 delims==" %%i in ('python --version 2^>^&1') do set py_version=%%i
if not "%py_version%"=="3.10" (
    where conda >nul 2>nul
    if %errorlevel% neq 0 (
        echo conda未安装，请安装conda后重试。
        call :install_conda
    )
    call conda env list | findstr "python_au3.10" >nul
    if %errorlevel% neq 0 (
        echo Python 3.10环境未安装，正在安装...
        call conda create -n python_au3.10 python=3.10 -y
    )
    for /f "tokens=*" %%i in ('conda info --base') do set CONDA_BASE=%%i
    set "PATH=%CONDA_BASE%\envs\python_au3.10\Scripts;%PATH%"
)

REM 检查agentUniverse是否已安装
pip list | findstr "agentUniverse" >nul
if %errorlevel% neq 0 (
   pip install agentUniverse -i https://pypi.tuna.tsinghua.edu.cn/simple
)

REM 检查custom_key文件是否存在
if not exist "..\..\config\custom_key.toml" (
    copy "..\..\config\custom_key.toml.sample" "..\..\config\custom_key.toml"
)

REM 修改config.toml文件
powershell -Command "(Get-Content ..\..\config\config.toml) -replace '^#custom_key_path = ''\.\/custom_key\.toml''', 'custom_key_path = ''\.\/custom_key\.toml''' | Set-Content ..\..\config\config.toml"

REM 设置PYTHONPATH
set PYTHONPATH=%CD%\..\..\..\..\

REM 启动服务
cd app\bootstrap
python -u rag_chat_bot.py
