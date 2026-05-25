@echo off
setlocal enabledelayedexpansion

:: IndieTracks MinIO one-click setup
:: Run: double-click or execute from terminal

echo ============================================================
echo   IndieTracks MinIO Setup
echo ============================================================
echo.

:: Paths (script is in scripts/windows/, project root is ..\..)
set "ROOT=%~dp0..\.."
set "MINIO_EXE=%ROOT%\tools\minio\minio.exe"
set "MC_EXE=%ROOT%\tools\minio\mc.exe"
set "DATA_DIR=%ROOT%\database\minio-data"
set "CONFIG_FILE=%ROOT%\crawler\config\minio.json"

:: Credentials
set "ROOT_USER=admin"
set "ROOT_PASS=indietracks2026"
set "APP_USER=indietracks_app"
set "APP_PASS=indietracks_app_2026"

echo [1/5] Check MinIO Server...

if exist "%MINIO_EXE%" (
    echo   minio.exe found, skip download
) else (
    echo   Downloading minio.exe...
    if not exist "%ROOT%\tools\minio" mkdir "%ROOT%\tools\minio"
    curl -L -o "%MINIO_EXE%" "https://dl.min.io/server/minio/release/windows-amd64/minio.exe"
    if errorlevel 1 (
        echo   [ERROR] Download failed, check network
        pause
        exit /b 1
    )
    echo   Done
)

echo [2/5] Check MinIO Client (mc)...
if exist "%MC_EXE%" (
    echo   mc.exe found, skip download
) else (
    echo   Downloading mc.exe...
    curl -L -o "%MC_EXE%" "https://dl.min.io/client/mc/release/windows-amd64/mc.exe"
    if errorlevel 1 (
        echo   [ERROR] Download failed, check network
        pause
        exit /b 1
    )
    echo   Done
)

echo [3/5] Start MinIO...
echo   Data dir: %DATA_DIR%
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"

:: Check if MinIO already running
"%MC_EXE%" alias set local_check http://localhost:9000 %ROOT_USER% %ROOT_PASS% >nul 2>&1
if errorlevel 1 (
    set MINIO_ROOT_USER=%ROOT_USER%
    set MINIO_ROOT_PASSWORD=%ROOT_PASS%
    start "IndieTracks-MinIO" /MIN "%MINIO_EXE%" server "%DATA_DIR%" --console-address ":9001"
    echo   Waiting 10s for MinIO to start...
    timeout /t 10 /nobreak >nul
) else (
    echo   MinIO already running
)

echo [4/5] Configure Bucket and Access Key...
"%MC_EXE%" alias set local http://localhost:9000 %ROOT_USER% %ROOT_PASS%

echo   Create bucket: indietracks
"%MC_EXE%" mb local/indietracks >nul 2>&1
if errorlevel 1 (echo   bucket may already exist)

echo   Create app user: %APP_USER%
"%MC_EXE%" admin user add local %APP_USER% %APP_PASS% >nul 2>&1
if errorlevel 1 (echo   user may already exist)

echo   Attach readwrite policy...
"%MC_EXE%" admin policy attach local readwrite --user %APP_USER% >nul 2>&1
if errorlevel 1 (echo   policy may already be attached)
"%MC_EXE%" alias remove local_check >nul 2>&1

echo [5/5] Write config file...
(
echo {
echo   "endpoint": "http://localhost:9000",
echo   "access_key": "%APP_USER%",
echo   "secret_key": "%APP_PASS%",
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

echo   Config written: %CONFIG_FILE%

echo.
echo ============================================================
echo   Setup complete!
echo   MinIO API:       http://localhost:9000
echo   MinIO Console:   http://localhost:9001
echo   Root:            %ROOT_USER% / %ROOT_PASS%
echo   App:             %APP_USER% / %APP_PASS%
echo ============================================================
echo.
echo Press any key to exit...
pause >nul
