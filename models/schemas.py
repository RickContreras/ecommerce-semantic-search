from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductoAPI(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    price: str
    image_url: Optional[str] = None
    category: Optional[str] = "General"
    stock: Optional[int] = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ProductoIndexado(BaseModel):
    id: str
    name: str
    description: str
    category: str
    price: float
    stock: int
    image_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    embedding: Optional[List[float]] = None


class BusquedaRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: Optional[int] = Field(5, ge=1, le=50)
    category: Optional[str] = None
    price_max: Optional[float] = Field(None, ge=0)
    price_min: Optional[float] = Field(None, ge=0)


class ResultadoBusqueda(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    score: float


class BusquedaResponse(BaseModel):
    query: str
    total_resultados: int
    tiempo_ms: int
    resultados: List[ResultadoBusqueda]


class HealthResponse(BaseModel):
    status: str
    elasticsearch: str
    products_api: str
    timestamp: datetime


class SyncResponse(BaseModel):
    status: str
    productos_sincronizados: int
    tiempo_ms: int
    errores: List[str] = []
