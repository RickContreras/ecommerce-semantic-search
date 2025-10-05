import httpx
from typing import List, Dict, Any, Optional
import asyncio
from config import settings
from utils.logger import setup_logger
from models.schemas import ProductoAPI, ProductoIndexado

logger = setup_logger("product_service")


class ProductService:
    def __init__(self):
        self.base_url = settings.PRODUCTOS_API_URL
        self.timeout = settings.SYNC_TIMEOUT

    async def fetch_products(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene productos de la API externa con paginación

        Args:
            skip: Número de productos a omitir
            limit: Número máximo de productos a obtener

        Returns:
            Lista de productos
        """
        url = f"{self.base_url}?skip={skip}&limit={limit}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()

                productos_data = response.json()

                # Si la respuesta es una lista directa
                if isinstance(productos_data, list):
                    productos = productos_data
                # Si la respuesta tiene estructura con 'items' o similar
                elif isinstance(productos_data, dict):
                    productos = productos_data.get(
                        'items', productos_data.get('data', []))
                else:
                    productos = []

                logger.info(
                    f"Obtenidos {len(productos)} productos desde skip={skip}")
                return productos

        except httpx.TimeoutException:
            logger.error(f"Timeout al obtener productos desde {url}")
            return []
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Error HTTP {e.response.status_code} al obtener productos: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado al obtener productos: {e}")
            return []

    async def fetch_all_products(self, batch_size: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene todos los productos disponibles usando paginación

        Args:
            batch_size: Tamaño del lote para cada petición

        Returns:
            Lista completa de productos
        """
        all_products = []
        skip = 0

        while True:
            batch = await self.fetch_products(skip=skip, limit=batch_size)

            if not batch:
                # No hay más productos
                break

            all_products.extend(batch)

            # Si el lote es menor que batch_size, hemos llegado al final
            if len(batch) < batch_size:
                break

            skip += batch_size

            # Pequeña pausa para no sobrecargar la API
            await asyncio.sleep(0.1)

        logger.info(f"Total de productos obtenidos: {len(all_products)}")
        return all_products

    def transform_product(self, producto_api: Dict[str, Any]) -> ProductoIndexado:
        """
        Transforma un producto de la API externa al formato interno

        Args:
            producto_api: Producto en formato de la API externa

        Returns:
            Producto en formato interno para indexación
        """
        try:
            return ProductoIndexado(
                id=producto_api["id"],
                name=producto_api["name"],
                description=producto_api.get("description", ""),
                category=producto_api.get("category", "General"),
                price=float(producto_api.get("price", 0)),
                stock=int(producto_api.get("stock", 0)),
                image_url=producto_api.get("image_url"),
                created_at=producto_api.get("created_at"),
                updated_at=producto_api.get("updated_at")
            )
        except (ValueError, KeyError) as e:
            logger.error(
                f"Error transformando producto {producto_api.get('id', 'unknown')}: {e}")
            raise e

    async def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un producto específico por ID

        Args:
            product_id: ID del producto

        Returns:
            Producto encontrado o None
        """
        # Nota: Esta implementación asume que necesitamos obtener todos los productos
        # y filtrar. En una implementación real, la API debería tener un endpoint
        # específico para obtener por ID
        try:
            products = await self.fetch_all_products()
            for product in products:
                if product.get("id") == product_id:
                    return product
            return None
        except Exception as e:
            logger.error(f"Error obteniendo producto {product_id}: {e}")
            return None

    def check_api_health(self) -> bool:
        """
        Verifica si la API de productos está disponible

        Returns:
            True si la API está disponible, False en caso contrario
        """
        try:
            import requests
            response = requests.get(f"{self.base_url}?limit=1", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error verificando salud de la API: {e}")
            return False
