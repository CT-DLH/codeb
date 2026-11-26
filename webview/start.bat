@echo off
setlocal enabledelayedexpansion

rem ============================================================
rem  codeb webview launcher
rem
rem  Adapted from the shared_knowledge/launcher/launcher.bat
rem  template. webview is a ZERO-BUILD, live-file Node server, so
rem  the template's build + freshness-probe stages are removed
rem  (there is nothing to compile and nothing goes stale).
rem  Kept from the skeleton: arg parsing, PORT/HOST defaults with
rem  env override, node resolution with fallback, port cleanup,
rem  foreground serve, optional browser open.
rem
rem  Usage:
rem    webview\start.bat              start on port 8777, open browser
rem    webview\start.bat --no-open    do not open the browser
rem    set PORT=9000 & webview\start.bat    use another port
rem    set HOST=0.0.0.0 & webview\start.bat  bind all interfaces
rem    set ROOT=D:\somewhere & webview\start.bat  serve another workspace
rem
rem  NOTE: keep this file ASCII-only. cmd.exe parses .bat with the
rem  OEM codepage; UTF-8 Chinese breaks lines mid-character.
rem ============================================================

rem ======================= CONFIG START =======================
rem Short name used in log lines.
set "APP_NAME=codeb-webview"

rem Port + bind address DEFAULTS. A PORT/HOST already present in the
rem environment wins (see "defaults" section below). HOST stays loopback
rem by default -- this panel can read/edit workspace files and expose
rem session data, so it must not silently bind to the network.
set "DEFAULT_PORT=8777"
set "DEFAULT_HOST=127.0.0.1"

rem Absolute fallback node.exe for machines without node on PATH.
rem Leave empty to require node on PATH.
set "NODE_FALLBACK=C:\Users\30520\.workbuddy\binaries\node\versions\22.22.2-6\node.exe"

rem Workspace root passed to server.mjs via --root. Empty means "let
rem server.mjs auto-detect" (it walks up looking for repo/00-projects.md).
rem Override with `set ROOT=...` before starting.
set "WORKSPACE_ROOT="

rem Foreground serve command. %NODE% is the resolved node path,
rem %PORT% / %HOST% / %WORKSPACE_ROOT% are resolved below.
set "SERVER_SCRIPT=webview\server.mjs"
rem ======================== CONFIG END ========================

rem ---------- parse args ----------
set "OPEN=1"
:parse
if "%~1"=="" goto parsed
if /i "%~1"=="--no-open" set "OPEN=0"
if /i "%~1"=="-h" goto usage
if /i "%~1"=="--help" goto usage
shift
goto parse
:parsed

rem ---------- defaults (env overrides config) ----------
rem Only set from the DEFAULT_* fallbacks when not already in the env,
rem so `set PORT=9000 & webview\start.bat` works.
if not defined PORT set "PORT=%DEFAULT_PORT%"
if not defined HOST set "HOST=%DEFAULT_HOST%"
set "APP_DIR=%~dp0.."
cd /d "%~dp0.."
rem Resolve to an absolute root so server.mjs does not depend on cwd.
if "%WORKSPACE_ROOT%"=="" set "WORKSPACE_ROOT=%CD%"

rem ---------- resolve node ----------
where node >nul 2>&1
if %errorlevel%==0 (
  set "NODE=node"
) else (
  if not "%NODE_FALLBACK%"=="" (
    set "NODE=%NODE_FALLBACK%"
  ) else (
    echo [%APP_NAME%] ERROR: node not found. Install Node or put it on PATH.
    exit /b 1
  )
)
"%NODE%" -v >nul 2>&1
if errorlevel 1 (
  echo [%APP_NAME%] ERROR: node not found. Install Node or put it on PATH.
  exit /b 1
)

rem ---------- free the port ----------
rem Without this the new server fights a still-running old one serving
rem stale data -- the classic "I changed it but nothing moved".
echo [%APP_NAME%] stopping old process on port %PORT% ...
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /r /c:":%PORT% .*LISTENING"') do (
  taskkill /f /pid %%P >nul 2>&1
  echo [%APP_NAME%]   - killed pid %%P
)

rem ---------- serve (foreground) ----------
rem Browsers treat 0.0.0.0 as invalid; open the loopback alias instead.
set "OPEN_HOST=%HOST%"
if "%OPEN_HOST%"=="0.0.0.0" set "OPEN_HOST=127.0.0.1"
echo [%APP_NAME%] workspace : %WORKSPACE_ROOT%
echo [%APP_NAME%] serving   : http://%HOST%:%PORT%
echo [%APP_NAME%] (Ctrl+C to stop)
if "%OPEN%"=="1" start "" http://%OPEN_HOST%:%PORT%/
"%NODE%" "%SERVER_SCRIPT%" --root "%WORKSPACE_ROOT%" --port "%PORT%" --host "%HOST%"

endlocal
exit /b 0

:usage
echo usage: webview\start.bat [--no-open]
echo   --no-open   do not open the browser
echo   port: set PORT=9000 before starting (default 8777)
echo   bind: set HOST=0.0.0.0 to expose beyond loopback (default 127.0.0.1)
echo   root: set ROOT=D:\path to serve another workspace
echo         (default: the codeb project root)
exit /b 0