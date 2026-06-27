# Sgtm app

## Run the app

### uv

Run as a desktop app:

```bash
uv run flet run
```

Run as a web app:

```bash
uv run flet run --web
```

For more details on running the app, refer to the [Getting Started Guide](https://flet.dev/docs/).

## Build the app

### Android

```bash
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).

### iOS

```bash
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://flet.dev/docs/publish/ios/).

### macOS

```bash
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://flet.dev/docs/publish/macos/).

### Linux

```bash
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://flet.dev/docs/publish/linux/).

### Windows

```bash
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).

### Web

```bash
flet build web -v
```

For more details on building Web app, refer to the [Web Packaging Guide](https://flet.dev/docs/publish/web/).

# Configuración del Proyecto con `uv`

## 1. Instalar `uv`
Abre tu terminal y ejecuta el comando correspondiente a tu sistema operativo para instalar el gestor de paquetes:

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
macOS / Linux:

Bash
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
2. Clonar el repositorio
Descarga el proyecto desde GitHub y entra en la carpeta:

Bash
git clone <URL_DEL_REPOSITORIO>
cd transporte_montenegro
3. Sincronizar el proyecto
Al clonar el repositorio, las dependencias ya están declaradas en el archivo pyproject.toml. Para crear el entorno virtual automáticamente e instalar todo lo necesario de una sola vez, ejecuta:

Bash
uv sync
4. Activar el entorno virtual
Una vez finalizada la sincronización, activa el entorno:

Windows: .venv\Scripts\activate

macOS / Linux: source .venv/bin/activate

5. Ejecutar la aplicación
Con el entorno activado, levanta la interfaz gráfica con el siguiente comando:

Bash
uv run flet run src/main.py
