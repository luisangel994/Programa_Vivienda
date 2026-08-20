import logging
import feedparser
import requests
from typing import List
from fetchers.base import BaseFetcher, NoticeItem

logger = logging.getLogger(__name__)

class PLACSPFetcher(BaseFetcher):
    """
    Fetcher para la Plataforma de Contratacion del Sector Publico (PLACSP).
    Monitoriza licitaciones de la Entidad Valenciana de Vivienda y Suelo (EVha - NIF Q4601105B),
    AUMSA y ayuntamientos de la provincia de Valencia.
    """
    name = "PLACSP (Contratación Pública VPO/Suelo)"

    FEEDS = [
        # Feeds Atom generales de la Plataforma de Contratacion del Sector Publico para la Comunitat Valenciana
        "https://contrataciondelestado.es/sindicacion/sindicacion_643/licitacionesPerfilesContratante.atom",
        # Generalitat Valenciana / EVha
        "https://contrataciondelestado.es/sindicacion/sindicacion_1044/licitacionesPerfilesContratante.atom",
    ]

    # Palabras clave especificas de busqueda en pliegos y licitaciones públicas
    KEYWORDS = ["vpo", "vpp", "evha", "aumsa", "vivienda", "parcela", "suelo", "plan vive", "permuta", "superficie"]

    def fetch(self) -> List[NoticeItem]:
        items: List[NoticeItem] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        for feed_url in self.FEEDS:
            try:
                resp = requests.get(feed_url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    parsed = feedparser.parse(resp.content)
                    for entry in parsed.entries:
                        title = getattr(entry, 'title', '')
                        summary = getattr(entry, 'summary', '')
                        link = getattr(entry, 'link', '')
                        
                        text_to_check = f"{title} {summary}".lower()
                        if any(kw in text_to_check for kw in self.KEYWORDS):
                            item = NoticeItem(
                                title=title,
                                url=link or feed_url,
                                source=self.name,
                                location="Valencia (Provincia)",
                                notice_type="Licitación Suelo / VPO Público",
                                description=summary[:300] if summary else title,
                                raw_identifier=link or title
                            )
                            items.append(item)
            except Exception as e:
                logger.warning(f"Error consultando feed PLACSP ({feed_url}): {e}")

        return items
