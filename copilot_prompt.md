# Prompt para GitHub Copilot

## Contexto
Necesito implementar un sistema de búsqueda semántica con Elasticsearch para productos de e-commerce. Ya tengo un microservicio de productos corriendo en: `https://scaling-umbrella-vj7gqw4v65qcw5g-8000.app.github.dev/api/v1/products`

## Estructura de Producto (API existente)
```json
{
  "name": "iPhone 15 Pro Max",
  "description": "El iPhone más avanzado con chip A17 Pro...",
  "price": "1199.99",
  "image_url": "https://images.unsplash.com/...",
  "category": "Smartphones",
  "stock": 25,
  "id": "88d7984b-a03c-413c-960f-e73291",
  "created_at": "2025-09-15T03:42:47.3640767",
  "updated_at": "2025-09-15T03:42:47.3640767"
}
```

## Requisitos

### 1. API de Búsqueda Semántica (FastAPI)
Crear un servicio FastAPI con estos endpoints:

**POST /indexar**
- Obtiene productos de `https://scaling-umbrella-vj7gqw4v65qcw5g-8000.app.github.dev/api/v1/products?skip=0&limit=100`
- Genera embeddings usando `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Indexa en Elasticsearch con mapeo:
  ```json
  {
    "mappings": {
      "properties": {
        "id": {"type": "keyword"},
        "name": {"type": "text"},
        "description": {"type": "text"},
        "category": {"type": "keyword"},
        "price": {"type": "float"},
        "stock": {"type": "integer"},
        "embedding": {
          "type": "dense_vector",
          "dims": 384,
          "index": true,
          "similarity": "cosine"
        }
      }
    }
  }
  ```

**POST /buscar**
Request:
```json
{
  "query": "laptop para programar",
  "top_k": 5,
  "category": "Laptops" (opcional),
  "price_max": 2000 (opcional)
}
```

Response:
```json
{
  "query": "laptop para programar",
  "total_resultados": 5,
  "tiempo_ms": 45,
  "resultados": [
    {
      "id": "...",
      "name": "MacBook Pro 14",
      "description": "...",
      "price": 1599.00,
      "category": "Laptops",
      "score": 0.92
    }
  ]
}
```

**GET /health**
- Verifica salud de API y Elasticsearch

**POST /sync**
- Sincroniza manualmente desde el microservicio de productos
- Usa paginación para manejar grandes volúmenes

### 2. Docker Compose
Archivo `docker-compose.yml` con:
- Elasticsearch 8.11.0 (single-node, sin seguridad para desarrollo)
- API de búsqueda (Python 3.10)
- Kibana 8.11.0 (opcional para visualización)

### 3. Características Técnicas
- Embeddings multilingües (español principalmente)
- Búsqueda por similitud de coseno
- Filtros combinados (categoría, precio)
- Manejo de paginación en sincronización
- Logs informativos
- Manejo de errores robusto

### 4. Archivos a Generar
```
proyecto/
├── main.py                 # API FastAPI
├── requirements.txt        # Dependencias Python
├── Dockerfile             # Imagen de la API
├── docker-compose.yml     # Orquestación
├── .env                   # Variables de entorno
├── README.md              # Documentación
└── test_api.py           # Tests básicos
```

## Dependencias Principales
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
elasticsearch==8.11.0
sentence-transformers==2.3.1
requests==2.31.0
pydantic==2.5.0
python-dotenv==1.0.0
```

## Variables de Entorno (.env)
```env
ELASTICSEARCH_URL=http://elasticsearch:9200
PRODUCTOS_API_URL=https://scaling-umbrella-vj7gqw4v65qcw5g-8000.app.github.dev/api/v1/products
INDEX_NAME=productos
MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

## Transformación de Datos
El API existente usa snake_case, transformar a formato consistente:
```python
def transformar_producto(producto_api):
    return {
        "id": producto_api["id"],
        "name": producto_api["name"],
        "description": producto_api.get("description", ""),
        "category": producto_api.get("category", "General"),
        "price": float(producto_api.get("price", 0)),
        "stock": int(producto_api.get("stock", 0)),
        "image_url": producto_api.get("image_url"),
        "created_at": producto_api.get("created_at"),
        "updated_at": producto_api.get("updated_at")
    }
```

## Ejemplo de Uso
```bash
# 1. Iniciar servicios
docker-compose up -d

# 2. Sincronizar productos
curl -X POST http://localhost:8000/sync

# 3. Buscar
curl -X POST http://localhost:8000/buscar \
  -H "Content-Type: application/json" \
  -d '{
    "query": "iPhone con buena cámara",
    "top_k": 3,
    "category": "Smartphones"
  }'
```

## Consideraciones
- La API de productos está protegida, usa headers apropiados si es necesario
- Implementa retry logic para llamadas HTTP
- Usa async/await para mejor performance
- Maneja timeouts (30s para sync, 5s para búsquedas)
- Implementa logging con niveles (INFO, ERROR)

## Extras Opcionales
- Endpoint `/categories` para listar categorías disponibles
- Endpoint `/stats` para estadísticas del índice
- Cache simple con `lru_cache` para búsquedas comunes
- Health check que valide conectividad con ambos servicios

## Testing
Incluir tests básicos para:
- Conexión a Elasticsearch
- Sincronización de productos
- Búsqueda simple
- Búsqueda con filtros
- Manejo de errores

---

**Objetivo:** Sistema funcional mínimo viable (MVP) que permita búsqueda semántica sobre los productos existentes, fácil de ejecutar con Github Codespaces o devcontainer.

**Prioridad:** Simplicidad y funcionalidad sobre optimización prematura.