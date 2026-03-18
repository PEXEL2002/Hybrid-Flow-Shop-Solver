@echo off
chcp 65001 >nul
echo ========================================
echo Aplikacja Harmonogramowania Produkcji HFS
echo Autor: Bartlomiej Adam Kuk
echo ========================================
echo.

REM ===== SPRAWDZANIE WYMAGAN =====

echo [1/4] Sprawdzanie Java...
where java >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [BLAD] Java nie jest zainstalowana lub nie jest w PATH
    echo        Pobierz Java 17+ z: https://adoptium.net/
    pause
    exit /b 1
)
java -version 2>&1 | findstr /C:"version" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Java jest zainstalowana
) else (
    echo [BLAD] Nie mozna sprawdzic wersji Java
    pause
    exit /b 1
)

echo.
echo [2/4] Sprawdzanie Maven...
where mvn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [BLAD] Maven nie jest zainstalowany lub nie jest w PATH
    echo        Pobierz Maven z: https://maven.apache.org/download.cgi
    pause
    exit /b 1
)
echo [OK] Maven jest zainstalowany

echo.
echo [3/4] Sprawdzanie Python...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [BLAD] Python nie jest zainstalowany lub nie jest w PATH
    echo        Pobierz Python 3.8+ z: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo [OK] Python jest zainstalowany

echo.
echo [4/4] Instalowanie zaleznosci Python...
cd Python
python -m pip install --upgrade pip >nul 2>nul
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [OSTRZEZENIE] Nie udalo sie zainstalowac wszystkich zaleznosci Python
    echo               Aplikacja moze dzialac nieprawidlowo
    echo.
) else (
    echo [OK] Zaleznosci Python zainstalowane
)
cd ..

echo.
echo ========================================
echo Uruchamianie aplikacji...
echo ========================================
echo.

REM Przejdz do folderu z aplikacja Java
cd Demo_UI\javafx-ui

REM Uruchom aplikacje
echo Uruchamianie interfejsu graficznego...
echo (To moze potrwac kilka sekund przy pierwszym uruchomieniu)
echo.

call mvn javafx:run

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo [BLAD] Aplikacja zakonczyla sie z bledem
    echo ========================================
    cd ..\..
    pause
    exit /b 1
)

cd ..\..
echo.
echo ========================================
echo Aplikacja zakonczona
echo ========================================
pause
