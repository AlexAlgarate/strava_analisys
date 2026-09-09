# Strava Analysis

CLI en Python 3.13 para consultar actividades de Strava, analizar sus streams
y generar resúmenes semanales.

## Requisitos

- Python 3.13
- [uv](https://docs.astral.sh/uv/)

## Instalación

```bash
git clone https://github.com/AlexAlgarate/strava_analisys.git
cd strava_analisys
uv sync --locked --all-groups
```

Crea un archivo `.env` en la raíz:

```dotenv
STRAVA_CLIENT_ID=<client-id>
STRAVA_SECRET_KEY=<client-secret>
# Opcional: si se omite, se genera una clave local privada.
FERNET_KEY=<fernet-key>
```

Los tokens OAuth no requieren Supabase ni otra base de datos. Se guardan
cifrados fuera del repositorio, por defecto en
`~/.local/share/strava-analysis/tokens.enc`. La clave generada localmente se
guarda con permisos exclusivos del usuario en
`~/.config/strava-analysis/fernet.key`.

## Uso

```bash
make run
```

También puede ejecutarse directamente:

```bash
uv run --no-sync python main.py
```

## Calidad y tests

```bash
make check
```

Este comando ejecuta Ruff, el formateador, `ty`, pytest con cobertura de ramas
y los contratos de arquitectura. La cobertura mínima exigida es del 95%.

Los comandos individuales son `make lint`, `make test` y `make architecture`.
El workflow de GitHub Actions los ejecuta en paralelo y construye la imagen
Docker cuando todos terminan correctamente. La imagen sólo se publica en GHCR
desde un `push` a `main`.

## Arquitectura

```text
src/
├── domain/          # Entidades y reglas de negocio puras
├── core/            # Casos de uso y puertos (Protocol)
├── infrastructure/  # HTTP, OAuth, persistencia local y exportadores
├── presentation/    # Menú y salida de consola
├── access_token.py  # Composición del flujo OAuth
└── utils/           # Constantes, errores y utilidades compartidas
```

Las dependencias entre capas están verificadas mediante import-linter.

## Docker

```bash
docker build -t strava-analysis .
docker run --rm --env-file .env -it strava-analysis
```

Si se quiere conservar el token entre ejecuciones del contenedor, monta un
volumen para los directorios XDG de datos y configuración.

## Licencia

MIT. Consulta [LICENSE](LICENSE).
