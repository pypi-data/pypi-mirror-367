::MediBot.bat - Updated to use MediCafe entry point
@echo off
setlocal enabledelayedexpansion

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

:: Determine which paths to use based on availability
if exist "F:\Medibot" (
    set "local_storage_path=%local_storage_legacy%"
    set "config_file=%config_file_legacy%"
    set "temp_file=%temp_file_legacy%"
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

:: Check if Python is installed and the path is correctly set
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not added to PATH.
    exit /b
)

:: Check if critical directories exist
if not exist "%source_folder%" (
    echo.
    echo Warning: Source folder not found at: %source_folder%
    echo.
    echo Would you like to provide an alternate path for the source folder?
    set /p provide_alt_source="Enter 'Y' to provide alternate path, or any other key to continue: "
    if /i "!provide_alt_source!"=="Y" (
        echo.
        echo Please enter the full path to your source folder.
        echo Example: C:\MediCare\Data
        echo Example with spaces: "G:\My Drive\MediCare\Data"
        echo.
        echo Note: If your path contains spaces, please include quotes around the entire path.
        echo.
        set /p alt_source_path="Enter source folder path: "
        :: Remove any surrounding quotes from user input and re-add them for consistency
        set "alt_source_path=!alt_source_path:"=!"
        if exist "!alt_source_path!" (
            echo Source folder found at: !alt_source_path!
            set "source_folder=!alt_source_path!"
        ) else (
            echo Source folder not found at: !alt_source_path!
            echo Continuing with default path...
        )
    ) else (
        echo Continuing with default path...
    )
)

if not exist "%local_storage_path%" (
    echo.
    echo Warning: Local storage path not found at: %local_storage_path%
    echo.
    echo Would you like to provide an alternate path for the local storage?
    set /p provide_alt_storage="Enter 'Y' to provide alternate path, or any other key to continue: "
    if /i "!provide_alt_storage!"=="Y" (
        echo.
        echo Please enter the full path to your local storage folder.
        echo Example: C:\MediBot\Downloads
        echo Example with spaces: "G:\My Drive\MediBot\Downloads"
        echo.
        echo Note: If your path contains spaces, please include quotes around the entire path.
        echo.
        set /p alt_storage_path="Enter local storage path: "
        :: Remove any surrounding quotes from user input and re-add them for consistency
        set "alt_storage_path=!alt_storage_path:"=!"
        if exist "!alt_storage_path!" (
            echo Local storage folder found at: !alt_storage_path!
            set "local_storage_path=!alt_storage_path!"
        ) else (
            echo Local storage folder not found at: !alt_storage_path!
            echo Continuing with default path...
        )
    ) else (
        echo Continuing with default path...
    )
)

if not exist "%target_folder%" (
    echo.
    echo Warning: Target folder not found at: %target_folder%
    echo.
    echo Would you like to provide an alternate path for the target folder?
    set /p provide_alt_target="Enter 'Y' to provide alternate path, or any other key to continue: "
    if /i "!provide_alt_target!"=="Y" (
        echo.
        echo Please enter the full path to your target folder.
        echo Example: C:\MediCare\CSV
        echo Example with spaces: "G:\My Drive\MediCare\CSV"
        echo.
        echo Note: If your path contains spaces, please include quotes around the entire path.
        echo.
        set /p alt_target_path="Enter target folder path: "
        :: Remove any surrounding quotes from user input and re-add them for consistency
        set "alt_target_path=!alt_target_path:"=!"
        if exist "!alt_target_path!" (
            echo Target folder found at: !alt_target_path!
            set "target_folder=!alt_target_path!"
        ) else (
            echo Target folder not found at: !alt_target_path!
            echo Continuing with default path...
        )
    ) else (
        echo Continuing with default path...
    )
)

:: Check if the MediCafe package is installed and retrieve its version
echo Checking for installed MediCafe package version...
python -c "import pkg_resources; print('MediCafe=='+pkg_resources.get_distribution('medicafe').version)" > temp.txt 2>nul
set /p package_version=<temp.txt
del temp.txt

if not defined package_version (
    echo MediCafe package version not detected or MediCafe not installed. Consider manual re-install.
    exit /b
)

:: Extract version number and display it
for /f "tokens=2 delims==" %%a in ("%package_version%") do (
    set "medicafe_version=%%a"
)

if not defined medicafe_version (
    echo Failed to detect MediCafe version.
) else (
    echo Detected MediCafe version: %medicafe_version%
    ping -n 2 127.0.0.1 >nul
)

:: Check for internet connectivity
ping -n 1 google.com > nul 2>&1
if %ERRORLEVEL% neq 0 (
    set "internet_available=0"
    echo No internet connection detected.
) else (
    set "internet_available=1"
    echo Internet connection detected.
)

:: Common pre-menu setup
echo Setting up the environment...
if not exist "%config_file%" (
    echo Configuration file missing.
    echo.
    echo Expected configuration file path: %config_file%
    echo.
    echo Would you like to provide an alternate path for the configuration file?
    set /p provide_alt="Enter 'Y' to provide alternate path, or any other key to exit: "
    if /i "!provide_alt!"=="Y" (
        echo.
        echo Please enter the full path to your configuration file.
        echo Example: C:\MediBot\config\config.json
        echo Example with spaces: "G:\My Drive\MediBot\config\config.json"
        echo.
        echo Note: If your path contains spaces, please include quotes around the entire path.
        echo.
        set /p alt_config_path="Enter configuration file path: "
        :: Remove any surrounding quotes from user input and re-add them for consistency
        set "alt_config_path=!alt_config_path:"=!"
        if exist "!alt_config_path!" (
            echo Configuration file found at: !alt_config_path!
            set "config_file=!alt_config_path!"
            goto config_check_complete
        ) else (
            echo Configuration file not found at: !alt_config_path!
            echo.
            set /p retry="Would you like to try another path? (Y/N): "
            if /i "!retry!"=="Y" (
                goto retry_config_path
            ) else (
                goto end_script
            )
        )
    ) else (
        goto end_script
    )
) else (
    goto config_check_complete
)

:retry_config_path
echo.
echo Please enter the full path to your configuration file.
echo Example: C:\MediBot\config\config.json
echo Example with spaces: "G:\My Drive\MediBot\config\config.json"
echo.
echo Note: If your path contains spaces, please include quotes around the entire path.
echo.
set /p alt_config_path="Enter configuration file path: "
:: Remove any surrounding quotes from user input and re-add them for consistency
set "alt_config_path=!alt_config_path:"=!"
if exist "!alt_config_path!" (
    echo Configuration file found at: !alt_config_path!
    set "config_file=!alt_config_path!"
) else (
    echo Configuration file not found at: !alt_config_path!
    echo.
    set /p retry="Would you like to try another path? (Y/N): "
    if /i "!retry!"=="Y" (
        goto retry_config_path
    ) else (
        goto end_script
    )
)

:config_check_complete

:: Check if the file exists and attempt to copy it to the local directory
echo Checking for the update script...
ping -n 2 127.0.0.1 >nul

:: DIAGNOSTIC SECTION - Analyze F: drive accessibility
echo.
echo ==========================================
echo F: DRIVE ACCESSIBILITY DIAGNOSTICS
echo ==========================================
echo.

:: Check if F: drive exists at all
echo [DIAGNOSTIC] Checking F: drive existence...
if exist "F:\" (
    echo [OK] F: drive is accessible
    
    :: Check F: drive properties
    echo [DIAGNOSTIC] F: drive properties:
    dir F:\ | find "Directory of" 2>nul || echo [!] Cannot read F: drive directory listing
    
    :: Check available space
    echo [DIAGNOSTIC] F: drive free space:
    dir F:\ | find "bytes free" 2>nul || echo [!] Cannot determine free space
    
    :: Check if F:\Medibot directory exists
    echo [DIAGNOSTIC] Checking F:\Medibot directory...
    if exist "F:\Medibot" (
        echo [OK] F:\Medibot directory exists
        
        :: Check directory permissions by attempting to create a test file
        echo [DIAGNOSTIC] Testing write permissions to F:\Medibot...
        echo test > "F:\Medibot\permission_test.tmp" 2>nul
        if exist "F:\Medibot\permission_test.tmp" (
            echo [OK] Write permissions confirmed
            del "F:\Medibot\permission_test.tmp" >nul 2>&1
        ) else (
            echo [ERROR] PERMISSION DENIED - Cannot write to F:\Medibot
            echo [ERROR] This is likely the cause of the path error!
        )
        
        :: List contents of F:\Medibot
        echo [DIAGNOSTIC] F:\Medibot directory contents:
        dir /b "F:\Medibot" 2>nul || echo [!] Cannot list directory contents (permission issue?)
        
        :: Check if update_medicafe.py specifically exists
        echo [DIAGNOSTIC] Checking for update_medicafe.py...
        if exist "F:\Medibot\update_medicafe.py" (
            echo [OK] update_medicafe.py found at F:\Medibot\update_medicafe.py
            echo [DIAGNOSTIC] File details:
            dir "F:\Medibot\update_medicafe.py" 2>nul || echo [!] Cannot read file details
            
            :: Test file accessibility by attempting to read it
            echo [DIAGNOSTIC] Testing file read permissions...
            type "F:\Medibot\update_medicafe.py" | find "#update_medicafe.py" >nul 2>&1
            if %errorlevel% equ 0 (
                echo [OK] File is readable
            ) else (
                                 echo [ERROR] FILE READ ERROR - Cannot read update_medicafe.py
                echo [ERROR] File exists but is not accessible (permission/lock issue?)
            )
        ) else (
                         echo [ERROR] update_medicafe.py NOT FOUND at F:\Medibot\update_medicafe.py
        )
        
    ) else (
                 echo [ERROR] F:\Medibot directory does NOT exist
        echo [DIAGNOSTIC] Attempting to create F:\Medibot...
        mkdir "F:\Medibot" 2>nul
        if exist "F:\Medibot" (
            echo [OK] Successfully created F:\Medibot directory
        ) else (
            echo [ERROR] FAILED to create F:\Medibot directory
            echo [ERROR] Permission denied or F: drive is read-only
        )
    )
    
) else (
    echo [ERROR] F: drive is NOT accessible
    echo [ERROR] F: drive may be:
    echo    - Disconnected network drive
    echo    - Unmounted USB/external drive  
    echo    - Mapped drive that's no longer available
    echo    - Security policy blocking access
    
    :: Check what drives are actually available
    echo [DIAGNOSTIC] Available drives on this system:
    wmic logicaldisk get size,freespace,caption 2>nul || echo [!] Cannot enumerate drives
)

echo.
echo ==========================================
echo END F: DRIVE DIAGNOSTICS
echo ==========================================
echo.

:: Continue with existing logic but with enhanced error reporting
:: First check if we already have it locally
if exist "%upgrade_medicafe_local%" (
    echo Found update_medicafe.py in local directory. No action needed.
    ping -n 2 127.0.0.1 >nul
) else if exist "C:\Python34\Lib\site-packages\MediBot\update_medicafe.py" (
    echo Found update_medicafe.py in site-packages. Copying to local directory...
    ping -n 2 127.0.0.1 >nul
    :: Ensure MediBot directory exists
    if not exist "MediBot" mkdir "MediBot"
    copy "C:\Python34\Lib\site-packages\MediBot\update_medicafe.py" "%upgrade_medicafe_local%" >nul 2>&1
    if %errorlevel% neq 0 (
        echo Copy to local directory failed. Error code: %errorlevel%
        echo [DIAGNOSTIC] Attempting copy to F: drive (with detailed error reporting)...
        ping -n 2 127.0.0.1 >nul
        :: Ensure F:\Medibot directory exists (only if F: drive is accessible)
        if exist "F:\" (
            if not exist "F:\Medibot" (
                echo [DIAGNOSTIC] Creating F:\Medibot directory...
                mkdir "F:\Medibot" 2>nul
                if not exist "F:\Medibot" (
                    echo [ERROR] Failed to create F:\Medibot - Permission denied or read-only drive
                )
            )
            if exist "F:\Medibot" (
                echo [DIAGNOSTIC] Attempting file copy to F:\Medibot...
                copy "C:\Python34\Lib\site-packages\MediBot\update_medicafe.py" "%upgrade_medicafe_legacy%" 2>nul
                if %errorlevel% neq 0 (
                    echo [ERROR] Copy to F:\Medibot failed with error code: %errorlevel%
                    echo [ERROR] Possible causes:
                    echo    - Permission denied (insufficient write access)
                    echo    - Disk full
                    echo    - File locked by another process
                    echo    - Antivirus blocking the operation
                ) else (
                    echo [SUCCESS] File copied to F:\Medibot successfully
                )
            )
        ) else (
            echo [ERROR] F: drive not accessible - skipping F: drive copy attempt
        )
    ) else (
        echo File copied to local directory successfully.
        ping -n 2 127.0.0.1 >nul
    )
) else if exist "%upgrade_medicafe_legacy%" (
    echo Found update_medicafe.py in legacy F: drive location.
    echo [DIAGNOSTIC] Verifying F: drive file accessibility...
    type "%upgrade_medicafe_legacy%" | find "#update_medicafe.py" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] F: drive file is accessible and readable
    ) else (
        echo [ERROR] F: drive file exists but cannot be read (permission/lock issue)
    )
    ping -n 2 127.0.0.1 >nul
) else (
    echo update_medicafe.py not detected in any known location.
    echo.
    echo Checked locations:
    echo   - Site-packages: C:\Python34\Lib\site-packages\MediBot\update_medicafe.py
    echo   - Local: %upgrade_medicafe_local%
    echo   - Legacy: %upgrade_medicafe_legacy%
    echo.
    echo [DIAGNOSTIC] Current working directory:
    cd
    echo [DIAGNOSTIC] Current directory contents:
    dir /b
    echo.
    echo [DIAGNOSTIC] MediBot directory contents:
    dir /b MediBot\ 2>nul || echo MediBot directory not found
    echo.
    echo Continuing without update script...
    ping -n 2 127.0.0.1 >nul
)
)

:: Main menu
:main_menu
cls
echo Version: %medicafe_version%
echo --------------------------------------------------------------
echo                .//*  Welcome to MediCafe  *\\. 
echo --------------------------------------------------------------
echo. 

echo Please select an option:
echo.
if "!internet_available!"=="1" (
    echo 1. Update MediCafe
    echo.
    echo 2. Download Email de Carol
    echo.
    echo 3. MediLink Claims
    echo.
    echo 4. ^[United^] Claims Status
    echo.
    echo 5. ^[United^] Deductible
    echo.
)
echo 6. Run MediBot
echo.
echo 7. Troubleshooting: Open Log File
echo.
echo 8. Troubleshooting: Clear Python Cache
echo.
echo 9. Exit
echo.
set /p choice=Enter your choice:  

:: Update option numbers
if "!choice!"=="9" goto end_script
if "!choice!"=="8" goto clear_cache
if "!choice!"=="7" goto open_latest_log
if "!choice!"=="6" goto medibot_flow
if "!choice!"=="5" goto united_deductible
if "!choice!"=="4" goto united_claims_status
if "!choice!"=="3" goto medilink_flow
if "!choice!"=="2" goto download_emails
if "!choice!"=="1" goto check_updates

:: Invalid choice - return to menu
echo Invalid choice. Please try again.
pause
goto main_menu

:: Medicafe Update
:check_updates
if "!internet_available!"=="0" (
    echo No internet connection available.
    goto main_menu
)

echo ========================================
echo DEBUG: Starting MediCafe Update Process
echo ========================================
echo.
echo Current working directory: %CD%
echo Package version: %package_version%
echo Update script path: %upgrade_medicafe%
echo.
echo Press Enter to continue to step 1...
pause >nul

:: Step 1: Check if update_medicafe.py exists in expected location
echo.
echo ========================================
echo DEBUG STEP 1: Checking for update script
echo ========================================
echo.
echo Checking for update script (priority: local first, then legacy path)...
if exist "%upgrade_medicafe_local%" (
    echo [SUCCESS] Found update script at: %upgrade_medicafe_local%
    echo File size: 
    dir "%upgrade_medicafe_local%" | find "update_medicafe.py"
    set "upgrade_medicafe=%upgrade_medicafe_local%"
) else if exist "%upgrade_medicafe_legacy%" (
    echo [SUCCESS] Found update script at legacy location: %upgrade_medicafe_legacy%
    echo File size: 
    dir "%upgrade_medicafe_legacy%" | find "update_medicafe.py"
    set "upgrade_medicafe=%upgrade_medicafe_legacy%"
) else (
    echo [FAILED] Update script not found in either location:
    echo   - Local: %upgrade_medicafe_local%
    echo   - Legacy: %upgrade_medicafe_legacy%
    echo.
    echo Available files in current directory:
    dir /b
    echo.
    echo Available files in MediBot directory:
    dir /b MediBot\ 2>nul || echo MediBot directory not found
    )
)
echo.
echo Press Enter to continue to step 2...
pause >nul

:: Step 2: Verify Python installation and path
echo.
echo ========================================
echo DEBUG STEP 2: Python Environment Check
echo ========================================
echo.
echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH
    echo Current PATH: %PATH%
) else (
    echo [SUCCESS] Python found
    echo Python executable: %PYTHONPATH%
    echo Python version:
    python --version
)
echo.
echo Checking pip installation...
python -m pip --version
if %errorlevel% neq 0 (
    echo [ERROR] pip not found
) else (
    echo [SUCCESS] pip found
    echo pip version:
    python -m pip --version
)
echo.
echo Press Enter to continue to step 3...
pause >nul

:: Step 3: Check MediCafe package installation
echo.
echo ========================================
echo DEBUG STEP 3: MediCafe Package Check
echo ========================================
echo.
echo Checking MediCafe package installation...
python -c "import pkg_resources; print('MediCafe=='+pkg_resources.get_distribution('medicafe').version)" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] MediCafe package not found or error accessing
    echo.
    echo Checking if MediCafe is importable...
    python -c "import MediCafe; print('MediCafe module found')" 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] MediCafe module not importable
    ) else (
        echo [SUCCESS] MediCafe module is importable
    )
) else (
    echo [SUCCESS] MediCafe package found
    echo Package version: %package_version%
)
echo.
echo Press Enter to continue to step 4...
pause >nul

:: Step 4: Check internet connectivity
echo.
echo ========================================
echo DEBUG STEP 4: Internet Connectivity
echo ========================================
echo.
echo Testing internet connectivity...
ping -n 1 google.com >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No internet connection detected
    echo Cannot proceed with update without internet
    echo.
    echo Press Enter to return to main menu...
    pause >nul
    goto main_menu
) else (
    echo [SUCCESS] Internet connection detected
    echo Testing PyPI connectivity...
    python -c "import requests; print('PyPI accessible:', requests.get('https://pypi.org/pypi/medicafe/json', timeout=5).status_code)" 2>nul
    if %errorlevel% neq 0 (
        echo [WARNING] PyPI connectivity test failed
    ) else (
        echo [SUCCESS] PyPI connectivity confirmed
    )
)
echo.
echo Press Enter to continue to step 5...
pause >nul

:: Step 5: Attempt update with detailed logging
echo.
echo ========================================
echo DEBUG STEP 5: Starting Update Process
echo ========================================
echo.
echo Starting update process...
echo.

:: Check if update_medicafe.py exists using the new priority system
if exist "%upgrade_medicafe_local%" (
    echo [INFO] Using local update script at: %upgrade_medicafe_local%
    echo Command: python "%upgrade_medicafe_local%" %package_version%
    
    :: Pre-execution diagnostics
    echo.
    echo [DIAGNOSTIC] Pre-execution checks for local script:
    echo [DIAGNOSTIC] File size and permissions:
    dir "%upgrade_medicafe_local%" 2>nul || echo [!] Cannot read file details
    echo [DIAGNOSTIC] Testing Python access to file:
    python -c "import os; print('[OK] Python can access file') if os.path.exists('%upgrade_medicafe_local%') else print('[ERROR] Python cannot access file')" 2>nul || echo [!] Python test failed
    
    echo.
    echo Press Enter to execute update command...
    pause >nul
    echo.
    echo Executing update command...
    echo.
    echo The update window will open and show detailed progress.
    echo All output will be displayed on screen.
    echo.
    start "Medicafe Update" cmd /c "echo [DIAGNOSTIC] About to execute: python \"%upgrade_medicafe_local%\" %package_version% & echo. & python \"%upgrade_medicafe_local%\" %package_version% & echo. & echo [DIAGNOSTIC] Python exit code: %ERRORLEVEL% & echo Update process completed. Press any key to close... & pause >nul" && (
        echo %DATE% %TIME% Upgrade initiated successfully (local). >> "%temp_file%"
        echo [SUCCESS] Update process started successfully
        echo All output will be displayed in the update window.
    ) || (
        echo %DATE% %TIME% Update failed (local). >> "%temp_file%"
        echo [ERROR] Upgrade failed. Check the update window for details.
        echo [DIAGNOSTIC] Possible causes for local script failure:
        echo    - Python not in PATH
        echo    - Script syntax error
        echo    - Missing Python dependencies
        echo    - File corruption
    )
) else if exist "%upgrade_medicafe_legacy%" (
    echo [INFO] Using legacy update script at: %upgrade_medicafe_legacy%
    echo Command: python "%upgrade_medicafe_legacy%" %package_version%
    
    :: Pre-execution diagnostics for F: drive
    echo.
    echo [DIAGNOSTIC] Pre-execution checks for F: drive script:
    echo [DIAGNOSTIC] File size and permissions:
    dir "%upgrade_medicafe_legacy%" 2>nul || echo [!] Cannot read file details
    echo [DIAGNOSTIC] Testing Python access to F: drive file:
    python -c "import os; print('[OK] Python can access F: drive file') if os.path.exists('%upgrade_medicafe_legacy%') else print('[ERROR] Python cannot access F: drive file')" 2>nul || echo [!] Python F: drive test failed
    echo [DIAGNOSTIC] Testing file read permissions:
    type "%upgrade_medicafe_legacy%" | find "#update_medicafe.py" >nul 2>&1 && echo [OK] File content readable || echo [ERROR] Cannot read file content
    
    echo.
    echo Press Enter to execute update command...
    pause >nul
    echo.
    echo Executing update command...
    start "Medicafe Update" cmd /c "echo [DIAGNOSTIC] About to execute: python \"%upgrade_medicafe_legacy%\" %package_version% & echo [DIAGNOSTIC] F: drive accessibility test... & dir F:\ ^| find \"Directory of\" ^>nul 2^>^&1 ^&^& echo [OK] F: drive accessible ^|^| echo [ERROR] F: drive access lost & echo. & python \"%upgrade_medicafe_legacy%\" %package_version% & echo. & echo [DIAGNOSTIC] Python exit code: %ERRORLEVEL% & echo Update process completed. Press any key to close... & pause >nul" && (
        echo %DATE% %TIME% Upgrade initiated successfully (legacy). >> "%temp_file%"
        echo [SUCCESS] Update process started successfully
        echo All output will be displayed in the update window.
    ) || (
        echo %DATE% %TIME% Update failed (legacy). >> "%temp_file%"
        echo [ERROR] Upgrade failed. Check the update window for details.
        echo [DIAGNOSTIC] Possible causes for F: drive script failure:
        echo    - F: drive disconnected during execution
        echo    - Permission denied accessing F: drive
        echo    - F: drive file locked by antivirus
        echo    - Network drive timeout
        echo    - Python cannot access network paths
    )
) else (
    echo [ERROR] update_medicafe.py not found in either location
    echo Expected locations:
    echo   - Local: %upgrade_medicafe_local%
    echo   - Legacy: %upgrade_medicafe_legacy%
    echo.
    echo Current directory contents:
    dir /b
    echo.
    echo MediBot directory contents:
    dir /b MediBot\ 2>nul || echo MediBot directory not found
    echo.
    echo %DATE% %TIME% Update failed - script not found. >> "%temp_file%"
    echo.
    echo Press Enter to return to main menu...
    pause >nul
    goto main_menu
)

echo.
echo ========================================
echo DEBUG: Update Process Complete
echo ========================================
echo.
echo Update process has been initiated.
echo All output will be displayed in the update window.
echo.
echo Press Enter to return to main menu...
pause >nul
goto main_menu

:: Download Carol's Emails - Using MediCafe entry point
:download_emails
if "!internet_available!"=="0" (
    echo No internet connection available.
    goto main_menu
)
call :process_csvs
cls
echo Starting email download via MediCafe...
cd /d "%~dp0.."
python -m MediCafe download_emails
if errorlevel 1 (
    echo Failed to download emails.
    pause
)
goto main_menu

:: Run MediBot Flow
:medibot_flow
call :process_csvs
cls
echo Starting MediBot via MediCafe...
cd /d "%~dp0.."
python -m MediCafe medibot "%config_file%"
if errorlevel 1 echo Failed to run MediBot.
pause
goto main_menu

:: Continue to MediLink
:medilink_flow
if "!internet_available!"=="0" (
    echo No internet connection available.
    goto main_menu
)
call :process_csvs
cls
:: move this path.
cd /d "%~dp0.."
python -m MediCafe medilink
if errorlevel 1 echo MediLink failed to execute.
pause
goto main_menu

:: United Claims Status
:united_claims_status
if "!internet_available!"=="0" (
    echo No internet connection available.
    goto main_menu
)
cls
echo Loading United Claims Status...
cd /d "%~dp0.."
python -m MediCafe claims_status
if errorlevel 1 echo Failed to check United Claims Status.
pause
goto main_menu

:: United Deductible
:united_deductible
if "!internet_available!"=="0" (
    echo No internet connection available.
    goto main_menu
)
cls
echo Loading United Deductible...
cd /d "%~dp0.."
python -m MediCafe deductible
if errorlevel 1 echo Failed to check United Deductible.
pause
goto main_menu

:: Process CSV Files and Validate Against Config
:process_csvs

:: Check if the Python script for JSON updates exists
if not exist "%python_script%" (
    echo.
    echo Warning: Python script for JSON updates not found at: %python_script%
    echo.
    echo Would you like to provide an alternate path for the JSON update script?
    set /p provide_alt_json="Enter 'Y' to provide alternate path, or any other key to continue: "
    if /i "!provide_alt_json!"=="Y" (
        echo.
        echo Please enter the full path to your update_json.py file.
        echo Example: C:\MediBot\scripts\update_json.py
        echo Example with spaces: "G:\My Drive\MediBot\scripts\update_json.py"
        echo.
        echo Note: If your path contains spaces, please include quotes around the entire path.
        echo.
        set /p alt_json_path="Enter JSON update script path: "
        :: Remove any surrounding quotes from user input and re-add them for consistency
        set "alt_json_path=!alt_json_path:"=!"
        if exist "!alt_json_path!" (
            echo JSON update script found at: !alt_json_path!
            set "python_script=!alt_json_path!"
        ) else (
            echo JSON update script not found at: !alt_json_path!
            echo Continuing without JSON update script...
        )
    ) else (
        echo Continuing without JSON update script...
    )
)

:: Move CSV files from local_storage_path to source_folder in case AK sends it unencrypted by accident.
echo Checking for new CSV files in local storage...
for %%f in ("%local_storage_path%\*.csv") do (
    echo WARNING: Found CSV files!
    echo Moving %%f to %source_folder%...
    move "%%f" "%source_folder%" >nul 2>&1
    if errorlevel 1 (
        echo Failed to move %%f. Check permissions or path.
    ) else (
        echo Moved %%f successfully.
    )
)

:: Retrieve the current time and date to create a timestamp
for /f "tokens=1-5 delims=/: " %%a in ('echo %time%') do (
    set "hour=%%a"
    set "minute=%%b"
    set "second=%%c"
)
for /f "tokens=2-4 delims=/ " %%a in ('echo %date%') do (
    set "day=%%a"
    set "month=%%b"
    set "year=%%c"
)
set "timestamp=!year!!month!!day!_!hour!!minute!"

:: Search for the most recent CSV file in source folder
set "latest_csv="
for /f "delims=" %%a in ('dir /b /a-d /o-d "%source_folder%\*.csv" 2^>nul') do (
    set "latest_csv=%%a"
    echo Found New CSV Files...
    goto process_found_csv
)
goto :eof

:process_found_csv
echo Validating latest CSV with config file...
:: Run Python script to get current CSV path from JSON
for /f "delims=" %%a in ('python "%python_script%" "%config_file%"') do (
    set "current_csv=%%a"
)

:: Extract filenames from paths
for %%f in ("!current_csv!") do set "current_csv_name=%%~nxf"
for %%f in ("%target_folder%\!latest_csv!") do set "latest_csv_name=%%~nxf"

:: Compare the paths and prompt user if necessary
if not "!current_csv_name!"=="!latest_csv_name!" (
    echo.
    echo ALERT: Config file CSV path differs from the latest CSV. This can happen if a new CSV is downloaded.
    echo Current CSV: !current_csv_name!
    echo Latest CSV: !latest_csv_name!
    echo.
    set /p update_choice="Do you want to update to the latest CSV? (Y/N): "
    if /i "!update_choice!"=="Y" (
        echo Updating config file with latest CSV...
        py "%python_script%" "%config_file%" "%target_folder%\!latest_csv!"
        echo Config file updated.
    ) else (
        echo Using existing CSV path from config.
    )
) else (
    echo CSV path in config matches the latest CSV.
)

move "%source_folder%\!latest_csv!" "%target_folder%\SX_CSV_!timestamp!.csv"
set "new_csv_path=%target_folder%\SX_CSV_!timestamp!.csv"
echo Processing CSV...
py "%python_script%" "%config_file%" "!new_csv_path!"
echo CSV Processor Complete...
goto :eof

:: Clear Python Cache
:clear_cache
cls
echo Clearing Python cache for MediCafe...
echo.
cd /d "%~dp0.."

:: Check if update_medicafe.py exists using priority system (local first)
if exist "%upgrade_medicafe_local%" (
    echo Found update_medicafe.py in local location - using relative path
    echo [DIAGNOSTIC] Cache clearing with local script:
    echo [DIAGNOSTIC] Command: python "%upgrade_medicafe_local%" --clear-cache
    python "%upgrade_medicafe_local%" --clear-cache
    if %errorlevel% neq 0 (
        echo [ERROR] Cache clearing failed with local script, error code: %errorlevel%
        echo [DIAGNOSTIC] Possible causes:
        echo    - Python not in PATH
        echo    - Script syntax error
        echo    - Missing dependencies
    )
) else if exist "%upgrade_medicafe_legacy%" (
    echo Found update_medicafe.py in legacy location - using F: drive path
    echo [DIAGNOSTIC] Cache clearing with F: drive script:
    echo [DIAGNOSTIC] Command: python "%upgrade_medicafe_legacy%" --clear-cache
    echo [DIAGNOSTIC] Testing F: drive access before execution:
    dir "F:\Medibot" >nul 2>&1 && echo [OK] F: drive accessible || echo [ERROR] F: drive access issue
    python "%upgrade_medicafe_legacy%" --clear-cache
    if %errorlevel% neq 0 (
        echo [ERROR] Cache clearing failed with F: drive script, error code: %errorlevel%
        echo [DIAGNOSTIC] Possible causes:
        echo    - F: drive disconnected during execution
        echo    - Permission denied accessing F: drive file
        echo    - F: drive file locked
        echo    - Python cannot access network paths
    )
) else (
    echo ERROR: update_medicafe.py not found in either location
    echo Expected locations:
    echo   - Local: %upgrade_medicafe_local%
    echo   - Legacy: %upgrade_medicafe_legacy%
    pause
    goto main_menu
)

if errorlevel 1 (
    echo Cache clearing failed.
    pause
) else (
    echo Cache clearing completed successfully.
    pause
)
goto main_menu

:: Exit Script
:end_script
echo Exiting MediCafe.
pause
exit /b

:: Open Latest Log
:open_latest_log
echo Opening the latest log file...
set "latest_log="

:: Attempt to find any files in the directory
echo Attempting to locate files in %local_storage_path%...

:: Method 1: Check for any files
echo Attempt #1: Checking for any files...
dir "%local_storage_path%\*" >nul 2>&1
if %errorlevel% == 0 (
    echo Files found in %local_storage_path%.
) else (
    echo No files found in %local_storage_path%.
    pause
    goto main_menu
)

:: Method 2: Check for .log files specifically
echo Attempt #2: Checking for .log files...
dir "%local_storage_path%\*.log" >nul 2>&1
if %errorlevel% == 0 (
    echo .log files found in %local_storage_path%.
) else (
    echo No .log files found in %local_storage_path%.
)

:: Method 3: Check for .txt files as a fallback
echo Attempt #3: Checking for .txt files...
dir "%local_storage_path%\*.txt" >nul 2>&1
if %errorlevel% == 0 (
    echo .txt files found in %local_storage_path%. This indicates that files are present.
) else (
    echo No .txt files found in %local_storage_path%.
)

:: Method 4: List all files with detailed output
echo Attempt #4: Listing all files in %local_storage_path%...
dir "%local_storage_path%"
pause

:: Now attempt to find the latest .log file
echo Attempting to find the latest .log file...
set "latest_log="
for /f "delims=" %%a in ('dir /b /a-d /o-d "%local_storage_path%\*.log" 2^>nul') do (
    set "latest_log=%%a"
    goto open_log_found
)

echo No log files found in %local_storage_path%. Please ensure that log files are present.
pause
goto main_menu

:open_log_found
echo Found log file: %latest_log%
pause

:: Method 1: Attempt to open with Notepad
echo Attempt #1: Opening with Notepad...
notepad "%local_storage_path%\%latest_log%"
if %errorlevel% == 0 (
    echo Successfully opened the log file with Notepad.
    pause
    goto main_menu
) else (
    echo Attempt #1 Failed: Could not open with Notepad.
    pause
)

:: Method 2: Attempt to open with WordPad
echo Attempt #2: Opening with WordPad...
write "%local_storage_path%\%latest_log%"
if %errorlevel% == 0 (
    echo Successfully opened the log file with WordPad.
    pause
    goto main_menu
) else (
    echo Attempt #2 Failed: Could not open with WordPad.
    pause
)

:: Method 3: Display contents using the TYPE command
echo Attempt #3: Displaying log file contents with TYPE command...
type "%local_storage_path%\%latest_log%"
if %errorlevel% == 0 (
    echo Successfully displayed the log file contents.
    pause
    goto main_menu
) else (
    echo Attempt #3 Failed: Could not display contents with TYPE.
    pause
)

:: Method 4: Display the last 30 lines of the log file
echo Attempt #4: Displaying the last 30 lines of the log file...
call :tail "%local_storage_path%\%latest_log%" 30
if %errorlevel% == 0 (
    echo Successfully displayed the last 30 lines of the log file.
) else (
    echo Attempt #4 Failed: Could not display the last 30 lines.
)
pause
goto main_menu

:: Subroutine to display the last N lines of a file
:tail
:: Usage: call :tail filename number_of_lines
setlocal enabledelayedexpansion
set "file=%~1"
set /a lines=%~2
set "count=0"
set "output="

for /f "usebackq delims=" %%x in ("%file%") do (
    set /a count+=1
    set "line[!count!]=%%x"
)

if %count% LSS %lines% (
    set "start=1"
) else (
    set /a start=%count% - %lines% + 1
)

for /l %%i in (%start%,1,%count%) do (
    echo !line[%%i]!
)

endlocal
goto :eof