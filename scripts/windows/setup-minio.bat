@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: IndieTracks MinIO 一键部署脚本
:: 用法：双击运行，或在终端中直接执行
:: ============================================================

echo ============================================================
echo   IndieTracks MinIO 部署脚本
echo ============================================================
echo.

:: 路径计算（脚本在 scripts/windows/，项目根在 ../..)
set "ROOT=%~dp0..\.."
set "MINIO_EXE=%ROOT%\tools\minio\minio.exe"
set "MC_EXE=%ROOT%\tools\minio\mc.exe"
set "DATA_DIR=%ROOT%\database\minio-data"
set "CONFIG_FILE=%ROOT%\crawler\config\minio.json"

:: MinIO 管理员凭证
set "MINIO_ROOT_USER=admin"
set "MINIO_ROOT_PASSWORD=indietracks2026"

:: 应用凭证（写入 minio.json 供爬虫使用）
set "APP_USER=indietracks-app"
set "APP_PASSWORD=indietracks-app-2026"

echo [1/5] 检查 MinIO Server...

if exist "%MINIO_EXE%" (
    echo   minio.exe 已存在，跳过下载
) else (
    echo   正在下载 minio.exe ...
    mkdir "%ROOT%\tools\minio" 2>nul
    curl -L -o "%MINIO_EXE%" "https://dl.min.io/server/minio/release/windows-amd64/minio.exe"
    if errorlevel 1 (
        echo   [错误] 下载失败，请检查网络连接
        pause
        exit /b 1
    )
    echo   下载完成
)

echo [2/5] 检查 MinIO Client (mc) ...
if exist "%MC_EXE%" (
    echo   mc.exe 已存在，跳过下载
) else (
    echo   正在下载 mc.exe ...
    curl -L -o "%MC_EXE%" "https://dl.min.io/client/mc/release/windows-amd64/mc.exe"
    if errorlevel 1 (
        echo   [错误] 下载失败，请检查网络连接
        pause
        exit /b 1
    )
    echo   下载完成
)

echo [3/5] 启动 MinIO 服务 ...
echo   数据目录: %DATA_DIR%

:: 如果数据目录不存在则创建
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"

:: 检查 MinIO 是否已在运行
"%MC_EXE%" alias set local-check http://localhost:9000 admin indietracks2026 >nul 2>&1
if %errorlevel% equ 0 (
    echo   MinIO 已在运行
    "%MC_EXE%" alias remove local-check >nul 2>&1
) else (
    start "IndieTracks-MinIO" /MIN "%MINIO_EXE%" server "%DATA_DIR%" --console-address ":9001"
    echo   等待 MinIO 启动（10 秒）...
    timeout /t 10 /nobreak >nul
)

echo [4/5] 配置 Bucket 和访问密钥 ...
:: 设置 mc 别名
"%MC_EXE%" alias set local http://localhost:9000 admin indietracks2026

:: 创建 bucket（幂等）
echo   创建 bucket: indietracks
"%MC_EXE%" mb local/indietracks >nul 2>&1
if errorlevel 1 (
    echo   bucket 可能已存在，跳过
)

:: 创建应用用户
echo   创建应用用户: %APP_USER%
"%MC_EXE%" admin user add local %APP_USER% %APP_PASSWORD% >nul 2>&1
if errorlevel 1 (
    echo   用户可能已存在，跳过
)

:: 附加读写策略
echo   附加读写策略 ...
"%MC_EXE%" admin policy attach local readwrite --user %APP_USER% >nul 2>&1
if errorlevel 1 (
    echo   策略附加可能已存在，跳过
)

echo [5/5] 写入配置文件 ...
(
echo {
echo   "endpoint": "http://localhost:9000",
echo   "access_key": "%APP_USER%",
echo   "secret_key": "%APP_PASSWORD%",
echo   "bucket": "indietracks",
echo   "prefixes": {
echo     "audio_preview": "audio/preview/",
echo     "audio_full": "audio/full/",
echo     "covers": "covers/",
echo     "logos": "logos/",
echo     "avatars": "avatars/"
echo   }
echo }
) > "%CONFIG_FILE%"

echo   配置文件已写入: %CONFIG_FILE%

echo.
echo ============================================================
echo   部署完成！
echo   MinIO API:      http://localhost:9000
echo   MinIO 控制台:   http://localhost:9001
echo   管理员账号:     admin / indietracks2026
echo   应用账号:       %APP_USER% / %APP_PASSWORD%
echo ============================================================
echo.
echo 按任意键退出...
pause >nul
