#!/bin/bash
# Setup script para EcoLocal com Mapa Interativo

echo "🌍 EcoLocal - Setup do Mapa Interativo"
echo "======================================"
echo ""

# Verificar Python
if ! command -v python &> /dev/null; then
    echo "❌ Python não encontrado. Por favor, instale Python 3.8+"
    exit 1
fi

echo "✓ Python encontrado"
echo ""

# Verificar venv
if [ ! -d ".venv" ]; then
    echo "📦 Criando virtual environment..."
    python -m venv .venv
else
    echo "✓ Virtual environment já existe"
fi

echo ""
echo "🔌 Ativando virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

echo "✓ Virtual environment ativado"
echo ""

echo "📥 Instalando dependências..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup completo!"
    echo ""
    echo "🚀 Para iniciar a aplicação, execute:"
    echo "   python app.py"
    echo ""
    echo "📍 Acesse:"
    echo "   Home: http://localhost:5000"
    echo "   Mapa: http://localhost:5000/mapa"
    echo "   API:  http://localhost:5000/api/coleta-pontos"
else
    echo "❌ Erro ao instalar dependências"
    exit 1
fi
