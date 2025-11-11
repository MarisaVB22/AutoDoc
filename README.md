# AutoDoc

Este repositorio ahora contiene una aplicación Flask mínima.

Estructura:

```powershell
app/
│
├── __init__.py
├── routes/
│   └── services.py
└── utils/
    └── funciones.py
main.py
```

Instrucciones rápidas (Windows PowerShell):

1. Crear un entorno virtual e instalar dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Ejecutar la aplicación localmente:

```powershell
python main.py
```

La aplicación escuchará por defecto en http://127.0.0.1:5000/ y expondrá una ruta `/` que devuelve un JSON simple.
