# NOTA PARA DESARROLLADORES Y CI/CD
#
# Para ejecutar los tests correctamente, asegúrate de lanzar pytest desde la raíz del proyecto con la variable de entorno PYTHONPATH:
#
#   $env:PYTHONPATH = "."; pytest --maxfail=2 --disable-warnings -v
#
# Esto permite que los imports del paquete src funcionen correctamente en todos los tests.
#
# Si usas bash o Linux/Mac:
#   PYTHONPATH=. pytest --maxfail=2 --disable-warnings -v
