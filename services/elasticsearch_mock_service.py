"""
Servicio mock de Elasticsearch para desarrollo sin Elasticsearch ejecutándose
"""
from typing import List, Dict, Any, Optional
from utils.logger import setup_logger

logger = setup_logger("elasticsearch_mock")


class ElasticsearchMockService:
    """Servicio mock que simula Elasticsearch para desarrollo"""

    def __init__(self):
        self.index_name = "productos_mock"
        self.products_data = []  # Almacenamiento en memoria
        logger.info("Iniciando servicio mock de Elasticsearch")

    async def check_connection(self) -> bool:
        """Simula conexión exitosa"""
        return True

    def create_index(self) -> bool:
        """Simula creación de índice exitosa"""
        logger.info(f"Índice mock {self.index_name} creado")
        return True

    def index_product(self, producto: Dict[str, Any]) -> bool:
        """Simula indexación de producto"""
        self.products_data.append(producto)
        return True

    def bulk_index_products(self, productos: List[Dict[str, Any]]) -> tuple:
        """Simula indexación masiva"""
        if not productos:
            return 0, []

        self.products_data.extend(productos)
        logger.info(f"Mock: Indexados {len(productos)} productos")
        return len(productos), []

    def semantic_search(
        self,
        query_vector: List[float],
        size: int = 10,
        category: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Simula búsqueda semántica con búsqueda por texto"""

        # Filtrar productos basado en criterios
        filtered_products = self.products_data.copy()

        if category:
            filtered_products = [p for p in filtered_products if p.get(
                "category", "").lower() == category.lower()]

        if price_min is not None:
            filtered_products = [
                p for p in filtered_products if p.get("price", 0) >= price_min]

        if price_max is not None:
            filtered_products = [
                p for p in filtered_products if p.get("price", 0) <= price_max]

        # Simular score basado en si el nombre/descripción contiene palabras similares
        # En una implementación real, esto sería mucho más sofisticado
        results = []
        for product in filtered_products[:size]:
            # Score simulado
            score = 0.8 + (len(results) * 0.01)  # Score decreciente
            product_copy = product.copy()
            product_copy["score"] = score
            results.append(product_copy)

        logger.info(
            f"Mock: Búsqueda simulada retornó {len(results)} resultados")
        return results

    def get_index_stats(self) -> Dict[str, Any]:
        """Simula estadísticas del índice"""
        return {
            "total_documents": len(self.products_data),
            "index_size": len(str(self.products_data)),
            "status": "mock_healthy"
        }
