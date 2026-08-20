import argparse
import logging
import sys
import time
from typing import List

from config import LOOP_INTERVAL_SECONDS, MAX_PRICE_EUR
from database import init_db, generate_notice_id, is_notice_seen, save_notice, get_recent_notices
from fetchers.base import NoticeItem
from fetchers.placsp import PLACSPFetcher
from fetchers.dogv import DOGVFetcher
from fetchers.cooperatives import CooperativesFetcher
from fetchers.promotoras import PromotorasFetcher
from fetchers.gva import GVAFetcher
from filter_engine import FilterEngine
from notifier import TelegramNotifier

# Forzar codificación UTF-8 en consolas Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ValenciaViviendaMain")

def run_pipeline():
    """Ejecuta el pipeline completo: extracción -> filtrado -> deduplicación -> notificación."""
    logger.info("=== INICIANDO RUTA DE MONITORIZACIÓN DE VIVIENDA (VALENCIA VPO/VPP) ===")
    logger.info(f"Filtro Presupuesto Máximo: {MAX_PRICE_EUR:,.2f} €")

    # 1. Instanciar extractores
    fetchers = [
        PLACSPFetcher(),
        DOGVFetcher(),
        GVAFetcher(),
        CooperativesFetcher(),
        PromotorasFetcher(),
    ]

    all_raw_items: List[NoticeItem] = []

    # 2. Ingesta de datos
    for fetcher in fetchers:
        logger.info(f"Ejecutando extractor: {fetcher.name}...")
        try:
            items = fetcher.fetch()
            logger.info(f"  -> Encontrados {len(items)} registros brutos en {fetcher.name}")
            all_raw_items.extend(items)
        except Exception as e:
            logger.error(f"Error procesando {fetcher.name}: {e}")

    logger.info(f"Total registros brutos recolectados: {len(all_raw_items)}")

    # 3. Filtrado según reglas de negocio
    filter_engine = FilterEngine()
    filtered_items = filter_engine.filter_items(all_raw_items)
    logger.info(f"Total registros calificados tras filtrado de reglas: {len(filtered_items)}")

    # 4. Deduplicación y Notificación
    notifier = TelegramNotifier()
    if not notifier.is_configured():
        logger.warning("⚠️  Telegram Bot no está configurado en el archivo .env.")
        logger.warning("   Para recibir alertas en tu móvil, configura TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID.")

    new_notices_count = 0
    for item in filtered_items:
        notice_id = generate_notice_id(item.source, item.raw_identifier or item.url)
        
        if not is_notice_seen(notice_id):
            logger.info(f"🚨 ¡NUEVA OPORTUNIDAD ENCONTRADA! [{item.source}] {item.title}")
            
            # Enviar notificación si Telegram está listo
            notified_success = False
            if notifier.is_configured():
                notified_success = notifier.notify_item(item)
            
            # Guardar en SQLite
            save_notice(
                notice_id=notice_id,
                url=item.url,
                title=item.title,
                source=item.source,
                location=item.location,
                price=item.price,
                notice_type=item.notice_type,
                notified=notified_success,
                image_url=item.image_url,
                units=item.units,
                bedrooms=item.bedrooms,
                size_m2=item.size_m2,
                status=item.status
            )
            new_notices_count += 1
        else:
            logger.debug(f"Registro ya procesado previamente: {item.title}")

    # Sincronizar estado de viviendas activas vs vendidas/retiradas
    current_run_ids = {generate_notice_id(item.source, item.raw_identifier or item.url) for item in filtered_items}
    from database import sync_active_status
    sync_active_status(current_run_ids)

    logger.info(f"=== PIPELINE COMPLETADO. Nuevas novedades registradas: {new_notices_count} ===")
    return new_notices_count

def main():
    parser = argparse.ArgumentParser(description="Bot de Monitorización de Vivienda Protegida (VPO/VPP) en Valencia")
    parser.add_argument("--once", action="store_true", help="Ejecutar una sola vez y salir (por defecto)")
    parser.add_argument("--loop", action="store_true", help="Ejecutar en bucle continuo según CHECK_INTERVAL_SECONDS")
    parser.add_argument("--test-telegram", action="store_true", help="Enviar un mensaje de prueba al bot de Telegram")
    parser.add_argument("--list", action="store_true", help="Listar últimas novedades guardadas en la base de datos")
    parser.add_argument("--html", action="store_true", help="Generar un informe visual en HTML y abrirlo en el navegador web")
    parser.add_argument("--notify-summary", action="store_true", help="Enviar un resumen de ejecución a Telegram")

    args = parser.parse_args()

    # Inicializar Base de Datos SQLite
    init_db()

    if args.html:
        from export_html import generate_html_report
        # Ejecutar pipeline primero si la DB está vacía
        from database import get_recent_notices
        if not get_recent_notices(1):
            logger.info("Base de datos vacía. Ejecutando rastreo inicial...")
            run_pipeline()
        generate_html_report(auto_open=True)
        return

    if args.test_telegram:
        notifier = TelegramNotifier()
        if not notifier.is_configured():
            print("ERROR: Telegram no configurado. Revisa tu archivo .env (TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID).")
            sys.exit(1)
        print("Enviando mensaje de prueba a Telegram...")
        if notifier.send_test_notification():
            print("¡Mensaje enviado con éxito! Revisa tu Telegram.")
        else:
            print("Error al enviar el mensaje de prueba. Revisa el log.")
        return

    if args.list:
        notices = get_recent_notices(25)
        print(f"\n--- ÚLTIMAS NOVEDADES REGISTRADAS EN DB ({len(notices)}) ---")
        for n in notices:
            id_, title, source, loc, price, url, created_at, notified = n
            print(f"[{created_at}] [{source}] {title} | {loc} | {price:.2f} € | Notificado: {bool(notified)}")
            print(f"   URL: {url}\n")
        return

    if args.loop:
        logger.info(f"Modo bucle activado. Se ejecutará cada {LOOP_INTERVAL_SECONDS} segundos.")
        while True:
            try:
                run_pipeline()
            except Exception as e:
                logger.error(f"Error durante la ejecución en bucle: {e}")
            logger.info(f"Esperando {LOOP_INTERVAL_SECONDS} segundos para la próxima comprobación...")
            time.sleep(LOOP_INTERVAL_SECONDS)
    else:
        run_pipeline()

if __name__ == "__main__":
    main()
