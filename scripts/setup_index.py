#!/usr/bin/env python3
"""
Script para configurar el índice inicial de Elasticsearch
"""

from utils.logger import setup_logger
from services.elasticsearch_service import ElasticsearchService
import asyncio
import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


logger = setup_logger("setup_index")


async def main():
    """Función principal para configurar el índice"""

    logger.info("Iniciando configuración del índice de Elasticsearch...")

    es_service = ElasticsearchService()

    # Verificar conexión
    if not await es_service.check_connection():
        logger.error(
            "No se puede conectar a Elasticsearch. Verifica que esté ejecutándose.")
        return False

    # Crear índice
    if es_service.create_index():
        logger.info("Índice configurado exitosamente")
        return True
    else:
        logger.error("Error configurando el índice")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
