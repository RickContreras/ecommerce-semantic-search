from fastapi import APIRouter, HTTPException, Depends
from typing import List
import time
from datetime import datetime

from models.schemas import (
    BusquedaRequest,
    BusquedaResponse,
    ResultadoBusqueda,
    HealthResponse,
    SyncResponse
)
from services.elasticsearch_service import ElasticsearchService
from services.elasticsearch_mock_service import ElasticsearchMockService
from services.embedding_service import EmbeddingService
from services.product_service import ProductService
from utils.logger import setup_logger

logger = setup_logger("api_routes")

# Instancias de servicios con fallback a mock
try:
    es_service = ElasticsearchService()
    # Verificar si Elasticsearch está disponible
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    is_es_available = loop.run_until_complete(es_service.check_connection())
    loop.close()

    if not is_es_available:
        logger.warning("Elasticsearch no disponible, usando servicio mock")
        es_service = ElasticsearchMockService()
except Exception as e:
    logger.warning(f"Error iniciando Elasticsearch, usando mock: {e}")
    es_service = ElasticsearchMockService()

try:
    embedding_service = EmbeddingService()
    logger.info("Servicio de embeddings inicializado correctamente")
except Exception as e:
    logger.error(f"Error iniciando servicio de embeddings: {e}")
    embedding_service = None

product_service = ProductService()

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Verifica el estado de salud de la API y servicios conectados"""

    # Verificar Elasticsearch
    es_status = "healthy" if await es_service.check_connection() else "unhealthy"

    # Verificar API de productos
    products_api_status = "healthy" if product_service.check_api_health() else "unhealthy"

    # Estado general
    overall_status = "healthy" if es_status == "healthy" and products_api_status == "healthy" else "unhealthy"

    return HealthResponse(
        status=overall_status,
        elasticsearch=es_status,
        products_api=products_api_status,
        timestamp=datetime.now()
    )


@router.post("/sync", response_model=SyncResponse)
async def sync_products():
    """Sincroniza productos desde la API externa hacia Elasticsearch"""
    start_time = time.time()
    errores = []
    productos_sincronizados = 0

    try:
        # Verificar conexión a Elasticsearch
        if not await es_service.check_connection():
            raise HTTPException(
                status_code=503, detail="Elasticsearch no disponible")

        # Crear índice si no existe
        if not es_service.create_index():
            raise HTTPException(
                status_code=500, detail="Error creando índice en Elasticsearch")

        # Obtener todos los productos
        logger.info("Iniciando sincronización de productos...")
        productos_api = await product_service.fetch_all_products()

        if not productos_api:
            return SyncResponse(
                status="warning",
                productos_sincronizados=0,
                tiempo_ms=int((time.time() - start_time) * 1000),
                errores=["No se encontraron productos para sincronizar"]
            )

        # Procesar productos en lotes
        productos_para_indexar = []

        for producto_data in productos_api:
            try:
                # Transformar producto
                producto = product_service.transform_product(producto_data)

                # Generar embedding (si el servicio está disponible)
                embedding = None
                if embedding_service:
                    try:
                        embedding = embedding_service.encode_product(
                            producto.name,
                            producto.description,
                            producto.category
                        )
                    except Exception as e:
                        logger.warning(
                            f"Error generando embedding para {producto.id}: {e}")

                # Preparar para indexación
                producto_dict = producto.dict()
                producto_dict["embedding"] = embedding
                productos_para_indexar.append(producto_dict)

            except Exception as e:
                error_msg = f"Error procesando producto {producto_data.get('id', 'unknown')}: {str(e)}"
                errores.append(error_msg)
                logger.error(error_msg)

        # Indexar productos en Elasticsearch
        if productos_para_indexar:
            success_count, failed = es_service.bulk_index_products(
                productos_para_indexar)
            productos_sincronizados = success_count

            if failed:
                for error in failed:
                    errores.append(str(error))

        tiempo_total = int((time.time() - start_time) * 1000)

        status = "success"
        if errores:
            status = "partial_success" if productos_sincronizados > 0 else "error"

        logger.info(
            f"Sincronización completada: {productos_sincronizados} productos en {tiempo_total}ms")

        return SyncResponse(
            status=status,
            productos_sincronizados=productos_sincronizados,
            tiempo_ms=tiempo_total,
            errores=errores
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error durante sincronización: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/buscar", response_model=BusquedaResponse)
async def buscar_productos(request: BusquedaRequest):
    """Realiza búsqueda semántica de productos"""
    start_time = time.time()

    try:
        # Verificar conexión a Elasticsearch
        if not await es_service.check_connection():
            raise HTTPException(
                status_code=503, detail="Elasticsearch no disponible")

        # Generar embedding para la consulta (si el servicio está disponible)
        query_embedding = None
        if embedding_service:
            try:
                query_embedding = embedding_service.encode_query(
                    request.query, request.category)
            except Exception as e:
                logger.warning(f"Error generando embedding para consulta: {e}")

        # Realizar búsqueda semántica
        if query_embedding:
            resultados_raw = es_service.semantic_search(
                query_vector=query_embedding,
                size=request.top_k,
                category=request.category,
                price_min=request.price_min,
                price_max=request.price_max
            )
        else:
            # Fallback: búsqueda simulada sin embeddings
            resultados_raw = es_service.semantic_search(
                query_vector=[],  # Vector vacío para el mock
                size=request.top_k,
                category=request.category,
                price_min=request.price_min,
                price_max=request.price_max
            )

        # Transformar resultados
        resultados = []
        for resultado in resultados_raw:
            resultados.append(ResultadoBusqueda(
                id=resultado["id"],
                name=resultado["name"],
                description=resultado["description"],
                price=resultado["price"],
                category=resultado["category"],
                image_url=resultado.get("image_url"),
                score=round(resultado["score"], 4)
            ))

        tiempo_total = int((time.time() - start_time) * 1000)

        logger.info(
            f"Búsqueda '{request.query}' completada: {len(resultados)} resultados en {tiempo_total}ms")

        return BusquedaResponse(
            query=request.query,
            total_resultados=len(resultados),
            tiempo_ms=tiempo_total,
            resultados=resultados
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error durante búsqueda: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/stats")
async def get_index_stats():
    """Obtiene estadísticas del índice de Elasticsearch"""
    try:
        if not await es_service.check_connection():
            raise HTTPException(
                status_code=503, detail="Elasticsearch no disponible")

        stats = es_service.get_index_stats()
        return stats

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error obteniendo estadísticas: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/indexar")
async def indexar_productos():
    """Alias para el endpoint de sincronización (compatibilidad)"""
    return await sync_products()
