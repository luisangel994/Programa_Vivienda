# 🏢 Monitor de Vivienda Protegida (VPO/VPP) y Suelo en Valencia

Programa automatizado en Python para rastrear licitaciones públicas de suelo, boletines oficiales (DOGV/PLACSP), gestoras de cooperativas y promotoras de obra nueva en Valencia y su área metropolitana, notificando novedades en tiempo real a través de un **Bot de Telegram**.

---

## 🚀 Características Principales

- **Multi-Fuente**: Rastreos en PLACSP (EVha / AUMSA), DOGV, cooperativas (SFI Consulting, CooperOpen, Prygesa, FECOVI, Libra, TPM Homes) y promotoras (Metrovacesa, Culmia, Olivares Consultores, Grupo Ática, Urbages 99, Avintia).
- **Filtro Inteligente por Presupuesto y Zona**:
  - Presupuesto máximo configurable por defecto en **300.000 €**.
  - Filtrado específico para **Valencia Capital** (Patraix, Malilla, Quatre Carreres, Benimaclet, Turianova, Nou Moles) y **Corona Metropolitana** (Torrent, Mislata, Quart de Poblet, Paterna, L'Eliana, Sagunto, etc.).
  - Coincidencia con palabras clave obligatorias (`VPO`, `VPP`, `cooperativa`, `Plan VIVE`, `derecho de superficie`, `obra nueva`) y lista negra de descartes (`alquiler únicamente`, `subasta judicial`, `suelo industrial`).
- **Control de Duplicados**: Persistencia en base de datos local SQLite (`housing.db`) con hashing de IDs para evitar notificaciones repetidas.
- **Notificaciones por Telegram**: Envío instantáneo de fichas con ubicación, precio estimado, fuente y enlace directo.

---

## 🛠️ Requisitos e Instalación

### 1. Requisitos de Software
- Python 3.8 o superior instalado.

### 2. Instalación de Dependencias
Abre una terminal/consola en esta carpeta y ejecuta:

```bash
pip install -r requirements.txt
```

---

## 📲 Configuración del Bot de Telegram (Paso a Paso)

Para recibir las alertas en tu teléfono móvil u ordenador:

1. **Crear tu Bot**:
   - Abre Telegram y busca a **`@BotFather`**.
   - Envía el comando `/newbot` y sigue las instrucciones para ponerle un nombre a tu bot (ej: `ViviendaValenciaBot`).
   - Copia el **HTTP API TOKEN** que te proporcione (ejemplo: `7123456789:ABCdefGHIjklMNO...`).

2. **Obtener tu Chat ID**:
   - En Telegram, busca a **`@userinfobot`** y envíale cualquier mensaje.
   - Te responderá con tu **`Id`** numérico (ejemplo: `12345678`).
   - Inicia conversación con tu bot recién creado enviándole el mensaje `/start`.

3. **Configurar el archivo `.env`**:
   - Abre el archivo `.env` creado en la carpeta del proyecto y rellena los datos:

```env
TELEGRAM_BOT_TOKEN=7123456789:ABCdefGHIjklMNO...
TELEGRAM_CHAT_ID=12345678
MAX_PRICE_EUR=300000
CHECK_INTERVAL_SECONDS=14400
```

---

## 💻 Modos de Ejecución

### 1. Probar y Ver Ofertas en el Navegador Web (Panel HTML Interactivo)
Puedes generar un informe visual con tarjetas interactivas, buscador en tiempo real y enlaces directos a cada oportunidad sin necesidad de configurar Telegram aún:

```bash
py main.py --html
```
Esto creará y abrirá automáticamente el archivo `report.html` en tu navegador habitual.

---

### 2. Comprobar la Configuración de Telegram
Verifica que tu bot envía mensajes correctamente:

```bash
python main.py --test-telegram
```

### 2. Ejecutar una Sola Comprobación (Modo Manual / Cron)
Busca novedades, las guarda en la base de datos y envía alertas por Telegram si encuentra oportunidades nuevas:

```bash
python main.py
```

### 3. Ejecutar en Bucle Continuo (Modo Daemon)
El programa se quedará funcionando en segundo plano y comprobará automáticamente el mercado cada 4 horas (14.400 segundos):

```bash
python main.py --loop
```

### 5. Ejecución 100% Gratuita en la Nube con tu Ordenador Apagado (GitHub Actions)

Puedes subir este proyecto a un repositorio privado de GitHub para que los servidores de GitHub ejecuten la búsqueda **todos los días automáticamente sin necesidad de encender tu PC**:

1. Crea un repositorio en [GitHub.com](https://github.com).
2. Sube esta carpeta a tu repositorio:
   ```bash
   git init
   git add .
   git commit -m "Inicializar Valencia Housing Bot"
   git remote add origin https://github.com/TU_USUARIO/Programa_Vivienda.git
   git push -u origin main
   ```
3. En tu repositorio de GitHub, ve a **Settings > Secrets and variables > Actions** y añade dos secretos:
   - `TELEGRAM_BOT_TOKEN`: Tu token del bot de Telegram.
   - `TELEGRAM_CHAT_ID`: Tu Chat ID de Telegram.
4. **¡Listo!** GitHub ejecutará automáticamente la búsqueda todos los días a las 08:00 AM, actualizará la base de datos y te enviará las novedades a tu móvil por Telegram.

---

## 🧹 Gestión Automática de Viviendas Vendidas o Retiradas

El sistema incluye una función de **Sincronización de Disponibilidad**:
- Cada vez que el script se ejecuta, compara el catálogo activo de las webs con tu base de datos local.
- Si una promotora retira una vivienda o licitación por haber sido vendida o finalizada, el programa la detecta y la **oculta del panel de ofertas activas**, garantizando que tu informe muestre únicamente inmuebles disponibles en tiempo real.


```
Programa_Vivienda/
├── config.py             # Configuración de filtros, municipios, presupuesto y keywords
├── database.py           # Persistencia y deduplicación en SQLite (housing.db)
├── filter_engine.py      # Motor de reglas de negocio para validar anuncios
├── notifier.py           # Integración con la API de Telegram Bot
├── main.py               # Script principal y CLI
├── fetchers/             # Extractores por fuentes de información
│   ├── base.py           # Clase base NoticeItem
│   ├── placsp.py         # Licitaciones públicas de suelo (EVha/AUMSA)
│   ├── dogv.py           # Diari Oficial de la Generalitat Valenciana
│   ├── cooperatives.py   # Gestoras de cooperativas (SFI, CooperOpen, Prygesa, etc.)
│   └── promotoras.py     # Promotoras y comercializadoras (Metrovacesa, Olivares, etc.)
├── requirements.txt      # Dependencias de Python
└── .env                  # Credenciales y ajustes personales
```
