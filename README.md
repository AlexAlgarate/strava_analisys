# Strava Analysis

CLI en Python 3.13 para consultar actividades de Strava, analizar y exportar
sus streams, guardar zonas cardiacas en JSON y generar resúmenes semanales.

Las respuestas externas se validan al entrar en la aplicación y se convierten
en modelos de dominio inmutables. Las consultas por lotes limitan su
concurrencia y conservan los errores parciales para que ninguna actividad falle
silenciosamente.

## Requisitos

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- Una [suscripción activa de Strava](https://developers.strava.com/docs/getting-started/)
  para registrar la aplicación API

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
```

Los tokens OAuth no requieren Supabase ni otra base de datos. Se guardan
automáticamente en la variable `STRAVA_OAUTH_TOKEN` del mismo `.env`. No hay
que crearla ni editarla manualmente. El archivo está excluido por `.gitignore`
y la aplicación comprueba que sea un archivo regular, rechaza enlaces
simbólicos y restringe sus permisos a `0600` antes de leerlo.

La autorización solicita únicamente `read,activity:read_all`. Cada intento usa
un `state` aleatorio que debe volver intacto en la URL de callback, cuya ruta y
origen también se validan antes de aceptar el código.

Los logs se escriben fuera del repositorio, en
`$XDG_STATE_HOME/strava-analysis/application.log` o, si esa variable no está
definida, en `~/.local/state/strava-analysis/application.log`. El directorio y
el archivo usan permisos `0700` y `0600`. Las exportaciones CSV y JSON también
son privadas y sustituyen el destino atómicamente solo cuando la escritura ha
terminado correctamente.

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

Este comando ejecuta Ruff, el formateador, `ty`, pytest con cobertura de ramas,
los contratos de arquitectura y `uv audit --locked`. La cobertura mínima
exigida es del 95%.

Los comandos individuales son `make lint`, `make test`, `make architecture` y
`make audit`. El workflow de GitHub Actions los ejecuta en paralelo y construye
la imagen Docker cuando todos terminan correctamente. La imagen sólo se publica
en GHCR desde un `push` a `main`.

## Documentación

- [Arquitectura y flujos](docs/architecture.md)
- [Desarrollo, testing y extensibilidad](docs/development.md)
- [Cómo añadir una opción a la terminal](docs/adding-cli-option.md)
- [Credenciales y almacenamiento local de tokens](docs/security.md)

Consulta el [índice de documentación](docs/README.md) para una vista general.

## Arquitectura

```text
src/
├── domain/          # Entidades y reglas de negocio puras
├── application/     # Casos de uso, puertos y resultados
├── infrastructure/  # HTTP, OAuth, persistencia local y exportadores
├── presentation/    # Menú y salida de consola
└── composition.py   # Construcción e inyección de implementaciones
```

Las dependencias entre capas están verificadas mediante import-linter.
Los streams se exportan con la biblioteca estándar de Python; no se necesita
`pandas` para procesarlos ni para generar CSV.

## Docker

Usa un archivo separado como `.env.docker`, con permisos `0600`, que contenga
solo `STRAVA_CLIENT_ID` y `STRAVA_SECRET_KEY`. No reutilices el `.env` local:
después del primer acceso también contiene el token OAuth y Docker expondría
todo su contenido como variables del contenedor.

```bash
docker build -t strava-analysis .
docker volume create strava-analysis-data
docker run --rm --env-file .env.docker \
  --mount type=volume,src=strava-analysis-data,dst=/data \
  -it strava-analysis
```

La imagen se ejecuta sin privilegios con UID/GID `10001`; el código de `/app`
queda de solo lectura para ese usuario. El archivo de entorno separado inyecta
solo las credenciales iniciales. El volumen conserva el token renovado en
`/data/.env`, los logs bajo `/data/state` y las exportaciones creadas desde el
directorio de trabajo `/data`. El volumen contiene secretos sin cifrar y debe
protegerse como el `.env` del host.

## Licencia

MIT. Consulta [LICENSE](LICENSE).
