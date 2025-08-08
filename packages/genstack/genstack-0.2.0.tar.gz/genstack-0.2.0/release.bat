@echo off
setlocal enabledelayedexpansion

:: --- 1. Extract and Clean Version ---
echo - Finding version in pyproject.toml...

:: Initialize variable to ensure it's not set from a previous run
set "raw_version="

:: Find the line with "version", ignore comments (#)
for /f "tokens=2 delims==" %%A in ('findstr /i "version" pyproject.toml ^| findstr /v "#"') do (
    set "raw_version=%%~A"
)

if not defined raw_version (
    echo.
    echo [ERROR] Could not find a 'version =' line in pyproject.toml.
    exit /b 1
)

:: Clean the extracted string: remove all quotes and spaces
set "cleaned_version=!raw_version:"=!"
set "cleaned_version=!cleaned_version: =!"

if not defined cleaned_version (
    echo.
    echo [ERROR] Version string is empty after cleaning. Check pyproject.toml.
    exit /b 1
)

set "tag=v!cleaned_version!"
echo - Detected version: %tag%
echo.

:: --- 2. Get Commit Message ---
set /p commit_msg="Enter commit message for release %tag%: "
if not defined commit_msg (
    echo - Commit message was empty. Using a default message.
    set "commit_msg=Release %tag%"
)
echo.

:: --- 3. Git Operations ---
echo - Staging all changes...
git add .

echo - Committing changes...
git commit -m "%commit_msg%"
if errorlevel 1 (
    echo - No changes to commit. Continuing to tag release.
)

echo - Creating/updating local tag %tag%...
:: The -f flag forces the update of the tag if it already exists
git tag -f %tag%
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to create tag %tag%. Aborting.
    exit /b 1
)

echo - Pushing main branch to origin...
git push origin main
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to push main branch. Aborting.
    exit /b 1
)

echo - Pushing tag %tag% to origin (will overwrite if it exists)...
:: The -f flag forces the update of the remote tag
git push origin %tag% -f
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to push tag %tag%.
    echo This can happen if the remote repository protects tags from being overwritten.
    exit /b 1
)

echo.
echo =================================================
echo  Success! Released %tag% to main.
echo =================================================
