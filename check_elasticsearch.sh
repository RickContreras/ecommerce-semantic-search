#!/bin/bash
# Script para probar Elasticsearch de múltiples formas

echo "🚀 === PRUEBAS DE ELASTICSEARCH ==="

echo ""
echo "🔍 1. Prueba básica de conexión..."
curl -s http://localhost:9200/ | python3 -m json.tool 2>/dev/null || echo "❌ No conectado"

echo ""
echo "🏥 2. Verificando salud del cluster..."
curl -s http://localhost:9200/_cluster/health | python3 -m json.tool 2>/dev/null || echo "❌ No se puede verificar salud"

echo ""
echo "📊 3. Información del cluster..."
curl -s http://localhost:9200/_cluster/stats | python3 -m json.tool 2>/dev/null || echo "❌ No se pueden obtener estadísticas"

echo ""
echo "📂 4. Listando índices..."
curl -s "http://localhost:9200/_cat/indices?v" || echo "❌ No se pueden listar índices"

echo ""
echo "🔧 5. Verificando nodos..."
curl -s "http://localhost:9200/_cat/nodes?v" || echo "❌ No se pueden verificar nodos"

echo ""
echo "💾 6. Uso de memoria..."
curl -s "http://localhost:9200/_cat/nodes?v&h=name,heap.percent,ram.percent" || echo "❌ No se puede verificar memoria"