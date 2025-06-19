# Docker Environment and Dev Container for Crypto Bot

This project is optimized to run in a Dockerized environment using VS Code Dev Containers. Here is a summary of the advantages, the recommended workflow, and instructions for advanced users.

## Advantages of Docker/Dev Container Environment
- **No dependency conflicts**: The entire environment (Python, Node, dependencies, extensions) is pre-installed and isolated.
- **No manual installation steps**: When you open the project in VS Code and select "Reopen in Container", dependencies are installed automatically.
- **No permission or path issues**: The workspace and ports are properly configured.
- **No need for venv or monkeypatches**: The container already includes everything you need.

## How to Use the Docker/Dev Container Environment
1. **Open the project in VS Code** (with the "Dev Containers" extension installed).
2. VS Code will suggest "Reopen in Container". Click it and wait for the environment to build.
3. Done! You can now use the terminal, debug, install packages, run backend and frontend, etc.

### App Access
- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

> If you need to expose other ports, use the "Forward a Port" option in VS Code.

## Manual Instructions (only if NOT using the container)
If you prefer to install everything locally, follow the classic instructions in the main README.

---

For full details, see the guide: [docs/Entorno-Docker-y-DevContainer.md](docs/Entorno-Docker-y-DevContainer.md)
