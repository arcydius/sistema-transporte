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


# 🚀 Sistema de Gestión de Transporte Pesado - Montenegro C.A.

¡Bienvenido al equipo de desarrollo! Este proyecto transforma el antiguo prototipo web en una solución de escritorio profesional, robusta y segura. Utilizaremos **Flet** para construir una interfaz reactiva en Python y **PostgreSQL** para la persistencia estructural de los datos.

Para garantizar un entorno de desarrollo ultrarrápido y sin conflictos, estamos utilizando **`uv`** como nuestro gestor de paquetes y entornos virtuales.

Sigue estos pasos para levantar el proyecto en tu máquina local:

## 1. Instalar `uv`
Si aún no tienes `uv` instalado en tu sistema, abre tu terminal y ejecuta el comando correspondiente a tu sistema operativo:

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
macOS / Linux:

Bash
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
2. Clonar el repositorio y acceder a la carpeta
Bash
git clone <URL_DEL_REPOSITORIO>
cd transporte_montenegro
3. Crear el entorno virtual e instalar dependencias
La magia de uv es que crea el entorno y resuelve las dependencias en milisegundos. Ejecuta:

Bash
# Crea el entorno virtual en la carpeta .venv
uv venv

# Activa el entorno virtual
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate

# Instala todas las dependencias del proyecto al instante
uv pip install -r requirements.txt
(Nota: El archivo requirements.txt ya incluye flet, sqlalchemy y los drivers para PostgreSQL).

4. Configurar variables de entorno (Backend)
Para la lógica de datos y conexión a la base de datos PostgreSQL, asegúrate de crear un archivo llamado .env en la raíz del proyecto. Este archivo está ignorado en Git por seguridad.

Agrega tus credenciales locales de este modo:

Fragmento de código
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
DB_NAME=transporte_montenegro
5. Ejecutar la aplicación
Para iniciar la interfaz gráfica de Flet de forma nativa como aplicación de escritorio, ejecuta:

Bash
uv run flet run src/main.py
Tip: Flet tiene "Hot Reload" por defecto al usar este comando. Si guardas un cambio en el código de la interfaz, la pantalla se actualizará automáticamente sin necesidad de reiniciar la app.

🏗️ Arquitectura y División de Tareas
Para evitar conflictos al hacer Merge en Git y trabajar en paralelo sin bloqueos, hemos dividido el proyecto mediante una estricta separación de responsabilidades:

Frontend (Vistas e Interfaz Flet)
Carpetas: src/views/ y src/components/.

Responsabilidad: Exclusivas para el desarrollo de la interfaz gráfica y la experiencia de usuario.

Regla: Aquí no debe existir lógica de negocio, cálculos matemáticos complejos, ni consultas directas a la base de datos. Solo se consumen los datos provenientes de los controladores.

Backend (PostgreSQL y Lógica de Negocio)
Carpetas: src/database/ (conexión), src/models/ (esquemas de tablas) y src/controllers/ (lógica y procesamiento).

Responsabilidad: Conexión a la base de datos, ejecución de CRUDs y cálculos (ej. deducciones de nómina, cálculo de utilidad neta).

Regla: Los controladores creados en src/controllers/ actúan como un puente. Deben recibir parámetros simples, ejecutar la lógica interna y retornar estructuras de datos nativas (diccionarios, listas, booleanos) que el Frontend consumirá para "pintar" las tablas e indicadores.
