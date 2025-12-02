@echo off
REM Setup script para EcoLocal com Mapa Interativo (Windows)

echo.
echo 🌍 EcoLocal - Setup do Mapa Interativo
echo ======================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Por favor, instale Python 3.8+
    pause
    exit /b 1
)

echo ✓ Python encontrado
echo.

REM Verificar venv
if not exist ".venv" (
    echo 📦 Criando virtual environment...
    python -m venv .venv
) else (
    echo ✓ Virtual environment já existe
)

echo.
echo 🔌 Ativando virtual environment...
call .venv\Scripts\activate.bat

if errorlevel 1 (
    echo ❌ Erro ao ativar virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment ativado
echo.

echo 📥 Instalando dependências...
pip install -r requirements.txt

if errorlevel 0 (
    echo.
    echo ✅ Setup completo!
    echo.
    echo 🚀 Para iniciar a aplicação, execute:
    echo    python app.py
    echo.
    echo 📍 Acesse:
    echo    Home: http://localhost:5000
    echo    Mapa: http://localhost:5000/mapa
    echo    API:  http://localhost:5000/api/coleta-pontos
    echo.
    pause
) else (
    echo ❌ Erro ao instalar dependências
    pause
    exit /b 1
)
