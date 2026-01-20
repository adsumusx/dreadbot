#!/bin/bash
# Script para iniciar o servidor de validação de licenças no Linux/Mac

echo "========================================"
echo "Servidor de Validação de Licenças"
echo "========================================"
echo ""

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python3 não encontrado!"
    echo "Por favor, instale Python primeiro."
    exit 1
fi

# Verifica se Flask está instalado
if ! python3 -c "import flask" &> /dev/null; then
    echo "Flask não encontrado. Instalando..."
    pip3 install flask
fi

echo "Iniciando servidor..."
echo ""
echo "Servidor rodando em: http://localhost:5000"
echo "Pressione Ctrl+C para parar"
echo ""

# Inicia o servidor
python3 license_server.py

