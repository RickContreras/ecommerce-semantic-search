# 🔍 Guía Completa: Cómo Probar Elasticsearch

## 📋 Resumen Ejecutivo

Elasticsearch no está ejecutándose actualmente. Aquí tienes múltiples formas de probarlo:

## 🚀 Métodos para Probar Elasticsearch

### 1. **✅ Prueba Básica con curl**
```bash
# Prueba de conexión simple
curl http://localhost:9200/

# Con formato JSON bonito
curl -s http://localhost:9200/ | python3 -m json.tool
```

**Respuesta esperada si funciona:**
```json
{
  "name": "node-1",
  "cluster_name": "elasticsearch",
  "cluster_uuid": "...",
  "version": {
    "number": "7.17.10"
  }
}
```

### 2. **🏥 Verificar Salud del Cluster**
```bash
# Salud básica
curl http://localhost:9200/_cluster/health

# Con formato
curl -s http://localhost:9200/_cluster/health | python3 -m json.tool
```

**Estados posibles:**
- 🟢 **GREEN**: Todo funcionando perfectamente
- 🟡 **YELLOW**: Funcionando con advertencias
- 🔴 **RED**: Problemas críticos

### 3. **📊 Información Detallada**
```bash
# Información general del cluster
curl http://localhost:9200/_cluster/stats

# Información de nodos
curl "http://localhost:9200/_cat/nodes?v"

# Lista de índices
curl "http://localhost:9200/_cat/indices?v"
```

### 4. **🔧 Usando el Cliente Python del Proyecto**
```bash
# Script personalizado del proyecto
cd /workspaces/ecommerce-semantic-search
python test_elasticsearch.py
```

### 5. **🩺 Health Check Completo del Proyecto**
```bash
cd /workspaces/ecommerce-semantic-search
PYTHONPATH=/workspaces/ecommerce-semantic-search python scripts/health_check.py
```

## 🚨 Resolución de Problemas

### **Si Elasticsearch no responde:**

1. **Verificar si está ejecutándose:**
```bash
# Verificar procesos Java
ps aux | grep elasticsearch

# Verificar puertos abiertos
netstat -tlnp | grep 9200
```

2. **Iniciar Elasticsearch:**
```bash
# Desde fuera del dev container (en tu máquina local)
cd /workspaces/ecommerce-semantic-search/.devcontainer
docker compose up -d
```

3. **Verificar logs:**
```bash
# Ver logs de Docker
docker compose logs elasticsearch
```

4. **Verificar puertos:**
```bash
# El dev container debe tener estos puertos redirigidos
# - 9200: Elasticsearch HTTP API
# - 9300: Elasticsearch Transport
```

### **Si funciona parcialmente:**

1. **Crear índice de prueba:**
```bash
curl -X PUT "http://localhost:9200/test-index"
```

2. **Insertar documento de prueba:**
```bash
curl -X POST "http://localhost:9200/test-index/_doc" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Elasticsearch", "timestamp": "2023-10-05"}'
```

3. **Buscar documentos:**
```bash
curl "http://localhost:9200/test-index/_search"
```

4. **Limpiar índice de prueba:**
```bash
curl -X DELETE "http://localhost:9200/test-index"
```

## 📝 Scripts Disponibles

### **Script de Prueba Rápida**
```bash
./check_elasticsearch.sh
```

### **Script de Prueba Completa**
```bash
python test_elasticsearch.py
```

### **Health Check del Proyecto**
```bash
PYTHONPATH=/workspaces/ecommerce-semantic-search python scripts/health_check.py
```

## 🎯 Comandos Útiles para Desarrollo

### **Monitoreo en Tiempo Real**
```bash
# Watch del estado del cluster
watch curl -s http://localhost:9200/_cluster/health

# Monitoreo de índices
watch curl -s "http://localhost:9200/_cat/indices?v"
```

### **Configuración Específica del Proyecto**
```bash
# Verificar configuración actual
python -c "from config import settings; print(f'ES URL: {settings.ELASTICSEARCH_URL}')"

# Probar conexión con configuración del proyecto
python -c "
from services.elasticsearch_service import ElasticsearchService
import asyncio
es = ElasticsearchService()
print('Conectado:', asyncio.run(es.check_connection()))
"
```

## 💡 Notas Importantes

1. **Tiempo de Inicio**: Elasticsearch puede tardar 1-3 minutos en iniciar completamente
2. **Memoria**: Necesita al menos 512MB RAM (configurado en docker-compose.yml)
3. **Puertos**: Debe estar disponible en localhost:9200
4. **Versión**: El proyecto usa Elasticsearch 7.17.10

## 🔗 URLs Útiles (cuando funcione)

- **API Root**: http://localhost:9200/
- **Health**: http://localhost:9200/_cluster/health
- **Índices**: http://localhost:9200/_cat/indices?v
- **Nodos**: http://localhost:9200/_cat/nodes?v
- **Plugins**: http://localhost:9200/_cat/plugins?v