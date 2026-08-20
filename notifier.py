import logging
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from fetchers.base import NoticeItem

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """
    Cliente para enviar notificaciones formateadas al Bot de Telegram.
    """

    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage" if self.token else ""

    def is_configured(self) -> bool:
        return bool(self.token and self.chat_id)

    def send_message(self, text: str) -> bool:
        """Envia un mensaje de texto formateado en HTML a uno o varios Chat IDs de Telegram."""
        if not self.is_configured():
            logger.warning("Telegram Bot no configurado. Omitiendo envío (TOKEN o CHAT_ID faltantes en .env).")
            return False

        # Separar por comas para soportar varios destinatarios (ej: "190425566,987654321")
        target_chat_ids = [cid.strip() for cid in str(self.chat_id).split(",") if cid.strip()]
        overall_success = True

        for cid in target_chat_ids:
            payload = {
                "chat_id": cid,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }

            try:
                resp = requests.post(self.api_url, json=payload, timeout=10)
                if resp.status_code == 200 and resp.json().get("ok"):
                    logger.info(f"Mensaje enviado correctamente a Telegram (Chat ID: {cid}).")
                else:
                    logger.error(f"Error al enviar mensaje a Telegram ({cid}): {resp.status_code} - {resp.text}")
                    overall_success = False
            except Exception as e:
                logger.error(f"Excepción al conectar con la API de Telegram ({cid}): {e}")
                overall_success = False

        return overall_success

    def notify_item(self, item: NoticeItem) -> bool:
        """Formatea un NoticeItem y lo envía a Telegram."""
        price_str = f"{item.price:,.2f} €" if item.price > 0 else "Por consultar / Pendiente pliego"

        # Enlace público al catálogo HTML interactivo
        dashboard_url = "https://raw.githack.com/luisangel994/Programa_Vivienda/main/report.html"

        msg = (
            f"🚨 <b>¡NUEVA OPORTUNIDAD EN VALENCIA!</b>\n\n"
            f"🏠 <b>{item.title}</b>\n"
            f"🏷️ <b>Estado:</b> {item.notice_type}\n"
            f"📍 <b>Ubicación:</b> {item.location}\n"
            f"💰 <b>Precio:</b> {price_str}\n"
            f"🏢 <b>Fuente:</b> {item.source}\n\n"
            f"🔗 <a href='{item.url}'>Ver Ficha Original</a>\n"
            f"🌐 <b><a href='{dashboard_url}'>Ver Catálogo Completo (Web HTML)</a></b>"
        )
        return self.send_message(msg)

    def send_test_notification(self) -> bool:
        """Envía un mensaje de prueba para validar que el token y el chat_id son correctos."""
        msg = (
            "✅ <b>¡Bot de Vivienda Valencia Configurado Correctamente!</b>\n\n"
            "El sistema de alertas de VPO/VPP, cooperativas y suelo licitado está listo "
            "y comenzará a notificar las oportunidades en la provincia de Valencia."
        )
        return self.send_message(msg)
