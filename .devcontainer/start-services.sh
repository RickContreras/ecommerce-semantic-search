#!/bin/bash

# Script para iniciar servicios automáticamente
echo "🔄 Iniciando servicios del proyecto..."

# Función para verificar si Elasticsearch está ejecutándose
check_elasticsearch() {
    curl -s -f http://localhost:9200/_cluster/health > /dev/null 2>&1
    return $?
}

# Función para esperar a que Elasticsearch esté listo
wait_for_elasticsearch() {
    echo "⏳ Esperando a que Elasticsearch esté listo..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if check_elasticsearch; then
            echo "✅ Elasticsearch está listo!"
            return 0
        fi
        
        echo "   Intento $attempt/$max_attempts - Elasticsearch no está listo aún..."
        sleep 2
        ((attempt++))
    done
    
    echo "❌ Timeout esperando Elasticsearch"
    return 1
}

# Cambiar al directorio del proyecto
cd /workspace

# Verificar si Elasticsearch ya está ejecutándose
if check_elasticsearch; then
    echo "✅ Elasticsearch ya está ejecutándose"
else
    echo "🐳 Iniciando servicios Docker Compose..."
    
    # Usar docker-compose desde el contexto del host
    # Nota: Este comando debe ejecutarse desde donde docker-compose esté disponible
    # Si estamos en un devcontainer, necesitamos ejecutar docker-compose en el host
    
    # Intentar iniciar desde el directorio .devcontainer
    cd /workspace/.devcontainer
    
    # Si docker-compose está disponible directamente
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d elasticsearch
    elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
        docker compose up -d elasticsearch
    else
        echo "⚠️ Docker Compose no está disponible en el devcontainer"
        echo "   Elasticsearch debe ser iniciado manualmente desde el host:"
        echo "   cd .devcontainer && docker-compose up -d elasticsearch"
        return 1
    fi
    
    # Esperar a que Elasticsearch esté listo
    wait_for_elasticsearch
fi

# Regresar al directorio del workspace
cd /workspace

echo "🎉 Servicios iniciados correctamente"

# Mostrar información útil
echo ""
echo "📋 Información de servicios:"
echo "  - Elasticsearch: http://localhost:9200"
echo "  - Health check: curl http://localhost:9200/_cluster/health"
echo ""
echo "🧪 Para probar Elasticsearch ejecuta:"
echo "  python test_elasticsearch.py"
echo ""