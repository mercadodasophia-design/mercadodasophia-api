#!/usr/bin/env bash
# Script de build para o Render

echo "🚀 Iniciando build do servidor Python..."

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Verificar se o SDK está presente
echo "🔍 Verificando SDK Python..."
if [ -f "iop/base.py" ]; then
    echo "✅ SDK Python encontrado"
else
    echo "❌ SDK Python não encontrado"
    exit 1
fi

echo "✅ Build concluído com sucesso!" 