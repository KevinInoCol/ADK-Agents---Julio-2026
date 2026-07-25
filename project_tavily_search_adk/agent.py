# agent.py

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

# De la librería del ADK, importamos la clase "Agent", el chasis del agente.
from google.adk.agents import Agent

# El "." al principio significa importación "relativa" desde la carpeta del proyecto.
from .tools.tavily_search import tavily_search

# --- Carga del system prompt ---
# El prompt NO se hardcodea aquí: vive en prompt/prompt.yaml, estructurado con tags.
PROMPT_PATH = Path(__file__).parent / "prompt" / "prompt.yaml"
SYSTEM_PROMPT = yaml.safe_load(PROMPT_PATH.read_text(encoding="utf-8"))["system_prompt"]

# Zona horaria usada para la fecha y hora que se inyecta en cada turno.
TIMEZONE = ZoneInfo("America/Lima")


def build_instruction(context) -> str:
    """
    El ADK acepta una función como 'instruction' y la ejecuta en cada turno.
    Así la fecha y hora nunca queda congelada dentro del prompt.
    """
    ahora = datetime.now(TIMEZONE)
    fecha_hora = ahora.strftime("%A %d de %B de %Y, %H:%M") + f" ({TIMEZONE.key})"
    return f"{SYSTEM_PROMPT}\n\n<fecha_hora_actual>\n{fecha_hora}\n</fecha_hora_actual>\n"


root_agent = Agent(
    name="TavilyAgent",
    model="gemini-2.5-flash",  # Simplemente el nombre del modelo.
    description="Agente investigador que busca información actualizada en internet con Tavily",
    tools=[
        tavily_search,
    ],
    instruction=build_instruction,
)
