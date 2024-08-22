@echo off

rem Ignore broken pipe errors
rem Windows doesn't need to handle PIPE errors like Unix, so this can be ignored.

rem 判断conda命令是否存在，如果不存在，则判断%USERPROFILE%\miniconda3\bin是否存在，如果存在则export一下conda
where conda >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" (
        echo conda already installed. Adding %USERPROFILE%\miniconda3\Scripts to PATH...
        set PATH=%USERPROFILE%\miniconda3\Scripts;%PATH%
    ) else (
        echo conda is not installed...
    )
) else (
    echo conda is already installed.
)

:install_conda
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo conda is not installed. Installing conda...
    mkdir %USERPROFILE%\miniconda3
    rem 根据系统类型下载Miniconda
    if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
        if "%OS%"=="Windows_NT" (
            powershell -Command "Invoke-WebRequest -Uri https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py39_24.3.0-0-Windows-x86_64.exe -OutFile %USERPROFILE%\miniconda3\miniconda.exe"
        )
    ) else (
        rem Handle other architectures if needed
    )
    rem 静默安装Miniconda
    %USERPROFILE%\miniconda3\miniconda.exe /InstallationType=JustMe /RegisterPython=0 /AddToPath=0 /S /D=%USERPROFILE%\miniconda3
    set PATH=%USERPROFILE%\miniconda3\Scripts;%USERPROFILE%\miniconda3;%PATH%
    del %USERPROFILE%\miniconda3\miniconda.exe
    rem 配置清华源
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
    echo conda is installed.
)

rem 检查Python是否安装，如果没有安装则安装它，或者python的版本小于3.10
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...
    call :install_conda
)

python --version 2>&1 | findstr /r "3\.10" >nul
if %errorlevel% neq 0 (
    where conda >nul 2>&1
    if %errorlevel% neq 0 (
        echo conda is not installed. Please install conda and try again.
        call :install_conda
    )
    conda env list | findstr "python_au3.10" >nul
    if %errorlevel% neq 0 (
        echo Python 3.10 environment is not installed. Installing Python 3.10 environment...
        conda create -n python_au3.10 python=3.10 -y
    )
    for /f "delims=" %%i in ('conda info --base') do set CONDA_BASE=%%i
    set PATH=%CONDA_BASE%\envs\python_au3.10\Scripts;%CONDA_BASE%\envs\python_au3.10;%PATH%
)

rem 判断 pip list 是否已安装 agentUniverse
pip list | findstr "agentUniverse" >nul
if %errorlevel% neq 0 (
    pip install agentUniverse -i https://pypi.tuna.tsinghua.edu.cn/simple
)

rem Check if custom_key file exists, if not, copy from sample
if not exist "config\custom_key.toml" (
    copy config\custom_key.toml.sample config\custom_key.toml
)

rem 替换 config.toml 中的 #custom_key_path 为 custom_key_path
powershell -Command "(Get-Content -path .\config\config.toml) -replace '^#custom_key_path = ''\.\/custom_key\.toml''', 'custom_key_path = ''\.\/custom_key\.toml''' | Set-Content -path .\config\config.toml"

rem Set PYTHONPATH to the parent directory of the current working directory
set PYTHONPATH=%cd%\..\..

rem Start the service
cd app\bootstrap
python -u server_application.py
