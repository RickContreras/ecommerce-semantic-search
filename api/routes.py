"""Endpoints del API REST."""
import asyncio
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from config import get_settings
from models.schemas import (
    SearchRequest, SearchResponse, SyncRequest, SyncResponse,
    HealthResponse, CategoriesResponse, StatsResponse, ServiceStatus,
    IndexStats, ErrorResponse
)
from services.elasticsearch_service import get_elasticsearch_service
from services.product_service import get_product_service
from services.embedding_service import get_embedding_service
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

router = APIRouter()


@router.post("/sync", response_model=SyncResponse)
async def sync_products(
    sync_request: SyncRequest = SyncRequest(),
    background_tasks: BackgroundTasks = None
):
    """Sincroniza productos desde la API externa hacia Elasticsearch."""
    start_time = datetime.now()
    
    try:
        logger.info("Iniciando sincronización de productos")
        
        es_service = get_elasticsearch_service()
        product_service = get_product_service()
        
        # Verificar conexión con Elasticsearch
        es_health = await es_service.check_connection()
        if es_health["status"] != "up":
            raise HTTPException(
                status_code=503,
                detail="Elasticsearch no disponible"
            )
        
        # Crear índice si no existe o forzar recreación
        if sync_request.force_reindex:
            logger.info("Forzando recreación del índice")
            await es_service.delete_index()
            
        await es_service.create_index()
        
        # Obtener todos los productos
        products = await product_service.get_all_products()
        
        if not products:
            logger.warning("No se encontraron productos para sincronizar")
            elapsed = int((datetime.now() - start_time).total_seconds() * 1000)
            return SyncResponse(
                message="No se encontraron productos para sincronizar",
                productos_indexados=0,
                tiempo_ms=elapsed,
                errores=0
            )
        
        # Indexar productos en lotes
        batch_size = 50  # Procesar en lotes para mejor performance
        total_indexed = 0
        total_errors = 0
        
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            logger.info(f"Procesando lote {i//batch_size + 1} ({len(batch)} productos)")
            
            try:
                result = await es_service.index_products_batch(batch)
                total_indexed += result["indexed"]
                total_errors += result["errors"]
                
            except Exception as e:
                logger.error(f"Error procesando lote: {str(e)}")
                total_errors += len(batch)
        
        elapsed = int((datetime.now() - start_time).total_seconds() * 1000)
        
        logger.info(
            "Sincronización completada",
            extra={
                "productos_indexados": total_indexed,
                "errores": total_errors,
                "tiempo_ms": elapsed
            }
        )
        
        return SyncResponse(
            message="Sincronización completada",
            productos_indexados=total_indexed,
            tiempo_ms=elapsed,
            errores=total_errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        elapsed = int((datetime.now() - start_time).total_seconds() * 1000)
        logger.error(f"Error en sincronización: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en sincronización: {str(e)}"
        )


@router.post("/buscar", response_model=SearchResponse)
async def search_products(search_request: SearchRequest):
    """Búsqueda semántica de productos."""
    try:
        logger.info(f"Búsqueda solicitada: '{search_request.query}'")

        es_service = get_elasticsearch_service()

        # Verificar que el índice existe
        es_health = await es_service.check_connection()
        if es_health["status"] != "up":
            raise HTTPException(
                status_code=503,
                detail="Servicio de búsqueda no disponible"
            )

        # Realizar búsqueda
        results = await es_service.search_products(search_request)

        return SearchResponse(**results)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en búsqueda: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en búsqueda: {str(e)}"
        )


@router.post("/buscar-simple", response_model=SearchResponse)
async def search_products_simple(search_request: SearchRequest):
    """Búsqueda simple de productos usando solo búsqueda textual (sin embeddings)."""
    try:
        logger.info(f"Búsqueda simple solicitada: '{search_request.query}'")

        es_service = get_elasticsearch_service()

        # Verificar que el índice existe
        es_health = await es_service.check_connection()
        if es_health["status"] != "up":
            raise HTTPException(
                status_code=503,
                detail="Servicio de búsqueda no disponible"
            )

        # Realizar búsqueda simple
        results = await es_service.search_products_simple(search_request)

        return SearchResponse(**results)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en búsqueda simple: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en búsqueda simple: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check del sistema."""
    try:
        logger.info("Ejecutando health check")
        
        # Verificar servicios en paralelo
        es_service = get_elasticsearch_service()
        product_service = get_product_service()
        embedding_service = get_embedding_service()
        
        # Ejecutar verificaciones en paralelo
        es_check_task = asyncio.create_task(es_service.check_connection())
        api_check_task = asyncio.create_task(product_service.check_api_health())
        
        es_status = await es_check_task
        api_status = await api_check_task
        
        # Verificar modelo de embeddings
        try:
            model_info = await embedding_service.get_model_info()
            embedding_status = ServiceStatus(
                status="loaded",
                model=model_info.get("model_name")
            )
        except Exception as e:
            embedding_status = ServiceStatus(
                status="error",
                model=str(e)
            )
        
        # Obtener estadísticas del índice
        try:
            stats = await es_service.get_index_stats()
            index_stats = IndexStats(**stats)
        except Exception as e:
            logger.warning(f"Error obteniendo stats del índice: {str(e)}")
            index_stats = IndexStats(total_productos=0)
        
        # Determinar estado general
        overall_status = "healthy"
        if (es_status["status"] != "up" or 
            api_status["status"] != "up" or 
            embedding_status.status != "loaded"):
            overall_status = "degraded"
        
        return HealthResponse(
            status=overall_status,
            services={
                "elasticsearch": ServiceStatus(**es_status),
                "productos_api": ServiceStatus(**api_status),
                "embedding_model": embedding_status
            },
            index_stats=index_stats
        )
        
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        # Retornar un health check básico indicando problemas
        return HealthResponse(
            status="unhealthy",
            services={
                "elasticsearch": ServiceStatus(status="unknown"),
                "productos_api": ServiceStatus(status="unknown"),
                "embedding_model": ServiceStatus(status="unknown")
            },
            index_stats=IndexStats(total_productos=0)
        )


@router.get("/categories", response_model=CategoriesResponse)
async def get_categories():
    """Lista categorías disponibles."""
    try:
        es_service = get_elasticsearch_service()
        
        categories = await es_service.get_categories()
        
        return CategoriesResponse(categories=categories)
        
    except Exception as e:
        logger.error(f"Error obteniendo categorías: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo categorías: {str(e)}"
        )


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Estadísticas del índice y uso."""
    try:
        es_service = get_elasticsearch_service()
        
        # Obtener estadísticas básicas
        stats = await es_service.get_index_stats()
        
        # TODO: Implementar métricas de uso más avanzadas
        # Por ahora retornamos datos básicos
        return StatsResponse(
            index_size_mb=stats.get("index_size_mb", 0.0),
            total_documents=stats.get("total_productos", 0),
            avg_search_time_ms=50,  # Placeholder
            last_24h_searches=0,    # Placeholder
            most_searched_terms=[]  # Placeholder
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )


# Nota: Los manejadores de errores se configuran en main.py