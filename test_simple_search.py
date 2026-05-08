"""Script para probar la búsqueda simple (sin embeddings) con Elasticsearch."""
import asyncio
import sys
from typing import List
from datetime import datetime

from services.elasticsearch_service import get_elasticsearch_service
from models.schemas import SearchRequest


async def print_results(query: str, results: dict):
    """Imprime los resultados de búsqueda de forma legible."""
    print(f"\n{'='*80}")
    print(f"QUERY: '{query}'")
    print(f"{'='*80}")
    print(f"Total de resultados: {results['total_resultados']}")
    print(f"Tiempo de búsqueda: {results['tiempo_busqueda_ms']} ms")

    if results['filtros_aplicados'].category:
        print(f"Categoría filtrada: {results['filtros_aplicados'].category}")

    if results['filtros_aplicados'].price_range:
        price_range = results['filtros_aplicados'].price_range
        print(f"Rango de precios: ${price_range.get('min', 0)} - ${price_range.get('max', 'Sin límite')}")

    print(f"\n{'='*80}")
    print("RESULTADOS:")
    print(f"{'='*80}\n")

    if not results['resultados']:
        print("No se encontraron resultados.\n")
        return

    for i, product in enumerate(results['resultados'], 1):
        print(f"{i}. {product.name}")
        print(f"   ID: {product.id}")
        print(f"   Categoría: {product.category}")
        print(f"   Precio: ${product.price:,.2f}")
        print(f"   Stock: {product.stock}")
        print(f"   Score: {product.score_semantico:.4f} - Relevancia: {product.relevancia}")
        print(f"   Descripción: {product.description[:100]}...")
        print()


async def test_simple_search():
    """Realiza pruebas de búsqueda simple."""
    es_service = get_elasticsearch_service()

    try:
        # Verificar conexión
        print("🔍 Verificando conexión con Elasticsearch...")
        health = await es_service.check_connection()

        if health['status'] != 'up':
            print("❌ Error: Elasticsearch no está disponible")
            print(f"   Estado: {health}")
            return

        print(f"✅ Elasticsearch conectado - Estado del cluster: {health.get('cluster_health', 'unknown')}")

        # Verificar que hay productos indexados
        stats = await es_service.get_index_stats()
        total_productos = stats.get('total_productos', 0)

        if total_productos == 0:
            print("\n⚠️  Advertencia: No hay productos indexados")
            print("   Por favor ejecuta primero: python -m scripts.setup_index")
            return

        print(f"✅ Productos indexados: {total_productos}\n")

        # Casos de prueba
        test_cases = [
            {
                "query": "laptop",
                "description": "Búsqueda de laptops"
            },
            {
                "query": "camara",
                "description": "Búsqueda con tilde (cámara)"
            },
            {
                "query": "telefono",
                "description": "Búsqueda de teléfonos"
            },
            {
                "query": "gaming",
                "description": "Búsqueda de productos para gaming"
            },
            {
                "query": "mouse inalambrico",
                "description": "Búsqueda de múltiples palabras"
            },
            {
                "query": "auriculares bluetooth",
                "description": "Búsqueda combinada"
            },
        ]

        print("\n" + "="*80)
        print("INICIANDO PRUEBAS DE BÚSQUEDA SIMPLE")
        print("="*80)

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}/{len(test_cases)}: {test_case['description']}")

            search_request = SearchRequest(
                query=test_case['query'],
                top_k=5
            )

            try:
                results = await es_service.search_products_simple(search_request)
                await print_results(test_case['query'], results)

            except Exception as e:
                print(f"❌ Error en búsqueda: {str(e)}")
                continue

            # Esperar un poco entre búsquedas
            await asyncio.sleep(0.5)

        # Pruebas con filtros
        print("\n" + "="*80)
        print("PRUEBAS CON FILTROS")
        print("="*80)

        # Búsqueda con filtro de categoría
        print("\n📝 Búsqueda con filtro de categoría")
        categories = await es_service.get_categories()
        if categories:
            category = categories[0].name
            search_request = SearchRequest(
                query="producto",
                category=category,
                top_k=5
            )
            results = await es_service.search_products_simple(search_request)
            await print_results(f"producto (categoría: {category})", results)

        # Búsqueda con filtro de precio
        print("\n📝 Búsqueda con filtro de precio")
        search_request = SearchRequest(
            query="computador",
            price_min=500,
            price_max=2000,
            top_k=5
        )
        results = await es_service.search_products_simple(search_request)
        await print_results("computador (precio: $500-$2000)", results)

        # Búsqueda solo productos con stock
        print("\n📝 Búsqueda solo productos con stock")
        search_request = SearchRequest(
            query="laptop",
            include_out_of_stock=False,
            top_k=5
        )
        results = await es_service.search_products_simple(search_request)
        await print_results("laptop (solo con stock)", results)

        print("\n" + "="*80)
        print("✅ PRUEBAS COMPLETADAS")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        await es_service.close()


async def test_comparison():
    """Compara resultados entre búsqueda simple y semántica."""
    es_service = get_elasticsearch_service()

    try:
        print("\n" + "="*80)
        print("COMPARACIÓN: BÚSQUEDA SIMPLE VS SEMÁNTICA")
        print("="*80)

        query = "laptop gaming potente"

        print(f"\n🔍 Query: '{query}'\n")

        # Búsqueda simple
        print("📄 BÚSQUEDA SIMPLE (sin embeddings):")
        print("-" * 80)
        search_request = SearchRequest(query=query, top_k=5)
        simple_results = await es_service.search_products_simple(search_request)

        print(f"Tiempo: {simple_results['tiempo_busqueda_ms']} ms")
        print(f"Resultados: {simple_results['total_resultados']}")
        for i, product in enumerate(simple_results['resultados'], 1):
            print(f"  {i}. {product.name} (score: {product.score_semantico:.4f})")

        # Búsqueda semántica
        print("\n🧠 BÚSQUEDA SEMÁNTICA (con embeddings):")
        print("-" * 80)
        search_request = SearchRequest(query=query, top_k=5)
        semantic_results = await es_service.search_products(search_request)

        print(f"Tiempo: {semantic_results['tiempo_busqueda_ms']} ms")
        print(f"Resultados: {semantic_results['total_resultados']}")
        for i, product in enumerate(semantic_results['resultados'], 1):
            print(f"  {i}. {product.name} (score: {product.score_semantico:.4f})")

        print("\n" + "="*80)
        print("ANÁLISIS:")
        print("="*80)
        print(f"Diferencia de tiempo: {abs(simple_results['tiempo_busqueda_ms'] - semantic_results['tiempo_busqueda_ms'])} ms")
        print(f"La búsqueda {'simple' if simple_results['tiempo_busqueda_ms'] < semantic_results['tiempo_busqueda_ms'] else 'semántica'} fue más rápida")

    except Exception as e:
        print(f"\n❌ Error en comparación: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        await es_service.close()


async def main():
    """Función principal."""
    print("\n" + "="*80)
    print("TEST DE BÚSQUEDA SIMPLE CON ELASTICSEARCH")
    print("="*80)
    print("Este script prueba la búsqueda textual sin usar embeddings")
    print("="*80 + "\n")

    # Elegir modo de prueba
    if len(sys.argv) > 1 and sys.argv[1] == "--compare":
        await test_comparison()
    else:
        await test_simple_search()


if __name__ == "__main__":
    asyncio.run(main())
