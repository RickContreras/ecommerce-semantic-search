#!/usr/bin/env python3
"""
Script simple para probar la conexión con Elasticsearch
"""

import requests
import json
from elasticsearch import Elasticsearch
import sys
from config import settings


def test_connection_with_requests():
    """Prueba usando requests directamente"""
    print("🔍 Probando conexión con requests...")
    print(f"🔗 URL: {settings.ELASTICSEARCH_URL}")

    try:
        response = requests.get(f"{settings.ELASTICSEARCH_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Elasticsearch está funcionando!")
            print(
                f"📋 Versión: {data.get('version', {}).get('number', 'unknown')}")
            print(f"🏷️  Cluster: {data.get('cluster_name', 'unknown')}")
            print(f"🆔 Node: {data.get('name', 'unknown')}")
            return True
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(
            f"❌ No se puede conectar a Elasticsearch en {settings.ELASTICSEARCH_URL}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_connection_with_elasticsearch_client():
    """Prueba usando el cliente oficial de Elasticsearch"""
    print("\n🔍 Probando con cliente oficial de Elasticsearch...")

    try:
        client = Elasticsearch([settings.ELASTICSEARCH_URL])

        if client.ping():
            print("✅ Conexión exitosa con cliente ES!")

            # Obtener información del cluster
            info = client.info()
            print(f"📋 Versión: {info['version']['number']}")
            print(f"🏷️  Cluster: {info['cluster_name']}")
            print(f"🆔 Node: {info['name']}")

            return True
        else:
            print("❌ No se pudo hacer ping a Elasticsearch")
            return False
    except Exception as e:
        print(f"❌ Error con cliente ES: {e}")
        return False


def test_cluster_health():
    """Prueba la salud del cluster"""
    print("\n🏥 Verificando salud del cluster...")

    try:
        response = requests.get(
            f"{settings.ELASTICSEARCH_URL}/_cluster/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            status = health.get('status', 'unknown')

            if status == 'green':
                print("✅ Cluster está saludable (GREEN)")
            elif status == 'yellow':
                print("⚠️ Cluster tiene advertencias (YELLOW)")
            elif status == 'red':
                print("🔴 Cluster tiene problemas críticos (RED)")

            print(f"📊 Nodos: {health.get('number_of_nodes', 0)}")
            print(f"📊 Shards activos: {health.get('active_shards', 0)}")

            return True
        else:
            print(f"❌ Error obteniendo salud: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verificando salud: {e}")
        return False


def test_indices():
    """Lista los índices disponibles"""
    print("\n📂 Verificando índices...")

    try:
        response = requests.get(
            f"{settings.ELASTICSEARCH_URL}/_cat/indices?v", timeout=5)
        if response.status_code == 200:
            indices_info = response.text
            if indices_info.strip():
                print("📋 Índices encontrados:")
                print(indices_info)
            else:
                print("📋 No hay índices creados aún")
            return True
        else:
            print(f"❌ Error listando índices: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verificando índices: {e}")
        return False


def main():
    print("🚀 === PRUEBA DE ELASTICSEARCH ===")

    # Pruebas básicas
    requests_ok = test_connection_with_requests()
    client_ok = test_connection_with_elasticsearch_client()

    if requests_ok and client_ok:
        # Pruebas adicionales si la conexión funciona
        test_cluster_health()
        test_indices()

        print("\n✅ === ELASTICSEARCH ESTÁ FUNCIONANDO CORRECTAMENTE ===")
        return True
    else:
        print("\n❌ === ELASTICSEARCH NO ESTÁ DISPONIBLE ===")
        print("\n💡 Para iniciar Elasticsearch:")
        print("   1. Desde fuera del dev container:")
        print("      cd .devcontainer && docker compose up -d")
        print("   2. O verifica que los puertos estén redirigidos correctamente")
        print("   3. Espera unos minutos para que Elasticsearch inicie completamente")

        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
