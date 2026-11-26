@echo off
setlocal enabledelayedexpansion

rem ============================================================
rem  Generic local launcher (Node / npm project)
rem
rem  Copy this file into a project root as launcher.bat, then fill
rem  in ONLY the CONFIG block below. Everything after line ~60 is
rem  project-agnostic skeleton: do not edit it per project.
rem
rem  Usage:
rem    launcher.bat              start; rebuild only when sources changed
rem    launcher.bat --rebuild    force a rebuild before starting
rem    launcher.bat --no-open    do not open the browser
rem    set PORT=6000 & launcher.bat    use another port
rem    set HOST=0.0.0.0 & launcher.bat  bind all interfaces (default loopback)
rem
rem  CONTRACT (what the skeleton assumes about your project):
rem    - BUILD_CMD  produces DIST_MARKER when it succeeds.
rem    - SERVE_CMD  is a long-running foreground command that binds
rem                 HOST:PORT. The skeleton does not background it.
rem    - PROBE_SCRIPT (optional) prints exactly "fresh" or "stale"
rem      on stdout and always exits 0. Leave empty to skip the
rem      timestamp probe (then a rebuild happens only when
rem      DIST_MARKER is missing or --rebuild is passed).
rem
rem  NOTE: keep this file ASCII-only. cmd.exe parses .bat with the
rem  OEM codepage; UTF-8 Chinese breaks lines mid-character and can
rem  corrupt goto labels under some codepage combinations.
rem ============================================================

rem ======================= CONFIG START =======================
rem Short name used in log lines.
set "APP_NAME=app"

rem Port + bind address DEFAULTS. These are only fallbacks: a PORT/HOST
rem already present in the environment wins (see "defaults" section below),
rem so `set PORT=6000 & launcher.bat` works. HOST stays loopback by default
rem -- safer when the server can show secrets.
set "DEFAULT_PORT=5478"
set "DEFAULT_HOST=127.0.0.1"

rem Absolute fallback node.exe for machines without node on PATH.
rem Leave empty to require node on PATH.
set "NODE_FALLBACK=C:\path\to\node.exe"

rem Command that builds the server/preview bundle.
set "BUILD_CMD=npm run build"

rem Artifact that must exist after a successful build. Used as the
rem "already built?" marker.
set "DIST_MARKER=build\handler.js"

rem Optional freshness probe (Node script). Empty string disables it.
rem It should compare your source/config mtimes against DIST_MARKER.
set "PROBE_SCRIPT=scripts\needs-build.mjs"

rem Foreground serve command. Use %NODE% for the resolved node path.
set "SERVE_CMD=%NODE% scripts\serve-local.mjs"
rem ======================== CONFIG END ========================

rem ---------- parse args ----------
set "OPEN=1"
set "FORCE=0"
:parse
if "%~1"=="" goto parsed
if /i "%~1"=="--no-open" set "OPEN=0"
if /i "%~1"=="--rebuild" set "FORCE=1"
if /i "%~1"=="-h" goto usage
if /i "%~1"=="--help" goto usage
shift
goto parse
:parsed

rem ---------- defaults (env overrides config) ----------
rem Only set from the DEFAULT_* fallbacks when not already in the env.
if not defined PORT set "PORT=%DEFAULT_PORT%"
if not defined HOST set "HOST=%DEFAULT_HOST%"
set "APP_DIR=%~dp0"
cd /d "%APP_DIR%"

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

rem ---------- decide whether to rebuild ----------
rem Freshness probe is optional; a missing marker always rebuilds.
set "NEED_BUILD=%FORCE%"
if not exist "%APP_DIR%%DIST_MARKER%" set "NEED_BUILD=1"
if "%NEED_BUILD%"=="1" goto build_decided
if "%PROBE_SCRIPT%"=="" goto build_decided
set "BUILD_STATE="
"%NODE%" "%PROBE_SCRIPT%" > "%TEMP%\%APP_NAME%-build-state.txt" 2>nul
if exist "%TEMP%\%APP_NAME%-build-state.txt" set /p BUILD_STATE=<"%TEMP%\%APP_NAME%-build-state.txt"
del "%TEMP%\%APP_NAME%-build-state.txt" >nul 2>&1
rem Anything other than exactly "fresh" triggers a rebuild: 20 wasted
rem seconds beat a stale bundle.
if /i not "%BUILD_STATE%"=="fresh" set "NEED_BUILD=1"
:build_decided

rem ---------- free the port ----------
rem Without this the new server fights a still-running old one that is
rem serving stale output -- the classic "I changed it but nothing moved".
echo [%APP_NAME%] stopping old process on port %PORT% ...
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /r /c:":%PORT% .*LISTENING"') do (
  taskkill /f /pid %%P >nul 2>&1
  echo [%APP_NAME%]   - killed pid %%P
)

rem ---------- build if needed ----------
if "%NEED_BUILD%"=="1" (
  echo [%APP_NAME%] sources changed - building ...
  call %BUILD_CMD%
  if errorlevel 1 (
    echo [%APP_NAME%] ERROR: build failed, not starting.
    exit /b 1
  )
) else (
  echo [%APP_NAME%] bundle is up to date - skip rebuild
)

rem ---------- serve (foreground) ----------
rem Browsers treat 0.0.0.0 as invalid; open the loopback alias instead.
set "OPEN_HOST=%HOST%"
if "%OPEN_HOST%"=="0.0.0.0" set "OPEN_HOST=127.0.0.1"
echo [%APP_NAME%] serving http://%HOST%:%PORT%
if "%OPEN%"=="1" start "" http://%OPEN_HOST%:%PORT%/
call %SERVE_CMD%

endlocal
exit /b 0

:usage
echo usage: launcher.bat [--rebuild] [--no-open]
echo   --rebuild   ignore timestamps, rebuild the bundle
echo   --no-open   do not open the browser
echo   port: set PORT=6000 before starting
echo   bind: set HOST=0.0.0.0 to expose beyond loopback
exit /b 0