::MediBot.bat - Streamlined version with coordinated debug system
@echo off
setlocal enabledelayedexpansion

:: Debug mode selection
echo ========================================
echo           MediBot Launcher
echo ========================================
echo.
echo Choose your mode:
echo 1. Normal Mode (Production)
echo 2. Debug Mode (Full diagnostics with automated checks)
echo.
set /p debug_choice="Enter your choice (1-2): "

if "!debug_choice!"=="2" (
    echo.
    echo ========================================
    echo           DEBUG MODE ACTIVATED
    echo ========================================
    echo [DEBUG] Running full diagnostic suite with automated checks...
    echo [DEBUG] This will run all checks without user interaction.
    echo [DEBUG] Results will be displayed for review.
    echo.
    goto full_debug_mode
) else if "!debug_choice!"=="1" (
    echo [INFO] Starting Normal Mode...
    goto normal_mode
) else (
    echo [ERROR] Invalid choice. Starting Normal Mode...
    goto normal_mode
)

:normal_mode
:: Normal production mode - streamlined without excessive debug output
cls
echo ========================================
echo           MediBot Starting
echo ========================================
echo.

:: Define paths with local fallbacks for F: drive dependencies
set "source_folder=C:\MEDIANSI\MediCare"
set "target_folder=C:\MEDIANSI\MediCare\CSV"
set "python_script=C:\Python34\Lib\site-packages\MediBot\update_json.py"
set "python_script2=C:\Python34\Lib\site-packages\MediBot\Medibot.py"
set "medicafe_package=medicafe"

:: Priority order: 1) Local relative path, 2) F: drive path (legacy)
set "upgrade_medicafe_local=MediBot\update_medicafe.py"
set "upgrade_medicafe_legacy=F:\Medibot\update_medicafe.py"

:: Storage and config paths with local fallbacks
set "local_storage_legacy=F:\Medibot\DOWNLOADS"
set "local_storage_local=MediBot\DOWNLOADS"
set "config_file_legacy=F:\Medibot\json\config.json"
set "config_file_local=MediBot\json\config.json"
set "temp_file_legacy=F:\Medibot\last_update_timestamp.txt"
set "temp_file_local=MediBot\last_update_timestamp.txt"

:: FIXED: Always prioritize local file if it exists
if exist "%upgrade_medicafe_local%" (
    set "upgrade_medicafe=%upgrade_medicafe_local%"
    set "use_local_update=1"
) else (
    set "use_local_update=0"
)

:: Determine which paths to use based on availability
if exist "F:\Medibot" (
    set "local_storage_path=%local_storage_legacy%"
    set "config_file=%config_file_legacy%"
    set "temp_file=%temp_file_legacy%"
    
    :: Only use F: drive update script if local doesn't exist
    if "!use_local_update!"=="0" (
        if exist "%upgrade_medicafe_legacy%" (
            set "upgrade_medicafe=%upgrade_medicafe_legacy%"
        )
    )
) else (
    set "local_storage_path=%local_storage_local%"
    set "config_file=%config_file_local%"
    set "temp_file=%temp_file_local%"
    :: Ensure local directories exist
    if not exist "MediBot\json" mkdir "MediBot\json" 2>nul
    if not exist "MediBot\DOWNLOADS" mkdir "MediBot\DOWNLOADS" 2>nul
)

set "firefox_path=C:\Program Files\Mozilla Firefox\firefox.exe"
set "claims_status_script=..\MediLink\MediLink_ClaimStatus.py"
set "deductible_script=..\MediLink\MediLink_Deductible.py"
set "package_version="
set PYTHONWARNINGS=ignore

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please run in Debug Mode to diagnose Python issues.
    pause
    exit /b 1
)

:: Check if critical directories exist
if not exist "%source_folder%" (
    echo [WARNING] Source folder not found at: %source_folder%
    set /p provide_alt_source="Enter 'Y' to provide alternate path, or any other key to continue: "
    if /i "!provide_alt_source!"=="Y" (
        set /p alt_source_folder="Enter the alternate source folder path: "
        if not "!alt_source_folder!"=="" set "source_folder=!alt_source_folder!"
    )
)

if not exist "%target_folder%" (
    mkdir "%target_folder%" 2>nul
)

:: Check if the MediCafe package is installed
python -c "import pkg_resources; print('MediCafe=='+pkg_resources.get_distribution('medicafe').version)" 2>nul
if errorlevel 1 (
    echo [WARNING] MediCafe package not found. Attempting to install...
    python -m pip install medicafe --upgrade
    if errorlevel 1 (
        echo [ERROR] Failed to install MediCafe package.
        echo Please run in Debug Mode to diagnose package issues.
        pause
        exit /b 1
    )
) else (
    for /f "tokens=2 delims==" %%i in ('python -c "import pkg_resources; print('MediCafe=='+pkg_resources.get_distribution('medicafe').version)" 2^>nul') do set "package_version=%%i"
)

:: Check for internet connectivity
ping -n 1 google.com >nul 2>&1
if errorlevel 1 (
    set "internet_available=0"
) else (
    set "internet_available=1"
)

:: Main menu
:main_menu
cls
echo.
echo ========================================
echo           MediBot Main Menu
echo ========================================
echo.
echo 1. Check for MediCafe Updates
echo 2. Download Carol's Emails
echo 3. MediBot Flow
echo 4. MediLink Flow
echo 5. United Claims Status
echo 6. United Deductible
echo 7. Process CSV Files
echo 8. Clear Cache
echo 9. Open Latest Log
echo 0. Exit
echo.

set /p choice="Enter your choice (0-9): "

if "!choice!"=="1" goto check_updates
if "!choice!"=="2" goto download_emails
if "!choice!"=="3" goto medibot_flow
if "!choice!"=="4" goto medilink_flow
if "!choice!"=="5" goto united_claims_status
if "!choice!"=="6" goto united_deductible
if "!choice!"=="7" goto process_csvs
if "!choice!"=="8" goto clear_cache
if "!choice!"=="9" goto open_latest_log
if "!choice!"=="0" goto end_script

echo Invalid choice. Please try again.
pause
goto main_menu

:: Medicafe Update
:check_updates
if "!internet_available!"=="0" (
    echo [WARNING] No internet connection available.
    goto main_menu
)

echo ========================================
echo Starting MediCafe Update Process
echo ========================================
echo.

:: Verify update script exists
if not exist "%upgrade_medicafe%" (
    echo [ERROR] Update script not found at: %upgrade_medicafe%
    echo Please run in Debug Mode to diagnose file issues.
    pause
    goto main_menu
)

echo Starting update process...
echo Update script: %upgrade_medicafe%
echo.

start "Medicafe Update" cmd /c "python \"%upgrade_medicafe%\" %package_version% & echo. & echo Update process completed. Press any key to close... & pause >nul" && (
    echo %DATE% %TIME% Upgrade initiated successfully. >> "%temp_file%"
    echo [SUCCESS] Update process started successfully
) || (
    echo %DATE% %TIME% Update failed. >> "%temp_file%"
    echo [ERROR] Upgrade failed. Check the update window for details.
)

echo.
echo Update process has been initiated.
echo All output will be displayed in the update window.
echo.
pause
goto main_menu

:: Download Carol's Emails
:download_emails
if "!internet_available!"=="0" (
    echo [WARNING] No internet connection available.
    goto main_menu
)

call :process_csvs
cls
echo Starting email download via MediCafe...
cd /d "%~dp0.."
python -m MediCafe download_emails
if errorlevel 1 (
    echo [ERROR] Failed to download emails.
    pause
)

pause
goto main_menu

:: MediBot Flow
:medibot_flow
cls
echo Starting MediBot flow...
cd /d "%~dp0.."
python -m MediCafe medibot
if errorlevel 1 (
    echo [ERROR] Failed to start MediBot flow.
    pause
)

pause
goto main_menu

:: MediLink Flow
:medilink_flow
cls
echo Starting MediLink flow...
cd /d "%~dp0.."
python -m MediCafe medilink
if errorlevel 1 (
    echo [ERROR] Failed to start MediLink flow.
    pause
)

pause
goto main_menu

:: United Claims Status
:united_claims_status
cls
echo Starting United Claims Status...
cd /d "%~dp0.."
python -m MediCafe claims_status
if errorlevel 1 (
    echo [ERROR] Failed to start United Claims Status.
    pause
)

pause
goto main_menu

:: United Deductible
:united_deductible
cls
echo Starting United Deductible...
cd /d "%~dp0.."
python -m MediCafe deductible
if errorlevel 1 (
    echo [ERROR] Failed to start United Deductible.
    pause
)

pause
goto main_menu

:: Process CSV Files
:process_csvs
if not exist "%source_folder%" (
    echo [ERROR] Source folder not found at: %source_folder%
    pause
    goto main_menu
)

if not exist "%target_folder%" (
    mkdir "%target_folder%" 2>nul
    if errorlevel 1 (
        echo [ERROR] Failed to create target folder
        pause
        goto main_menu
    )
)

copy "%source_folder%\*.csv" "%target_folder%\" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to copy CSV files
    pause
    goto main_menu
) else (
    echo [SUCCESS] Successfully copied CSV files
)

pause
goto main_menu

:: Clear Cache
:clear_cache
echo Clearing Python cache...
python -Bc "import compileall; compileall.compile_dir('.', force=True)" 2>nul
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
echo [SUCCESS] Cache cleared successfully

pause
goto main_menu

:: Open Latest Log
:open_latest_log
for /f "delims=" %%i in ('dir /b /o-d *.log 2^>nul') do (
    start notepad "%%i"
    goto main_menu
)
echo [WARNING] No log files found
pause
goto main_menu

:: End Script
:end_script
echo Exiting MediBot
exit /b 0

:: Full Debug Mode - Automated checks with no user interaction
:full_debug_mode
echo [DEBUG] ========================================
echo [DEBUG] FULL DEBUG MODE - AUTOMATED CHECKS
echo [DEBUG] ========================================
echo [DEBUG] Running all diagnostic checks automatically...
echo [DEBUG] No user interaction required - results will be displayed.
echo.

:: Step 1: F: Drive Diagnostic (automated)
echo [DEBUG] Step 1: F: Drive Diagnostic
echo [DEBUG] ========================================
call "f_drive_diagnostic.bat" >nul 2>&1
if errorlevel 1 (
    echo [DEBUG] F: Drive Diagnostic completed with issues
) else (
    echo [DEBUG] F: Drive Diagnostic completed successfully
)
echo.

:: Step 2: Crash Diagnostic (automated)
echo [DEBUG] Step 2: Crash Diagnostic
echo [DEBUG] ========================================
call "crash_diagnostic.bat" >nul 2>&1
if errorlevel 1 (
    echo [DEBUG] Crash Diagnostic completed with issues
) else (
    echo [DEBUG] Crash Diagnostic completed successfully
)
echo.

:: Step 3: Basic Debug (automated)
echo [DEBUG] Step 3: Basic Debug
echo [DEBUG] ========================================
call "MediBot_debug.bat" >nul 2>&1
if errorlevel 1 (
    echo [DEBUG] Basic Debug completed with issues
) else (
    echo [DEBUG] Basic Debug completed successfully
)
echo.

:: Step 4: Fixed Version Test (automated)
echo [DEBUG] Step 4: Fixed Version Test
echo [DEBUG] ========================================
call "MediBot_fixed.bat" >nul 2>&1
if errorlevel 1 (
    echo [DEBUG] Fixed Version Test completed with issues
) else (
    echo [DEBUG] Fixed Version Test completed successfully
)
echo.

:: Step 5: Additional automated checks
echo [DEBUG] Step 5: Additional System Checks
echo [DEBUG] ========================================

:: Check Python installation
echo [DEBUG] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
) else (
    echo [OK] Python found and accessible
)

:: Check MediCafe package
echo [DEBUG] Checking MediCafe package...
python -c "import pkg_resources; print('MediCafe=='+pkg_resources.get_distribution('medicafe').version)" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] MediCafe package not found
) else (
    echo [OK] MediCafe package found
)

:: Check internet connectivity
echo [DEBUG] Checking internet connectivity...
ping -n 1 google.com >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No internet connection
) else (
    echo [OK] Internet connection available
)

:: Check local update script
echo [DEBUG] Checking local update script...
if exist "MediBot\update_medicafe.py" (
    echo [OK] Local update script found
) else (
    echo [ERROR] Local update script not found
)

:: Check F: drive accessibility
echo [DEBUG] Checking F: drive accessibility...
if exist "F:\" (
    echo [OK] F: drive accessible
    if exist "F:\Medibot\update_medicafe.py" (
        echo [OK] F: drive update script found
    ) else (
        echo [WARNING] F: drive update script not found
    )
) else (
    echo [ERROR] F: drive not accessible
)

echo.
echo [DEBUG] ========================================
echo [DEBUG] ALL AUTOMATED CHECKS COMPLETED
echo [DEBUG] ========================================
echo [DEBUG] Review the output above for any issues.
echo [DEBUG] The system will continue to normal mode.
echo.
echo [DEBUG] Press Enter to continue to normal mode...
pause >nul

:: Continue to normal mode after debug
goto normal_mode