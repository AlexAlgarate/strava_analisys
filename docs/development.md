# Desarrollo y testing

Esta guía describe el entorno local, los controles de calidad y cómo extender
el proyecto sin romper sus límites.

## Entorno local

El proyecto tiene una única versión objetivo: Python 3.13. Está declarada en
`.python-version`, `pyproject.toml`, Docker y GitHub Actions. `uv.lock` fija
el entorno reproducible.

```bash
uv sync --locked --all-groups
```

Comandos habituales:

```bash
make run           # Ejecutar la CLI
make lint          # Ruff, formato y ty
make test          # Pytest con cobertura de ramas
make architecture  # Contratos de import-linter
make check         # Todos los controles anteriores
```

`make run` usa `uv run --no-sync`, por lo que no altera el entorno resuelto.
Si cambian las dependencias, regenera el lockfile explícitamente y compruébalo
con `uv lock --check`.

## Convenciones de Python

Python 3.13 permite usar genéricos nativos, uniones PEP 604, parámetros de tipo
PEP 695, colecciones abstractas desde `collections.abc` y `Protocol` para
puertos estructurales. Los objetos de dominio son inmutables cuando no
necesitan estado mutable.

Todas las funciones y métodos declaran parámetros y retorno. Los `cast` se
reservan para fronteras que ya han validado el valor en runtime; no deben
ocultar datos ambiguos. `ty` se ejecuta con todas sus reglas como errores.

## Estrategia de tests

La suite no necesita credenciales reales ni red:

- los gateways se sustituyen por `AsyncMock`;
- las llamadas OAuth con `requests` están parcheadas;
- navegador y entrada interactiva se simulan;
- persistencia y exportadores usan `tmp_path`;
- Rich escribe en un `StringIO`;
- reloj y concurrencia se inyectan cuando son relevantes.

La distribución refleja las capas:

| Ruta | Qué valida |
| --- | --- |
| `tests/domain/` | invariantes y cálculos puros |
| `tests/application/` | orquestación, puertos, concurrencia y fallos parciales |
| `tests/infrastructure/` | mapeo, persistencia y adaptadores |
| `tests/presentation/` | prompts, tablas, progreso y errores |
| `tests/test_composition.py` | ensamblado de implementaciones |
| `tests/test_main.py` | bootstrap y ciclo de vida |

La configuración exige al menos un 95 % de cobertura combinada de líneas y
ramas sobre `src` y `main.py`. Cada cambio debe probar caminos nominales,
límites y errores relevantes.

```bash
uv run --no-sync pytest tests/domain/test_activity_stream.py -q
uv run --no-sync pytest tests/application/use_cases/test_streams.py -q
```

Antes de publicar una rama se ejecuta `make check`.

## Cómo añadir un caso de uso

La guía [Añadir una opción a la terminal](adding-cli-option.md) desarrolla el
proceso con ejemplos completos.

1. Modela datos e invariantes nuevos en `src/domain`.
2. Declara la necesidad externa en `src/application/ports`.
3. Implementa la orquestación en `src/application/use_cases`, recibiendo sus
   puertos por constructor.
4. Traduce payloads y excepciones en un adaptador de `src/infrastructure`.
5. Expón un puerto de entrada pequeño cuando una frontera lo necesite y conecta
   el servicio en `ApplicationServices` y `build_application_services`.
6. Si lo usa la CLI, añade el `MenuOption` y registra un
   `MenuCommand[T]` en `build_menu_commands`, eligiendo allí su acción y
   presenter tipado. Amplía prompts o presenters solo si el contrato es nuevo.
7. Deja `MenuDependencies` estable: no contiene casos de uso, sino el registro
   de comandos y los servicios transversales de terminal.
8. Mantén en `main.py` únicamente bootstrap, ciclo de vida y adaptadores de
   presentación.
9. Añade tests por capa y refuerza `.importlinter` si aparece una relación
   nueva.

Presentación nunca importa ni instancia clientes HTTP, stores o exportadores
concretos. Aplicación tampoco importa infraestructura o presentación. Los tests
de composición de comandos verifican opción, argumentos y presenter; los de
`MenuHandler` verifican resolución, progreso y contención de errores sin
duplicar la lógica de cada caso de uso.

## Cómo añadir un exportador

Un formato nuevo solo tiene que satisfacer `StreamExporter`:

```python
from collections.abc import Sequence
from pathlib import Path

from src.domain.activity_stream import ActivityStream


class ExampleStreamExporter:
    def export(self, streams: Sequence[ActivityStream], path: Path, /) -> None: ...
```

Regístralo por nombre en el mapa que `build_application_services` entrega a
`StreamExportService`. El caso de uso selecciona el adaptador sin conocer su
implementación. Prueba por separado la escritura del adaptador y la delegación
del caso de uso.

## Docker y CI

```bash
docker build -t strava-analysis .
docker run --rm --env-file .env -it strava-analysis
```

GitHub Actions ejecuta tests, Ruff, formato, `ty` y los contratos de
arquitectura. La imagen se publica en GHCR únicamente desde un `push` a
`main`.

## Flujo de contribución

- Parte de `develop` actualizado.
- Usa una rama por responsabilidad.
- Crea commits pequeños y atómicos.
- Abre la PR contra `develop` y espera todos los checks.
- Promueve `develop` a `main` solo después de validarlo.

No mezcles cambios funcionales, arquitectura, dependencias y documentación si
pueden revisarse de forma independiente.
