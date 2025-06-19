# Plan de migración del proyecto a Docker

## Objetivo

Contenerizar toda la aplicación (backend, frontend y base de datos) usando Docker y Docker Compose para facilitar el despliegue, la portabilidad y el desarrollo local y en producción.

---

## Pasos para la migración

### 1. Instalación de Docker y Docker Compose

- **Windows/Mac:**
  - Descargar e instalar Docker Desktop: https://www.docker.com/products/docker-desktop
- **Linux:**
  - Instalar Docker Engine y Docker Compose:
    ```sh
    sudo apt update
    sudo apt install docker.io docker-compose -y
    sudo systemctl enable --now docker
    sudo usermod -aG docker $USER
    # Cierra sesión y vuelve a entrar para aplicar el grupo
    ```

### 2. Crear el `Dockerfile` para el backend
- Define cómo construir la imagen de tu backend (FastAPI, etc.).
- Incluye dependencias, copia el código y expón el puerto necesario.

### 3. Crear el `Dockerfile` para el frontend (opcional)
- Si tienes frontend React, crea un Dockerfile para servirlo (por ejemplo, con nginx o node).

### 4. Crear el archivo `docker-compose.yml`
- Orquesta los servicios: backend, frontend (opcional) y base de datos (PostgreSQL recomendado).
- Define variables de entorno, volúmenes y redes.

### 5. Configurar variables de entorno
- Usa archivos `.env` para credenciales y configuración sensible.
- No subas `.env` a git.

### 6. Adaptar la app para leer la configuración de entorno
- Asegúrate de que la app lee las variables de entorno para la conexión a la base de datos y otros servicios.

### 7. Probar el entorno en local
- Levanta todo con:
  ```sh
  docker-compose up --build
  ```
- Accede a la app y verifica que todo funciona.

### 8. Documentar el flujo de trabajo en Docker
- Cómo desarrollar, testear y desplegar usando Docker.
- Cómo acceder a la base de datos y logs.

---

## Recursos útiles
- [Documentación oficial de Docker](https://docs.docker.com/)
- [Documentación oficial de Docker Compose](https://docs.docker.com/compose/)

---

**Este documento servirá como guía para migrar y mantener el proyecto en Docker.**
