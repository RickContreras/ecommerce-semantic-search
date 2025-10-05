#!/bin/bash

# Script de configuración inicial del devcontainer
echo "🚀 Configurando el entorno de desarrollo..."

# Instalar dependencias de Python si no están instaladas
if [ -f "/workspace/requirements.txt" ]; then
    echo "📦 Instalando dependencias de Python..."
    cd /workspace
    pip install -r requirements.txt
fi

# Crear directorio para logs si no existe
mkdir -p /workspace/logs

echo "✅ Configuración inicial completada"