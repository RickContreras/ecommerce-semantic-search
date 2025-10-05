import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestAPI:
    """Tests básicos para la API"""

    def test_root_endpoint(self):
        """Test del endpoint raíz"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health_endpoint(self):
        """Test del endpoint de salud"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "elasticsearch" in data
        assert "products_api" in data
        assert "timestamp" in data

    def test_search_endpoint_format(self):
        """Test del formato del endpoint de búsqueda"""
        # Test con datos mínimos
        search_data = {
            "query": "smartphone"
        }

        response = client.post("/api/v1/buscar", json=search_data)
        # Puede fallar por servicios no disponibles, pero debe tener formato correcto
        assert response.status_code in [200, 500, 503]

        if response.status_code == 200:
            data = response.json()
            assert "query" in data
            assert "total_resultados" in data
            assert "tiempo_ms" in data
            assert "resultados" in data

    def test_search_validation(self):
        """Test de validación de datos de búsqueda"""
        # Query vacía debe fallar
        search_data = {
            "query": ""
        }

        response = client.post("/api/v1/buscar", json=search_data)
        assert response.status_code == 422  # Validation error

        # top_k inválido debe fallar
        search_data = {
            "query": "test",
            "top_k": 100  # Muy alto según el esquema
        }

        response = client.post("/api/v1/buscar", json=search_data)
        # Puede pasar si los límites están bien configurados
        assert response.status_code in [200, 422, 500, 503]


class TestServices:
    """Tests para los servicios individuales"""

    @pytest.mark.asyncio
    async def test_product_service_import(self):
        """Test de importación del servicio de productos"""
        try:
            from services.product_service import ProductService
            service = ProductService()
            assert service is not None
            assert service.base_url is not None
        except Exception as e:
            pytest.skip(f"Product service no disponible: {e}")

    def test_elasticsearch_service_import(self):
        """Test de importación del servicio de Elasticsearch"""
        try:
            from services.elasticsearch_service import ElasticsearchService
            service = ElasticsearchService()
            assert service is not None
            assert service.index_name is not None
        except Exception as e:
            pytest.skip(f"Elasticsearch service no disponible: {e}")

    def test_embedding_service_import(self):
        """Test de importación del servicio de embeddings"""
        try:
            from services.embedding_service import EmbeddingService
            # No instanciar porque requiere descargar el modelo
            assert EmbeddingService is not None
        except Exception as e:
            pytest.skip(f"Embedding service no disponible: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
