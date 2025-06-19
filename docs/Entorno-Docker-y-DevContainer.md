# Entorno Docker y Dev Container para Crypto Bot

Este proyecto está preparado para funcionar de forma óptima en un entorno Dockerizado usando Dev Containers de VS Code. Aquí tienes un resumen de las ventajas y el flujo recomendado, así como instrucciones para usuarios avanzados.

## Ventajas del entorno Docker/Dev Container
- **Sin conflictos de dependencias**: Todo el entorno (Python, Node, dependencias, extensiones) está preinstalado y aislado.
- **Sin pasos manuales de instalación**: Al abrir el proyecto en VS Code y seleccionar "Reopen in Container", las dependencias se instalan automáticamente.
- **Sin problemas de permisos ni rutas**: El workspace y los puertos están correctamente configurados.
- **Sin necesidad de venv ni monkeypatches**: El contenedor ya incluye todo lo necesario.

## Cómo usar el entorno Docker/Dev Container
1. **Abre el proyecto en VS Code** (con la extensión "Dev Containers" instalada).
2. VS Code te sugerirá "Reopen in Container". Haz clic y espera a que se construya el entorno.
3. ¡Listo! Ya puedes usar la terminal, depurar, instalar paquetes, ejecutar backend y frontend, etc.

### Acceso a la app
- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

> Si necesitas exponer otros puertos, usa la opción "Forward a Port" de VS Code.

## Instrucciones manuales (solo si NO usas el contenedor)
Si prefieres instalar todo localmente, sigue las instrucciones clásicas del README principal.

---

Para detalles completos, consulta la guía: [docs/Entorno-Docker-y-DevContainer.md](docs/Entorno-Docker-y-DevContainer.md)
