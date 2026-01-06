## Ayudante de código BQL para Python en entorno Bloomberg

Este repositorio incluye un ejemplo mínimo de uso de BQL desde Python
(`bql_helper.py`). El código está pensado para ejecutarse **dentro de un
Terminal Bloomberg**, donde ya están disponibles las dependencias `bql` y
`blpapi`.

### Requisitos

- Bloomberg Terminal con permisos para BQL.
- Python 3.9+.
- Librerías oficiales instaladas dentro del terminal:

```bash
pip install bql pandas
```

### Ejemplo rápido

```bash
python bql_helper.py
```

El ejemplo ejecuta una consulta `getdata` con dos acciones (AAPL y MSFT) y
devuelve un `DataFrame` con `PX_LAST` y `CUR_MKT_CAP`.

Si desea usarlo desde su propio código:

```python
from bql_helper import fetch_dataframe

df = fetch_dataframe(
    ["IBM US Equity"],
    {"PX_LAST": {}, "CUR_MKT_CAP": {}},
    session_options={"host": "localhost", "port": 8194},  # opcional
)
print(df.head())
```

El helper atrapa la ausencia de la librería `bql` y muestra un mensaje claro
para instalarla en caso de ejecutarse fuera del entorno Bloomberg.
