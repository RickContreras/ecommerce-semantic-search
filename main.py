"""Aplicación principal FastAPI para búsqueda tradicional de e-commerce."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from config import get_settings
from api.routes import router
from services.elasticsearch_service import get_elasticsearch_service
from utils.logger import get_logger
from monitoring.prometheus_middleware import PrometheusMiddleware, metrics_response

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejador del ciclo de vida de la aplicación."""
    # Startup
    logger.info("Iniciando aplicación de búsqueda semántica")
    
    # Verificar servicios básicos al inicio
    try:
        es_service = get_elasticsearch_service()
        health = await es_service.check_connection()
        if health["status"] == "up":
            logger.info("Conexión con Elasticsearch verificada")
        else:
            logger.warning("Elasticsearch no disponible al inicio")
    except Exception as e:
        logger.error(f"Error verificando Elasticsearch al inicio: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación")
    try:
        es_service = get_elasticsearch_service()
        await es_service.close()
    except Exception as e:
        logger.error(f"Error cerrando conexiones: {str(e)}")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.project_name,
    description="Sistema de búsqueda semántica para productos de e-commerce usando Elasticsearch y embeddings multilingües. Permite búsquedas por significado, no solo palabras exactas.",
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "E-commerce Traditional Search API",
        "url": "https://github.com/RickContreras/ecommerce-semantic-search",
    },
    license_info={
        "name": "MIT",
    },
)

# Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware, service_name="traditional-search")

# Configurar CORS - Permitir TODO desde cualquier lugar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite cualquier origen
    allow_credentials=True,  # Permite cookies y credenciales
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite cualquier header
    expose_headers=["*"],  # Expone todos los headers en respuestas
)

# Incluir rutas
app.include_router(router, prefix=settings.api_v1_str)


@app.get("/")
async def root():
    """Endpoint raíz con información básica."""
    return {
        "message": "API de Búsqueda Semántica E-commerce",
        "version": settings.version,
        "docs": "/docs",
        "health": f"{settings.api_v1_str}/health"
    }


@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Prometheus metrics endpoint."""
    return metrics_response()

@app.get("/ping")
async def ping():
    """Endpoint simple para verificar que la API está funcionando."""
    return {"status": "ok", "timestamp": "2025-01-01T00:00:00Z"}


@app.get("/api-info")
async def api_info():
    """Información detallada de la API y endpoints disponibles."""
    return {
        "api": {
            "title": "E-commerce Traditional Search",
            "version": settings.version,
            "description": "Sistema de búsqueda semántica para productos de e-commerce"
        },
        "documentation": {
            "swagger_ui": f"http://localhost:8000/docs",
            "redoc": f"http://localhost:8000/redoc", 
            "openapi_json": f"http://localhost:8000/openapi.json"
        },
        "endpoints": {
            "search": {
                "url": f"{settings.api_v1_str}/buscar",
                "method": "POST",
                "description": "Búsqueda semántica de productos",
                "example": {
                    "query": "smartphone con buena cámara",
                    "top_k": 5,
                    "category": "Smartphones",
                    "price_max": 1500.0
                }
            },
            "sync": {
                "url": f"{settings.api_v1_str}/sync",
                "method": "POST", 
                "description": "Sincronizar productos desde API externa"
            },
            "health": {
                "url": f"{settings.api_v1_str}/health",
                "method": "GET",
                "description": "Estado de salud de todos los servicios"
            },
            "categories": {
                "url": f"{settings.api_v1_str}/categories",
                "method": "GET",
                "description": "Lista de categorías disponibles"
            },
            "stats": {
                "url": f"{settings.api_v1_str}/stats", 
                "method": "GET",
                "description": "Estadísticas del índice y búsquedas"
            }
        },
        "examples": {
            "semantic_search": "curl -X POST http://localhost:8000/api/v1/buscar -H 'Content-Type: application/json' -d '{\"query\": \"laptop para programar\", \"top_k\": 3}'",
            "health_check": "curl http://localhost:8000/api/v1/health",
            "categories": "curl http://localhost:8000/api/v1/categories"
        }
    }


@app.get("/docs-simple", response_class=HTMLResponse)
async def docs_simple():
    """Documentación simple de la API en HTML."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>E-commerce Traditional Search API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { font-weight: bold; color: #2196F3; }
            .url { font-family: monospace; background: #e0e0e0; padding: 2px 5px; }
            .example { background: #1e1e1e; color: #fff; padding: 10px; margin: 10px 0; font-family: monospace; overflow-x: auto; }
            h1 { color: #333; }
            h2 { color: #555; }
        </style>
    </head>
    <body>
        <h1>🔍 E-commerce Traditional Search API</h1>
        <p>Sistema de búsqueda semántica para productos de e-commerce usando Elasticsearch y embeddings multilingües.</p>
        
        <h2>📚 Documentación</h2>
        <ul>
            <li><a href="/docs" target="_blank">Swagger UI</a> - Documentación interactiva</li>
            <li><a href="/redoc" target="_blank">ReDoc</a> - Documentación alternativa</li>
            <li><a href="/openapi.json" target="_blank">OpenAPI JSON</a> - Especificación de la API</li>
            <li><a href="/api-info" target="_blank">API Info</a> - Información detallada en JSON</li>
        </ul>

        <h2>🔗 Endpoints Principales</h2>
        
        <div class="endpoint">
            <h3>🔍 Búsqueda Semántica</h3>
            <p><span class="method">POST</span> <span class="url">/api/v1/buscar</span></p>
            <p>Encuentra productos por significado, no solo palabras exactas.</p>
            <div class="example">curl -X POST http://localhost:8000/api/v1/buscar \\
  -H "Content-Type: application/json" \\
  -d '{"query": "smartphone con buena cámara", "top_k": 5}'</div>
        </div>

        <div class="endpoint">
            <h3>🏥 Health Check</h3>
            <p><span class="method">GET</span> <span class="url">/api/v1/health</span></p>
            <p>Estado de salud de todos los servicios del sistema.</p>
            <div class="example">curl http://localhost:8000/api/v1/health</div>
        </div>

        <div class="endpoint">
            <h3>🔄 Sincronización</h3>
            <p><span class="method">POST</span> <span class="url">/api/v1/sync</span></p>
            <p>Sincroniza productos desde la API externa al índice de Elasticsearch.</p>
            <div class="example">curl -X POST http://localhost:8000/api/v1/sync \\
  -H "Content-Type: application/json" \\
  -d '{}'</div>
        </div>

        <div class="endpoint">
            <h3>🏷️ Categorías</h3>
            <p><span class="method">GET</span> <span class="url">/api/v1/categories</span></p>
            <p>Lista todas las categorías de productos disponibles.</p>
            <div class="example">curl http://localhost:8000/api/v1/categories</div>
        </div>

        <div class="endpoint">
            <h3>📊 Estadísticas</h3>
            <p><span class="method">GET</span> <span class="url">/api/v1/stats</span></p>
            <p>Estadísticas del índice y métricas de búsquedas.</p>
            <div class="example">curl http://localhost:8000/api/v1/stats</div>
        </div>

        <h2>✨ Ejemplos de Búsqueda Semántica</h2>
        <ul>
            <li><strong>"teléfono con buena cámara"</strong> → Encuentra iPhones, Samsung Galaxy</li>
            <li><strong>"laptop para programar"</strong> → Encuentra MacBooks, laptops de desarrollo</li>
            <li><strong>"regalo tecnológico económico"</strong> → Productos tech bajo cierto precio</li>
            <li><strong>"auriculares para música"</strong> → Dispositivos de audio premium</li>
        </ul>

        <h2>🎯 Filtros Avanzados</h2>
        <p>La búsqueda soporta filtros combinados:</p>
        <div class="example">{
  "query": "cámara",
  "category": "Smartphones", 
  "price_max": 1500.0,
  "price_min": 500.0,
  "include_out_of_stock": false,
  "top_k": 10
}</div>

        <p><em>Para documentación completa e interactiva, visita <a href="/docs">/docs</a></em></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )