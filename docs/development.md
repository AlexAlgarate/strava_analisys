# Desarrollo y testing

Esta guía describe el entorno local, los controles de calidad y la forma de
extender el proyecto sin romper sus límites arquitectónicos.

## Entorno local

El proyecto tiene una única versión objetivo: Python 3.13. Está declarada en
`.python-version`, `pyproject.toml`, Docker y GitHub Actions. `uv.lock` fija el
entorno reproducible y debe permanecer versionado.

```bash
uv sync --locked --all-groups
```

Los comandos habituales son:

```bash
make run           # Ejecutar la CLI
make lint          # Ruff, formato y ty
make test          # Pytest con cobertura de ramas
make architecture  # Contratos de import-linter
make check         # Todos los controles anteriores
```

`make run` usa `uv run --no-sync`: no modifica el entorno resuelto durante la
ejecución. Cuando cambien las dependencias, hay que regenerar el lockfile de
forma explícita y comprobarlo con `uv lock --check`.

## Convenciones de Python

El mínimo soportado permite usar directamente las construcciones modernas de
Python 3.13:

- genéricos nativos (`list[str]`, `dict[str, int]`);
- uniones PEP 604 (`TokenSet | None`);
- parámetros de tipo PEP 695 (`def map_concurrently[T, R](...)`);
- colecciones abstractas desde `collections.abc`;
- `Protocol` para puertos estructurales;
- `dataclass(frozen=True, slots=True)` para valores de dominio inmutables.

Las funciones y métodos deben declarar todos sus parámetros y su retorno. Los
`cast` se reservan para una frontera que ya haya validado el valor en runtime;
no deben ocultar una forma de datos desconocida. `ty` se ejecuta con todas sus
reglas en nivel de error.

## Estrategia de tests

La suite es determinista y no necesita un `client_id`, un `client_secret`, un
token real ni acceso de red:

- los puertos de Strava se sustituyen por `AsyncMock`;
- las llamadas OAuth con `requests` están parcheadas;
- navegador y entrada interactiva se simulan;
- los tests de persistencia usan `tmp_path` y claves Fernet efímeras;
- Rich escribe en un `StringIO`, sin depender de un terminal real;
- el reloj se inyecta en el servicio de tokens cuando importa la expiración.

La distribución de pruebas refleja las responsabilidades del código:

| Ruta | Qué valida |
| --- | --- |
| `tests/domain/` | invariantes, parsing y cálculos puros |
| `tests/core/` | orquestación, concurrencia y fallos parciales |
| `tests/infrastructure/` | persistencia y comportamiento de adaptadores |
| `tests/presentation/` | prompts, tablas, progreso y errores |
| `tests/test_*.py` | fachadas, composición y compatibilidad pública |

La configuración exige al menos un 95 % de cobertura combinada de líneas y
ramas sobre `src` y `main.py`. La cobertura alta no sustituye las aserciones de
comportamiento: cada cambio debe incluir casos nominales, bordes y errores
relevantes.

Para ejecutar una parte concreta durante el desarrollo:

```bash
uv run --no-sync pytest tests/domain/test_activity_stream.py -q
uv run --no-sync pytest tests/core/streams/test_fetcher.py -q
```

Antes de publicar una rama se ejecuta siempre `make check` completo.

## Cómo añadir un caso de uso

1. Modela en `src/domain` los datos y sus invariantes si el concepto aún no
   existe. Convierte la respuesta externa en la frontera con un constructor
   como `from_mapping`.
2. Declara en `src/core/ports` cualquier capacidad externa que necesite el
   caso de uso. El puerto debe expresar la necesidad del consumidor, no copiar
   la API completa del proveedor.
3. Implementa la orquestación en `src/core`, con dependencias recibidas por el
   constructor y efectos laterales explícitos.
4. Añade el adaptador concreto en `src/infrastructure`.
5. Si se expone en la terminal, amplía el contrato de presentación, añade una
   `MenuOption` y conecta la acción en `MenuHandler`.
6. Inyecta las implementaciones únicamente en `main.py`.
7. Añade tests por capa y, si aparece una nueva relación entre paquetes,
   actualiza o refuerza `.importlinter`.

La capa de presentación no debe importar ni instanciar clientes HTTP,
repositorios o exportadores concretos.

## Cómo añadir un exportador

Un nuevo formato solo tiene que satisfacer `StreamExporter`:

```python
from collections.abc import Sequence
from pathlib import Path

from src.domain.activity_stream import ActivityStream


class ExampleStreamExporter:
    def export(self, streams: Sequence[ActivityStream], path: Path, /) -> None:
        ...
```

No necesita heredar de una clase base. Se registra en el mapa `exporters` al
construir `StravaService`; `DataExporter` selecciona la implementación por
nombre y conserva el caso de uso cerrado a cambios en formatos existentes.

## Docker y CI

La imagen se valida localmente con:

```bash
docker build -t strava-analysis .
docker run --rm --env-file .env -it strava-analysis
```

GitHub Actions ejecuta en paralelo tests, Ruff, formato, `ty` y los contratos
de arquitectura. El job de Docker solo comienza si todos han terminado bien.
Las pull requests construyen la imagen, pero GHCR se actualiza únicamente con
un `push` a `main`.

## Flujo de contribución

- Parte siempre de `develop` actualizado.
- Usa una rama por responsabilidad (`refactor/...`, `feat/...`, `docs/...`).
- Crea commits pequeños y atómicos con mensajes que expliquen su intención.
- Abre la PR contra `develop` y espera todos los checks.
- Integra mediante rebase para mantener una historia lineal.
- Promueve `develop` a `main` solo cuando el conjunto esté validado.

No mezcles cambios funcionales, arquitectura, dependencias y documentación en
un único commit o pull request si pueden revisarse de forma independiente.
