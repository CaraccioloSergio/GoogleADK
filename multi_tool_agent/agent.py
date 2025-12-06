import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

import http.client
import json
import urllib.parse

def labbi_search_catalog(
    order_by: str = "ORDENAR POR AZ",
    direction: str = "ASC",
    info_types: str = "products",
    query: str = "",
    # paginación
    page: int | None = None,
    from_index: int | None = None,
    size: int = 30,
    auth_token: str = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZWNoQHlvcC1kZXYuY29tIiwiaWF0IjoxNzY0OTU5MTU5LCJleHAiOjE3ODA1MTExNTl9.kk8mIVaRY6RwZDVN8ikN3w3_0bKGimU0MkfyAbLiRsU"
) -> dict:
    """
    Consulta el catálogo de Labbi (UAT) usando /api/v2/search.

    Paginación:
    - Si se pasa 'from_index', se usa directamente (clamp >= 0).
    - Si se pasa 'page', se convierte a 'from = page * size' (clamp >= 0).
    - Si no se pasa nada, se usa from=0.
    """

    try:
        if not auth_token:
            return {
                "status": "error",
                "error_message": "Missing auth_token for Labbi API."
            }

        # --- Normalizar paginación ---
        if from_index is not None:
            # clamp
            if from_index < 0:
                from_index = 0
        else:
            # calcular a partir de page
            if page is None:
                page = 0
            if page < 0:
                page = 0
            from_index = page * size

        conn = http.client.HTTPSConnection("uat.api.labbi.com.ar", timeout=10)

        params = {
            "orderBy": order_by,
            "direction": direction,
            "infoTypes": info_types,
            "from": from_index,
            "size": size,
        }

        if query:
            params["q"] = query

        qs = urllib.parse.urlencode(params, safe=":/?& ")

        endpoint = f"/api/v2/search?{qs}"

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/json",
        }

        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        status_code = res.status
        raw = res.read()

        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            data = raw.decode("utf-8")

        if 200 <= status_code < 300:
            return {
                "status": "success",
                "status_code": status_code,
                "endpoint": endpoint,
                "from": from_index,
                "size": size,
                # adaptá estos nombres a lo que realmente devuelva la API
                "results_count": data.get("totalElements"),
                "items": data.get("content"),
                "raw": data,
            }
        else:
            return {
                "status": "error",
                "status_code": status_code,
                "endpoint": endpoint,
                "error_message": "Labbi API returned an error.",
                "response": data,
            }

    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
        }

def test_api_labbi(cuit: str) -> dict:
    """
    Testea la API de Labbi (dev) para obtener drugstores por CUIT.
    ADK requiere que las herramientas devuelvan un dict estructurado.
    """

    try:
        conn = http.client.HTTPSConnection("dev.api.labbi.com.ar", timeout=10)

        # Armamos la query
        endpoint = f"/api/pharmacy/drugstores?cuit={cuit}"

        headers = {
            "Accept": "application/json"
        }

        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()

        status_code = res.status
        raw = res.read()

        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            data = raw.decode("utf-8")

        if status_code >= 200 and status_code < 300:
            return {
                "status": "success",
                "status_code": status_code,
                "data": data
            }
        else:
            return {
                "status": "error",
                "status_code": status_code,
                "error_message": f"API returned {status_code}",
                "response": data
            }

    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }


root_agent = Agent(
    name="labbi_tester",
    model="gemini-2.0-flash",
    description="Agente para consultar el catálogo de Labbi vía API.",
    instruction=(
        "Sos un agente que consulta el catálogo de Labbi.\n"
        "- Usá 'labbi_search_catalog' para buscar productos, laboratorios o droguerías.\n"
        "- Nunca uses páginas negativas ni índices negativos.\n"
        "- Si el usuario pide 'página anterior' desde el inicio, mantenete en la primera página.\n"
    ),
    tools=[labbi_search_catalog],
)