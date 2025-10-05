#!/bin/bash
# Script de verificación post-reinicio del dev container

echo "🔄 === VERIFICACIÓN POST-REINICIO DEL DEV CONTAINER ==="

echo ""
echo "⏳ Esperando a que Elasticsearch inicie (puede tomar 1-2 minutos)..."
sleep 10

echo ""
echo "🔍 1. Verificando si Elasticsearch está respondiendo..."
for i in {1..12}; do
    if curl -s http://localhost:9200/ > /dev/null 2>&1; then
        echo "✅ Elasticsearch respondiendo en intento $i"
        break
    else
        echo "⏳ Intento $i/12 - Esperando..." 
        sleep 10
    fi
done

echo ""
echo "🏥 2. Verificando salud del cluster..."
curl -s http://localhost:9200/_cluster/health | python3 -m json.tool 2>/dev/null || echo "❌ No se puede verificar salud"

echo ""
echo "📋 3. Información básica de Elasticsearch..."
curl -s http://localhost:9200/ | python3 -m json.tool 2>/dev/null || echo "❌ No conectado"

echo ""
echo "📂 4. Verificando índices existentes..."
curl -s "http://localhost:9200/_cat/indices?v" 2>/dev/null || echo "📭 No hay índices aún (esto es normal)"

echo ""
echo "🔧 5. Verificando nodos del cluster..."
curl -s "http://localhost:9200/_cat/nodes?v" 2>/dev/null || echo "❌ No se pueden ver nodos"

echo ""
echo "🧪 6. Ejecutando health check del proyecto..."
cd /workspaces/ecommerce-semantic-search
PYTHONPATH=/workspaces/ecommerce-semantic-search python scripts/health_check.py

echo ""
echo "✨ === VERIFICACIÓN COMPLETADA ==="