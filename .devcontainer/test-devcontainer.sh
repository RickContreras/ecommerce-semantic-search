#!/bin/bash

# Script para probar manualmente los servicios del devcontainer
echo "🔧 Probando configuración del devcontainer..."

# Función para mostrar estado
show_status() {
    local service="$1"
    local command="$2"
    echo -n "  $service: "
    if eval "$command" >/dev/null 2>&1; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAIL"
        return 1
    fi
}

echo ""
echo "📋 Verificando servicios:"

# Verificar Elasticsearch
show_status "Elasticsearch HTTP" "curl -s -f http://localhost:9200 >/dev/null"
show_status "Elasticsearch Health" "curl -s -f http://localhost:9200/_cluster/health >/dev/null"

# Verificar Python y dependencias
show_status "Python" "python3 --version"
show_status "Pip packages" "pip list | grep -i elasticsearch"

echo ""
echo "🧪 Pruebas funcionales:"

# Probar conexión con Python
echo -n "  Python + Elasticsearch: "
python3 -c "
import requests
try:
    response = requests.get('http://localhost:9200', timeout=5)
    if response.status_code == 200:
        print('✅ OK')
        exit(0)
    else:
        print(f'❌ HTTP {response.status_code}')
        exit(1)
except Exception as e:
    print(f'❌ ERROR: {e}')
    exit(1)
" || echo "❌ FAIL"

# Mostrar información detallada si Elasticsearch funciona
if curl -s -f http://localhost:9200 >/dev/null 2>&1; then
    echo ""
    echo "📊 Información de Elasticsearch:"
    echo "$(curl -s http://localhost:9200 | python3 -m json.tool 2>/dev/null)" || \
    echo "$(curl -s http://localhost:9200)"
    
    echo ""
    echo "🏥 Estado del cluster:"
    echo "$(curl -s http://localhost:9200/_cluster/health | python3 -m json.tool 2>/dev/null)" || \
    echo "$(curl -s http://localhost:9200/_cluster/health)"
fi

echo ""
echo "💡 Comandos útiles:"
echo "  - Verificar health: curl http://localhost:9200/_cluster/health"
echo "  - Listar índices: curl http://localhost:9200/_cat/indices?v"
echo "  - Probar API: python test_elasticsearch.py"
echo "  - Health check: python scripts/health_check.py"