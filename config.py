import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class Settings:
    # Elasticsearch
    ELASTICSEARCH_URL: str = os.getenv(
        "ELASTICSEARCH_URL", "http://localhost:9200")
    INDEX_NAME: str = os.getenv("INDEX_NAME", "productos")

    # API Externa de Productos
    PRODUCTOS_API_URL: str = os.getenv(
        "PRODUCTOS_API_URL",
        "https://scaling-umbrella-vj7gqw4v65qcw5g-8000.app.github.dev/api/v1/products"
    )

    # Modelo de embeddings
    MODEL_NAME: str = os.getenv(
        "MODEL_NAME",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # Configuración de la API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "E-commerce Semantic Search"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API de búsqueda semántica para productos de e-commerce"

    # Timeouts
    SYNC_TIMEOUT: int = int(os.getenv("SYNC_TIMEOUT", "30"))
    SEARCH_TIMEOUT: int = int(os.getenv("SEARCH_TIMEOUT", "5"))

    # Configuración de paginación
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100


# Instancia global de configuración
settings = Settings()
