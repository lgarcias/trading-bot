# Paper Trading Bot: Roadmap & Design

## Descripción

El objetivo es implementar un sistema de paper trading para el bot de trading, gestionable tanto desde el frontend como desde un bot de Telegram. El sistema permitirá activar estrategias en modo "live" (simulado), ejecutando órdenes en la testnet de Binance o simulando la operativa, y monitorizar los resultados en tiempo real. Además, el sistema podrá funcionar tanto con datos en tiempo real del exchange como con datos históricos (ficheros OHLCV), permitiendo pruebas flexibles y repetibles. Esto servirá como base para una futura gestión de bots reales y permitirá experimentar con estrategias sin riesgo.

## Plan de desarrollo

1. **Diseño de endpoints en FastAPI**
   - [ ] Endpoint para activar un bot de paper trading (`/papertrade/start`)
   - [ ] Endpoint para detener un bot de paper trading (`/papertrade/stop`)
   - [ ] Endpoint para consultar el estado de los bots activos (`/papertrade/status`)
   - [ ] Endpoint para consultar el histórico de trades simulados (`/papertrade/trades`)
   - [ ] Permitir seleccionar el origen de datos: `live` (exchange) o `historical` (fichero)

2. **Gestión de bots en el backend**
   - [ ] Crear un gestor de bots en memoria (o persistente) que mantenga el estado de cada bot activo.
   - [ ] Implementar la lógica para ejecutar estrategias en modo live/paper trade.
   - [ ] Integrar con la testnet de Binance o simular órdenes.
   - [ ] Implementar un sistema de feeds de datos que permita consumir tanto datos en tiempo real como históricos.
   - [ ] Permitir lanzar bots en modo histórico (reproducción de ficheros) o en modo live (exchange).

3. **Frontend y Telegram Bot**
   - [ ] Añadir opciones en el frontend para activar/desactivar bots, seleccionar el modo de datos y consultar resultados.
   - [ ] Preparar la base para integración futura con un bot de Telegram.

4. **Persistencia y monitorización**
   - [ ] Decidir si los resultados y estados se guardan en memoria, archivos o base de datos.
   - [ ] Añadir logs y monitorización de los bots activos.

5. **Pruebas y validación**
   - [ ] Crear tests para los endpoints y la lógica de paper trading.
   - [ ] Validar que los trades simulados reflejan el comportamiento esperado en ambos modos (live e histórico).
