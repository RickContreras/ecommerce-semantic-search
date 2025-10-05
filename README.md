# E-commerce Semantic Search API

Sistema de búsqueda semántica para productos de e-commerce usando Elasticsearch y modelos de embeddings multilingües.

## 🚀 Características

- **Búsqueda semántica**: Encuentra productos por significado, no solo palabras clave exactas
- **Multilingüe**: Soporte principal para español con modelo `paraphrase-multilingual-MiniLM-L12-v2`
- **Filtros avanzados**: Búsqueda por categoría, rango de precios
- **API REST**: Interfaz FastAPI con documentación automática
- **Sincronización automática**: Indexa productos desde API externa
- **Monitoreo**: Endpoints de salud y estadísticas

## 📋 Requisitos

- Python 3.10+
- Elasticsearch 7.17+
- Acceso a internet (para descargar modelos de ML)

## 🛠️ Instalación y Configuración

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y ajusta las configuraciones:

```bash
cp .env.example .env
```

Edita `.env` con tus configuraciones:

```env
ELASTICSEARCH_URL=http://localhost:9200
PRODUCTOS_API_URL=https://scaling-umbrella-vj7gqw4v65qcww5g-8000.app.github.dev/api/v1/products/
INDEX_NAME=productos
MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
SYNC_TIMEOUT=30
SEARCH_TIMEOUT=5
```

### 3. Verificar servicios

```bash
python scripts/health_check.py
```

### 4. Configurar índice inicial

```bash
python scripts/setup_index.py
```

## 🚀 Uso

### Iniciar el servidor

```bash
python main.py
```

El servidor estará disponible en: http://localhost:8000

### Documentación interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### 🔄 Sincronización

**POST** `/api/v1/sync`

Sincroniza productos desde la API externa hacia Elasticsearch.

```bash
curl -X POST http://localhost:8000/api/v1/sync
```

### 🔍 Búsqueda Semántica

**POST** `/api/v1/buscar`

```bash
curl -X POST http://localhost:8000/api/v1/buscar \
  -H "Content-Type: application/json" \
  -d '{
    "query": "smartphone con buena cámara",
    "top_k": 5,
    "category": "Smartphones",
    "price_max": 1000
  }'
```

### 🏥 Salud del Sistema

**GET** `/api/v1/health`

```bash
curl http://localhost:8000/api/v1/health
```

## ⚠️ Estado Actual

**Nota**: Elasticsearch debe estar ejecutándose para que la API funcione correctamente. En el devcontainer actual, necesitas iniciar Elasticsearch manualmente o verificar la configuración del docker-compose.

## 📁 Estructura del Proyecto

```
ecommerce-semantic-search/
├── .env                    # Variables de entorno
├── requirements.txt      # Dependencias Python
├── config.py            # Configuración global
├── main.py             # Aplicación FastAPI principal
├── api/routes.py       # Endpoints
├── models/schemas.py   # Modelos Pydantic
├── services/           # Servicios (Elasticsearch, embeddings, productos)
├── utils/logger.py     # Logging
├── scripts/           # Scripts de configuración
└── tests/            # Tests básicos
```
