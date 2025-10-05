#!/usr/bin/env python3
"""
Script para verificar la salud de todos los servicios
"""

from utils.logger import setup_logger
from services.product_service import ProductService
from services.elasticsearch_service import ElasticsearchService
import asyncio
import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


logger = setup_logger("health_check")


async def check_elasticsearch():
    """Verifica Elasticsearch"""
    logger.info("Verificando Elasticsearch...")
    es_service = ElasticsearchService()

    if await es_service.check_connection():
        logger.info("✅ Elasticsearch: Conectado")

        # Verificar estadísticas del índice si existe
        try:
            stats = es_service.get_index_stats()
            if "error" not in stats:
                logger.info(
                    f"📊 Documentos en índice: {stats.get('total_documents', 0)}")
            else:
                logger.info("📊 Índice no existe aún")
        except:
            logger.info("📊 Índice no existe aún")

        return True
    else:
        logger.error("❌ Elasticsearch: No conectado")
        return False


async def check_products_api():
    """Verifica API de productos"""
    logger.info("Verificando API de productos...")
    product_service = ProductService()

    if product_service.check_api_health():
        logger.info("✅ API de productos: Disponible")

        # Probar obtener algunos productos
        try:
            productos = await product_service.fetch_products(limit=5)
            logger.info(f"📦 Productos de prueba obtenidos: {len(productos)}")
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo productos de prueba: {e}")

        return True
    else:
        logger.error("❌ API de productos: No disponible")
        return False


async def main():
    """Función principal de verificación"""
    logger.info("=== Health Check - Servicios ===")

    es_ok = await check_elasticsearch()
    api_ok = await check_products_api()

    logger.info("=== Resumen ===")
    if es_ok and api_ok:
        logger.info("✅ Todos los servicios funcionando correctamente")
        return True
    else:
        logger.error("❌ Algunos servicios tienen problemas")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
