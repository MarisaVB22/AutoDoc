# AutoDoc

Este repositorio contiene una aplicación Flask mínima conectada a PostgreSQL usando Docker, con inicialización automática de la base de datos y pgAdmin para gestión visual.

---

## Stack del proyecto

### Frontend
- **React** → Interfaz de usuario.

### Backend
- **Flask** → API y endpoints.
- **Docker + PostgreSQL** → Desarrollo local.
  - La base de datos local se ejecuta en contenedores Docker y se inicializa automáticamente desde `data.sql`.
  - En el futuro:
    - La base de datos se migrará a un **servidor de Desarrollo**.
    - Finalmente, se desplegará en **Producción**.

---

## Estructura del proyecto:
```powershell
app/
│
├── __init__.py
├── routes/
│   └── services.py   # Endpoints
└── utils/
    └── funciones.py  # Funciones auxiliares a los endpoints
└── db/
    └── postgres/
        └── data.sql  # Script de inicialización de la base de datos      
    └── queries.py    # Constantes que contienen las consultas a la BBDD
    └── psql_connection_pool.py # Pool de conexiones (para mejorar eficiencia de la conexión con la BBDD)
main.py
docker-compose.yml    # Contenedores para PostgreSQL
requirements.txt      # Instalaciones necesarias
```

---

## Instrucciones rápidas (Windows PowerShell):

### 1. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

### 2. Levantar la base de datos y pgAdmin con Docker:

```
docker-compose up -d
```

Esto levantará:
- PostgreSQL (postgres_db) en el puerto 5432 y creará automáticamente:
    - Usuario user
    - Base de datos autodoc_db
    - Schema documentos
    - Tabla documentos.documentos con registros de ejemplo
- pgAdmin (pgadmin) en el puerto 8080

### 3. Acceder a pgAmin para ver la BBDD de forma gráfica (opcional)

- Abrir navegador: http://localhost:8080
    - Usuario: admin@admin.com
    - Contraseña: admin123
- Agregar un servidor:
    - Name: PostgresLocal
    - Host name/address: postgres
    - Port: 5432
    - Base de datos de mantenimiento: autodoc_db
    - Username: autodoc_user
    - Password: autodoc
- Guardar y conectar
- Explorar la base de datos autodoc_db → Schemas → documentos → Tables → documentos.

### 4. Ejecutar la aplicación Flask localmente:

```powershell
python main.py
```

La aplicación escuchará por defecto en http://127.0.0.1:5000/ y expondrá una ruta `/` que devuelve un JSON simple.

### 5. Detener contenedores Docker:
Para detener los contenedores sin borrarlos: detiene los contenedores, pero deja los volúmenes y redes creadas para poder levantarlos de nuevo.
```powershell
docker-compose stop
```
Para eliminar contenedores y redes pero mantener los volúmenes:
```powershell
docker-compose down
```
Para eliminar contenedores, redes y volúmenes (borra también la base de datos):
```powershell
docker-compose down -v
```

---

# DOCUMENTACIÓN TÉCNICA

## Endpoints principales

### Proyectos
- `GET /proyectos` → Lista todos los proyectos
- `POST /proyectos` → Crea un nuevo proyecto
- `GET /proyectos/{id}` → Obtiene un proyecto por ID
- `PUT /proyectos/{id}` → Modifica un proyecto
- `DELETE /proyectos/{id}` → Elimina un proyecto

### Documentos
- `GET /proyectos/{idProyecto}/documentos` → Lista documentos de un proyecto
- `POST /proyectos/{idProyecto}/documentos` → Subir un nuevo documento
- `GET /proyectos/{idProyecto}/documentos/{idDocumento}` → Obtener documento
- `PUT /proyectos/{idProyecto}/documentos/{idDocumento}` → Modificar documento
- `DELETE /proyectos/{idProyecto}/documentos/{idDocumento}` → Eliminar documento
- `POST /proyectos/{idProyecto}/documentos/buscar` → Buscar documentos con IA
- `POST /proyectos/{idProyecto}/documentos/analizar` → Analizar documento con IA

## Modelos de datos

### Proyecto
| Campo       | Tipo    | Descripción |
|------------|---------|-------------|
| idProyecto | integer | Identificador del proyecto |
| nombre     | string  | Nombre del proyecto |
| descripcion| string  | Descripción del proyecto |
| proyecto_url | string | URL del proyecto |

### Documento
| Campo       | Tipo    | Descripción |
|------------|---------|-------------|
| idDocumento | integer | Identificador del documento |
| nombre      | string  | Nombre del documento |
| descripcion | string  | Descripción del documento |
| url         | string  | URL del archivo subido |
