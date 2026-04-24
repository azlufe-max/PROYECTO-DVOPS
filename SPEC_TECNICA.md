# OpenSpec: Sistema de Registro de Visitantes (Guest-Pass)

## 1. Arquitectura General
* **Backend:** Python con FastAPI (Puerto 8000).
* **Base de Datos:** PostgreSQL (Puerto 5432).
* **Frontend Web:** HTML/JS servido por Nginx.
* **App Local:** Script de Python (Tkinter o Consola).
* **Observabilidad:** Logs en formato JSON enviados a STDOUT para Grafana Loki.

## 2. Contrato de API (REST)
**Endpoint:** `POST /api/v1/checkin`

**Cuerpo del JSON (Payload):**
```json
{
  "nombre": "string",
  "empresa": "string",
  "motivo": "string",
  "origen": "web | local",
  "timestamp": "ISO8601 String"
}
```
### 3. Esquema de base de datos (SQL)-
**Tabla de Base de Datos (PostgreSQL)**
```sql
CREATE TABLE visitantes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    empresa VARCHAR(100),
    motivo TEXT,
    origen VARCHAR(20),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
### 4. Estandar deLogs
**Logs (STDOUT):**
```json
{"level": "INFO", "event": "visitor_checkin", "user": "nombre", "source": "web/local", "status": "success"}
```
## 5. Estructura de Directorios

El proyecto debe organizarse de la siguiente manera para mantener la separación de responsabilidades:

* **/backend**: Contendrá el código de la API (Python FastAPI), el archivo `requirements.txt` y el `Dockerfile` para la containerización.
* **/frontend-web**: Contendrá el `index.html`, los estilos CSS, el JavaScript cliente y un `Dockerfile` (usualmente basado en Nginx) para servir la web.
* **/app-local**: Contendrá el script ejecutable para la interfaz de escritorio (Python) y un archivo `README` con instrucciones de uso local.
* **/k8s**: Contendrá todos los manifiestos de Kubernetes (Deployments, Services, ConfigMaps y Secrets) para orquestar el sistema.
* **/grafana**: Contendrá los archivos JSON de exportación de los dashboards y la configuración de los data sources (Loki/PostgreSQL).
* **/database**: Opcionalmente, un script `init.sql` para la inicialización automática de la tabla en Docker.