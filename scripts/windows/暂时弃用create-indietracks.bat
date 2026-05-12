@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ==========================================
echo   IndieTracks 项目骨架一键创建脚本
echo   (Vue 3 + Spring Boot 4 + Scrapy)
echo ==========================================
echo.

:: ============ 第一步：检查必要的运行环境 ============
echo [第1步] 检查运行环境...
echo.

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 没有检测到 Node.js，请先安装 Node.js 22 或更高版本。
    echo 下载地址：https://nodejs.org
    pause
    exit /b 1
)
echo ✓ Node.js 已安装

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 没有检测到 npm，请检查 Node.js 安装是否完整。
    pause
    exit /b 1
)
echo ✓ npm 已安装

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 没有检测到 Python，请先安装 Python 3.10 或更高版本。
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python 已安装

where java >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 未在 PATH 中检测到 Java 命令。
    echo 如果已安装 JDK 25，请忽略此提示；否则请先安装。
    echo 下载地址：https://jdk.java.net/25/
)
echo ✓ Java 已安装

where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 未检测到 Git。如需版本管理，请安装 Git。
    echo 下载地址：https://git-scm.com/download/win
)
echo ✓ Git 已安装

echo.
echo [第2步] 确认创建目录并开始构建项目...
echo ==========================================
echo.
echo 项目将在当前目录下创建，所有文件将放入 indietracks 文件夹。
echo 如果该文件夹已存在，脚本将跳过已完成的步骤。
echo.
set /p confirm="是否继续创建项目？(输入 Y 确认，其他键退出): "
if /i not "%confirm%"=="Y" (
    echo 已取消操作。
    pause
    exit /b 0
)

:: ============ 第二步：创建项目根目录 ============
echo.
echo [正在创建项目根目录和子文件夹...]
mkdir indietracks 2>nul
cd indietracks
mkdir frontend 2>nul
mkdir backend 2>nul
mkdir crawler 2>nul
mkdir tools 2>nul
mkdir scripts 2>nul
mkdir data 2>nul
mkdir docs 2>nul
mkdir database 2>nul
echo ✓ 根目录结构已就绪

:: ============ 第三步：创建前端项目 (Vue 3 + Vite 8) ============
echo.
echo [第3步] 正在构建前端项目 (Vue 3 + Vite 8)...
if exist "frontend\package.json" (
    echo ⚠ frontend 项目已存在，跳过创建。
) else (
    rmdir /s /q frontend 2>nul
    echo 执行命令: npm create vite@latest frontend -- --template vue
    call npm create vite@latest frontend -- --template vue
    if %errorlevel% neq 0 (
        echo [错误] 前端项目创建失败，请检查网络连接或 npm 配置。
        pause
        exit /b 1
    )
    cd frontend
    echo 执行命令: npm install
    call npm install
    echo 执行命令: npm install vue-router@4 axios pinia
    call npm install vue-router@4 axios pinia
    cd ..
    echo ✓ 前端项目创建成功，并已安装 vue-router、axios、pinia
)

:: ============ 第四步：创建后端项目 (Spring Boot) ============
echo.
echo [第4步] 准备后端项目 (Spring Boot 4)...
if exist "backend\pom.xml" (
    echo ⚠ backend 项目已存在，跳过创建。
) else (
    echo ⚠ 脚本已自动跳过自动创建，还请手动创建
)

:: ============ 第五步：创建爬虫项目 (Scrapy) ============
echo.
echo [第5步] 正在构建爬虫项目 (Scrapy)...
if exist "crawler\scrapy.cfg" (
    echo ⚠ crawler 项目已存在，跳过创建。
) else (
    echo 执行命令: python -m venv crawler\env
    call python -m venv crawler\env
    if %errorlevel% neq 0 (
        echo [错误] 无法创建 Python 虚拟环境，请检查 Python 是否正确安装。
        pause
        exit /b 1
    )
    echo ✓ 虚拟环境创建完成

    echo 执行命令: 激活虚拟环境并安装 Scrapy
    call crawler\env\Scripts\activate.bat
    pip install scrapy
    if %errorlevel% neq 0 (
        echo [警告] Scrapy 安装失败，可能是网络问题，请稍后手动尝试。
        pause
    )
    scrapy startproject indietracks_spider .
    if %errorlevel% neq 0 (
        echo [警告] Scrapy 项目骨架创建失败，请检查 pip 安装情况。
    ) else (
        echo ✓ 爬虫项目创建成功
    )
    call deactivate
)

:: ============ 第六步：生成通用文件 (.gitignore) ============
echo.
echo [第6步] 生成通用配置和辅助文件...
if not exist ".gitignore" (
    echo 正在生成 .gitignore...
    (
        echo # 所有运行时产生的重型数据
        echo data/
        echo.
        echo # 前端
        echo frontend/node_modules/
        echo frontend/dist/
        echo.
        echo # 后端
        echo backend/target/
        echo *.class
        echo *.jar
        echo.
        echo # 爬虫
        echo crawler/env/
        echo __pycache__/
        echo *.pyc
        echo.
        echo # IDE 配置
        echo .vscode/
        echo .idea/
        echo *.iml
        echo.
        echo # 系统
        echo .DS_Store
        echo Thumbs.db
    ) > .gitignore
    echo ✓ .gitignore 已创建
)

if not exist "frontend\src\api\request.js" (
    echo 正在生成 axios 请求实例...
    (
        echo import axios from 'axios'
        echo const request = axios.create({ baseURL: '/api', timeout: 10000 })
        echo export default request
    ) > frontend\src\api\request.js
)

echo ✓ 基础配置文件已生成

:: ============ 第七步：完成 ============
echo.
echo ==========================================
echo   项目骨架创建完成！
echo ==========================================
echo.
echo 项目目录: %cd%
echo.
echo 接下来你需要做:
echo   1. 如果后端尚未创建，请按照上面第4步的提示手动下载 Spring Boot 项目。
echo   2. 进入 backend/ 目录，修改 pom.xml，将 Tomcat 替换为 Undertow。
echo   3. 分别进入 frontend/ 和 backend/ 目录，尝试启动开发服务器进行测试。
echo   4. 使用 git init 和 git remote add origin 将项目连接到远程仓库。
echo.
echo 祝你开发顺利！
pause