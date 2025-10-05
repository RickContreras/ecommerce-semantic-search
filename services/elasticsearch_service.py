from elasticsearch import Elasticsearch
from typing import List, Dict, Any, Optional
import json
from config import settings
from utils.logger import setup_logger

logger = setup_logger("elasticsearch_service")


class ElasticsearchService:
    def __init__(self):
        self.client = Elasticsearch([settings.ELASTICSEARCH_URL])
        self.index_name = settings.INDEX_NAME

    async def check_connection(self) -> bool:
        """Verifica la conexión con Elasticsearch"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Error conectando a Elasticsearch: {e}")
            return False

    def create_index(self) -> bool:
        """Crea el índice con el mapeo correcto"""
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text", "analyzer": "spanish"},
                    "description": {"type": "text", "analyzer": "spanish"},
                    "category": {"type": "keyword"},
                    "price": {"type": "float"},
                    "stock": {"type": "integer"},
                    "image_url": {"type": "keyword", "index": False},
                    "created_at": {"type": "date", "index": False},
                    "updated_at": {"type": "date", "index": False},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 384,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            },
            "settings": {
                "analysis": {
                    "analyzer": {
                        "spanish": {
                            "tokenizer": "standard",
                            "filter": ["lowercase", "spanish_stop", "spanish_stemmer"]
                        }
                    },
                    "filter": {
                        "spanish_stop": {
                            "type": "stop",
                            "stopwords": "_spanish_"
                        },
                        "spanish_stemmer": {
                            "type": "stemmer",
                            "language": "spanish"
                        }
                    }
                }
            }
        }

        try:
            if self.client.indices.exists(index=self.index_name):
                logger.info(f"Índice {self.index_name} ya existe")
                return True

            self.client.indices.create(index=self.index_name, body=mapping)
            logger.info(f"Índice {self.index_name} creado exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error creando índice: {e}")
            return False

    def index_product(self, producto: Dict[str, Any]) -> bool:
        """Indexa un producto individual"""
        try:
            self.client.index(
                index=self.index_name,
                id=producto["id"],
                body=producto
            )
            return True
        except Exception as e:
            logger.error(
                f"Error indexando producto {producto.get('id', 'unknown')}: {e}")
            return False

    def bulk_index_products(self, productos: List[Dict[str, Any]]) -> tuple:
        """Indexa múltiples productos usando bulk API"""
        if not productos:
            return 0, []

        actions = []
        for producto in productos:
            actions.append({
                "_index": self.index_name,
                "_id": producto["id"],
                "_source": producto
            })

        try:
            from elasticsearch.helpers import bulk
            success, failed = bulk(
                self.client,
                actions,
                index=self.index_name,
                raise_on_error=False,
                raise_on_exception=False
            )

            logger.info(f"Productos indexados exitosamente: {success}")
            if failed:
                logger.warning(f"Productos fallidos: {len(failed)}")

            return success, failed
        except Exception as e:
            logger.error(f"Error en bulk indexing: {e}")
            return 0, [str(e)]

    def semantic_search(
        self,
        query_vector: List[float],
        size: int = 10,
        category: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Realiza búsqueda semántica con filtros opcionales"""

        # Construir filtros
        filters = []
        if category:
            filters.append({"term": {"category": category}})
        if price_min is not None or price_max is not None:
            price_range = {}
            if price_min is not None:
                price_range["gte"] = price_min
            if price_max is not None:
                price_range["lte"] = price_max
            filters.append({"range": {"price": price_range}})

        # Construir query
        search_body = {
            "size": size,
            "query": {
                "script_score": {
                    "query": {
                        "bool": {
                            "filter": filters
                        }
                    } if filters else {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            }
        }

        try:
            response = self.client.search(
                index=self.index_name,
                body=search_body,
                timeout=f"{settings.SEARCH_TIMEOUT}s"
            )

            results = []
            for hit in response["hits"]["hits"]:
                result = hit["_source"]
                # Ajustar score (removemos el +1.0)
                result["score"] = hit["_score"] - 1.0
                results.append(result)

            return results
        except Exception as e:
            logger.error(f"Error en búsqueda semántica: {e}")
            return []

    def get_index_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del índice"""
        try:
            stats = self.client.indices.stats(index=self.index_name)
            count = self.client.count(index=self.index_name)

            return {
                "total_documents": count["count"],
                "index_size": stats["indices"][self.index_name]["total"]["store"]["size_in_bytes"],
                "status": "healthy"
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}
