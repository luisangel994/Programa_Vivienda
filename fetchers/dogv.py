import logging
import feedparser
import requests
from typing import List
from fetchers.base import BaseFetcher, NoticeItem

logger = logging.getLogger(__name__)

class DOGVFetcher(BaseFetcher):
    """
    Fetcher para el Diari Oficial de la Generalitat Valenciana (DOGV).
    Monitoriza la seccion de Urbanismo, Vivienda, PAIs y calificaciones VPO.
    """
    name = "DOGV (Diari Oficial GVA)"

    # RSS del DOGV para boletines y publicaciones oficial de la Comunitat Valenciana
    FEEDS = [
        "https://dogv.gva.es/es/rss",
        "https://dogv.gva.es/es/rss/seccion?id=3", # Urbanismo y Vivienda
    ]

    KEYWORDS = ["vpo", "vpp", "vivienda", "urbanismo", "pai", "reparcelacion", "licencia", "plan vive"]

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

                        content = f"{title} {summary}".lower()
                        if any(kw in content for kw in self.KEYWORDS):
                            item = NoticeItem(
                                title=title,
                                url=link or feed_url,
                                source=self.name,
                                location="Comunitat Valenciana",
                                notice_type="Boletín Oficial (DOGV)",
                                description=summary[:300] if summary else title,
                                raw_identifier=link or title
                            )
                            items.append(item)
            except Exception as e:
                logger.warning(f"Error consultando DOGV ({feed_url}): {e}")

        return items
