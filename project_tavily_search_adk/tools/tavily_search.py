# tools/tavily_search.py

import os

from tavily import TavilyClient

# --- Configuración de conexión a Tavily ---
# La API key NO se escribe aquí: se lee del archivo .env que el ADK carga
# automáticamente desde la carpeta del agente (TAVILY_API_KEY=tvly-...).
# Consíguela gratis en https://app.tavily.com
_client = None


def _get_tavily_client() -> TavilyClient:
    """Crea el cliente de Tavily una sola vez y lo reutiliza (lazy singleton)."""
    global _client
    if _client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise RuntimeError(
                "No se encontró la variable TAVILY_API_KEY. "
                "Créala en el archivo .env de la carpeta del agente."
            )
        _client = TavilyClient(api_key=api_key)
    return _client


# Al igual que run_sql_query, esta es una función de Python normal.
# El ADK la convierte en una herramienta automáticamente leyendo su firma y su docstring.
def tavily_search(query: str, topic: str, max_results: int) -> dict:
    """
    Busca información actualizada en internet usando el motor de búsqueda Tavily,
    optimizado para agentes de IA. Devuelve una respuesta sintetizada y la lista de
    fuentes con su URL y un extracto del contenido.

    Args:
        query (str): La consulta de búsqueda en lenguaje natural. Sé específico
            (ej. "resultados del censo de Perú 2025" en lugar de "censo").
        topic (str): El tipo de búsqueda. Usa "news" para noticias y eventos
            recientes, o "general" para cualquier otro tema.
        max_results (int): Cantidad de fuentes a devolver, entre 1 y 10.
            Usa 5 como valor razonable por defecto.

    Returns:
        dict: Un diccionario con la clave "status" ("success" o "error").
            Si es "success" incluye "answer" (resumen generado por Tavily) y
            "results" (lista de fuentes con title, url, content, score).
            Si es "error" incluye "error_message" con el detalle del fallo.
    """
    # Normalizamos los argumentos por si el modelo envía valores fuera de rango.
    topic = topic.lower().strip()
    if topic not in ("general", "news"):
        topic = "general"
    max_results = max(1, min(int(max_results), 10))

    try:
        client = _get_tavily_client()
        response = client.search(
            query=query,
            topic=topic,
            max_results=max_results,
            search_depth="advanced",  # Más preciso que "basic"; consume 2 créditos.
            include_answer=True,      # Tavily devuelve un resumen ya sintetizado.
        )

        results = [
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content"),
                "score": item.get("score"),
                "published_date": item.get("published_date"),
            }
            for item in response.get("results", [])
        ]

        if not results:
            return {
                "status": "success",
                "query": query,
                "answer": None,
                "results": [],
                "message": "La búsqueda se ejecutó correctamente, pero no devolvió resultados.",
            }

        return {
            "status": "success",
            "query": query,
            "answer": response.get("answer"),
            "results": results,
        }

    except Exception as e:
        # Devolvemos el error como dato para que el agente pueda reformular la búsqueda.
        return {
            "status": "error",
            "query": query,
            "error_message": f"Error al consultar Tavily: {e}",
        }
