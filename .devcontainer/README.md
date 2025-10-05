# 🚀 DevContainer con Elasticsearch Automático

Este devcontainer está configurado para iniciar Elasticsearch automáticamente cada vez que se crea o inicia el contenedor.

## 📋 ¿Qué se configuró?

### 1. **devcontainer.json**

```json
{
  "postCreateCommand": "bash /workspace/.devcontainer/setup.sh",
  "postStartCommand": "bash /workspace/.devcontainer/start-services.sh"
}
```

- **postCreateCommand**: Se ejecuta una sola vez cuando se crea el devcontainer
- **postStartCommand**: Se ejecuta cada vez que se inicia el devcontainer

### 2. **Scripts Automáticos**

#### `setup.sh` (Configuración inicial)

- Instala dependencias de Python
- Crea directorios necesarios
- Configuración que se ejecuta una sola vez

#### `start-services.sh` (Inicio de servicios)

- Verifica si Elasticsearch está ejecutándose
- Lo inicia si no está corriendo
- Espera hasta que esté completamente listo
- Muestra información útil

#### `test-devcontainer.sh` (Verificación manual)

- Script para probar manualmente que todo funciona
- Útil para debugging y verificación

### 3. **docker-compose.yml mejorado**

- Health checks para Elasticsearch
- Configuración optimizada para desarrollo
- Reinicio automático (`restart: unless-stopped`)

## 🎯 Uso Automático

Cuando crees o reinicies el devcontainer:

1. **Automático**: Los servicios se inician automáticamente
2. **Espera**: El sistema espera hasta que Elasticsearch esté listo
3. **Notificación**: Recibes confirmación cuando todo está funcionando

## 🧪 Verificación Manual

Si quieres verificar manualmente que todo funciona:

```bash
# Ejecutar script de prueba completo
/workspace/.devcontainer/test-devcontainer.sh

# O verificaciones individuales
curl http://localhost:9200/_cluster/health
python test_elasticsearch.py
```

## 🔧 Troubleshooting

### Si Elasticsearch no inicia automáticamente:

1. **Verificar Docker**:

   ```bash
   # Desde fuera del devcontainer
   cd .devcontainer
   docker-compose ps
   docker-compose logs elasticsearch
   ```

2. **Iniciar manualmente**:

   ```bash
   cd .devcontainer
   docker-compose up -d elasticsearch
   ```

3. **Revisar logs**:
   ```bash
   # Ver logs del script de inicio
   cat /workspace/logs/start-services.log
   ```

### Si hay problemas de memoria:

El contenedor está configurado con 512MB para Elasticsearch. Si necesitas más:

```yaml
# En docker-compose.yml, cambiar:
"ES_JAVA_OPTS=-Xms512m -Xmx1g"
```

## 📈 Beneficios de esta configuración

✅ **Automático**: No necesitas recordar iniciar servicios  
✅ **Rápido**: Elasticsearch se inicia en paralelo con el devcontainer  
✅ **Robusto**: Health checks y reintentos automáticos  
✅ **Informativo**: Feedback claro del estado de los servicios  
✅ **Debuggeable**: Scripts y logs para troubleshooting

## 🚦 Próximos pasos

Una vez que el devcontainer esté funcionando:

1. **Verificar**: `curl http://localhost:9200`
2. **Probar API**: `python test_elasticsearch.py`
3. **Desarrollar**: ¡Tu entorno está listo!

---

💡 **Tip**: Si realizas cambios en la configuración del devcontainer, reconstruye con "Dev Container: Rebuild Container" en VS Code.
