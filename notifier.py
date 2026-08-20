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
        """Envia un mensaje de texto formateado en HTML a Telegram."""
        if not self.is_configured():
            logger.warning("Telegram Bot no configurado. Omitiendo envío (TOKEN o CHAT_ID faltantes en .env).")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        try:
            resp = requests.post(self.api_url, json=payload, timeout=10)
            if resp.status_code == 200 and resp.json().get("ok"):
                logger.info("Mensaje enviado correctamente a Telegram.")
                return True
            else:
                logger.error(f"Error al enviar mensaje a Telegram: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            logger.error(f"Excepción al conectar con la API de Telegram: {e}")
            return False

    def notify_item(self, item: NoticeItem) -> bool:
        """Formatea un NoticeItem y lo envía a Telegram."""
        price_str = f"{item.price:,.2f} €" if item.price > 0 else "Por consultar / Pendiente pliego"

        msg = (
            f"🚨 <b>NUEVA PROMOCIÓN / SUELO DETECTADO</b>\n\n"
            f"📍 <b>Ubicación:</b> {item.location}\n"
            f"🏢 <b>Promotora / Fuente:</b> {item.source}\n"
            f"🏷️ <b>Tipo:</b> {item.notice_type}\n"
            f"📌 <b>Título:</b> {item.title}\n"
            f"💰 <b>Precio Máx / Estimado:</b> {price_str}\n"
            f"🔗 <b>Enlace directo:</b> <a href=\"{item.url}\">Ver Ficha / Pliego</a>\n"
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
