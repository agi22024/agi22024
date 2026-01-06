"""Utilidades básicas para trabajar con BQL desde Python en un entorno Bloomberg.

Este módulo no abre conexiones por sí solo; solamente envuelve las llamadas
habituales para que el código sea más legible. Las dependencias de Bloomberg
(`bql` y `blpapi`) deben estar instaladas en el terminal de Bloomberg donde se
ejecute el script.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Union

if TYPE_CHECKING:  # Solo para type checkers, evita dependencia en tiempo de ejecución
    import pandas as pd

logger = logging.getLogger(__name__)


def _get_service(session_options: Optional[Dict[str, Any]] = None):
    """Crea el servicio BQL usando las opciones suministradas.

    Se retrasa la importación para que el módulo pueda inspeccionarse o
    compilarse fuera de un terminal Bloomberg sin fallar.
    """
    try:
        import bql  # type: ignore
    except ImportError as exc:  # pragma: no cover - depende del entorno Bloomberg
        raise ImportError(
            "Instale el paquete oficial `bql` dentro del Terminal de Bloomberg "
            "para ejecutar consultas BQL (ejemplo: `pip install bql`)."
        ) from exc

    opts = session_options or {}
    return bql.Service(**opts)


def fetch_dataframe(
    tickers: Iterable[str],
    fields: Dict[str, Any],
    overrides: Optional[Dict[str, Any]] = None,
    *,
    session_options: Optional[Dict[str, Any]] = None,
) -> Union["pd.DataFrame", Any]:
    """Ejecuta una consulta BQL simple y devuelve un DataFrame cuando es posible.

    Parameters
    ----------
    tickers:
        Identificadores de valores, por ejemplo ``["AAPL US Equity", "MSFT US Equity"]``.
    fields:
        Diccionario de campos BQL, por ejemplo ``{"PX_LAST": {}, "CUR_MKT_CAP": {}}``.
    overrides:
        Parámetros opcionales para la consulta, por ejemplo fechas u hojas BQL.
    session_options:
        Diccionario con opciones de conexión, por ejemplo ``{"host": "localhost", "port": 8194}``.

    Returns
    -------
    pandas.DataFrame | Any
        Un DataFrame si la librería BQL lo permite; en caso contrario se devuelve
        la respuesta cruda para que el llamador decida cómo tratarla.
    """
    service = _get_service(session_options)
    result = service.execute("getdata", list(tickers), fields, overrides or {})

    if result is None:
        return result

    try:
        first = result[0]
    except IndexError:
        return result

    to_df = getattr(first, "df", None)
    if callable(to_df):
        try:
            return to_df()
        except (TypeError, ValueError) as exc:
            logger.debug("No se pudo convertir la respuesta a DataFrame: %s", exc)
            return result

    return result


def demo():
    """Ejemplo mínimo de uso.

    Ejecutar dentro de un terminal Bloomberg con la librería `bql` instalada:

    >>> python bql_helper.py
    """

    sample_tickers = ["AAPL US Equity", "MSFT US Equity"]
    sample_fields = {"PX_LAST": {}, "CUR_MKT_CAP": {}}
    df = fetch_dataframe(sample_tickers, sample_fields)
    print(df.head() if hasattr(df, "head") else df)


if __name__ == "__main__":  # pragma: no cover - uso manual
    demo()
