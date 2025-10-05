from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from config import settings
from utils.logger import setup_logger

logger = setup_logger("embedding_service")


class EmbeddingService:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        """Carga el modelo de embeddings"""
        try:
            logger.info(f"Cargando modelo: {settings.MODEL_NAME}")
            self.model = SentenceTransformer(settings.MODEL_NAME)
            logger.info("Modelo cargado exitosamente")
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            raise e

    def encode_text(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Genera embeddings para texto o lista de textos

        Args:
            text: Texto individual o lista de textos

        Returns:
            Embedding o lista de embeddings
        """
        if not self.model:
            raise ValueError("Modelo no cargado")

        try:
            if isinstance(text, str):
                # Texto individual
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            else:
                # Lista de textos
                embeddings = self.model.encode(text, convert_to_numpy=True)
                return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generando embeddings: {e}")
            raise e

    def encode_product(self, name: str, description: str, category: str) -> List[float]:
        """
        Genera embedding para un producto combinando nombre, descripción y categoría

        Args:
            name: Nombre del producto
            description: Descripción del producto  
            category: Categoría del producto

        Returns:
            Embedding del producto
        """
        # Combinar información del producto en un texto único
        combined_text = f"{name}. {description}. Categoría: {category}"

        return self.encode_text(combined_text)

    def encode_query(self, query: str, category: str = None) -> List[float]:
        """
        Genera embedding para una consulta de búsqueda

        Args:
            query: Consulta de búsqueda
            category: Categoría opcional para filtrar

        Returns:
            Embedding de la consulta
        """
        # Si hay categoría, incluirla en la consulta
        if category:
            enhanced_query = f"{query}. Categoría: {category}"
        else:
            enhanced_query = query

        return self.encode_text(enhanced_query)
