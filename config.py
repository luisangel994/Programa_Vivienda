import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# Configuración de Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Configuración de Base de Datos
DB_PATH = BASE_DIR / "housing.db"

# Parámetros de Filtrado de Vivienda
MAX_PRICE_EUR = float(os.getenv("MAX_PRICE_EUR", 300000))

# Lista blanca de municipios y zonas de interés (provincia de Valencia)
TARGET_LOCATIONS = [
    # Valencia Capital y distritos/barrios de expansión
    "valencia", "valència", "malilla", "patraix", "quatre carreres", "benimaclet", 
    "turianova", "nou moles", "moreras", "las moreras", "safranar",
    
    # L'Horta Sud
    "torrent", "mislata", "quart de poblet", "alaquàs", "alaquas", "aldaia", 
    "xirivella", "alfafar", "catarroja", "massanassa", "paiporta", "picanya", 
    "sedaví", "sedavi", "benetússer", "benetusser", "silla",
    
    # L'Horta Nord y Camp de Túria
    "paterna", "burjassot", "godella", "l'eliana", "eliana", "bétera", "betera", 
    "sagunto", "sagunt", "puerto de sagunto", "moncada", "rocafort", "puçol", 
    "pucol", "la pobla de vallbona", "riba-roja", "ribarroja", "alboraya"
]

# Palabras clave obligatorias (Match positivo: al menos una debe estar presente)
POSITIVE_KEYWORDS = [
    "vpo", "vpp", "vpc", "vivienda de protección", "vivienda protegida",
    "proteccion oficial", "protección oficial", "régimen general", "regimen general",
    "régimen concertado", "regimen concertado", "cooperativa de viviendas", "cooperativa",
    "adjudicación de socios", "adjudicacion de socios", "plan vive", "plan viu",
    "derecho de superficie", "enajenación de parcela", "enajenacion de parcela",
    "licitación de suelo", "licitacion de suelo", "concurso de suelo", "cesión de parcela",
    "obra nueva", "próxima promoción", "proxima promocion", "prelanzamiento", "preventa",
    "residencial"
]

# Palabras clave excluyentes (Blacklist: descarta noticias institucionales o no relevantes)
NEGATIVE_KEYWORDS = [
    "alquiler únicamente", "alquiler unico", "alquiler únicamente",
    "subasta judicial", "suelo industrial", "terreno industrial", 
    "local comercial", "nave industrial", "oficina",
    "unifamiliar aislado", "chalet independiente",
    "plaza de garaje únicamente", "trastero únicamente",
    
    # Filtros de exclusión de noticias institucionales / políticas no inmobiliarias
    "protección de datos", "proteccion de datos", "normativa jurídica",
    "guía vecindad", "guia vecindad", "servicios a cooperativas",
    "visita las obras", "visita la evha", "demolición", "demolicion",
    "violencia de género", "comunidad energética", "compromiso de poner",
    "nombra presidente", "convivencia en", "ratifica la adquisición",
    "aplaza el pago", "nuevo espacio de atención"
]

# Intervalo por defecto para modo bucle (en segundos, ej: 4 horas = 14400s)
LOOP_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", 14400))
