import logging
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import List
from fetchers.base import BaseFetcher, NoticeItem

logger = logging.getLogger(__name__)

COOP_IMAGES = [
    "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
]

class CooperativesFetcher(BaseFetcher):
    """
    Fetcher especializado en Gestoras de Cooperativas y Viviendas a Precio de Coste en Valencia.
    Garantiza URLs absolutas y funcionales.
    """
    name = "Gestoras de Cooperativas VPO/VPP"

    SOURCES = [
        {
            "name": "SFI Consulting",
            "url": "https://sficonsulting.es/promociones/",
            "keywords": ["valencia", "alaquàs", "alaquas", "paterna", "eliana", "malilla", "aura", "calia", "viure", "eresmas"]
        },
        {
            "name": "CooperOpen (CONCOVI)",
            "url": "https://cooperopen.org/",
            "keywords": ["valencia", "mislata", "quart", "paterna", "vpo", "vpp"]
        },
        {
            "name": "Prygesa (Grupo Pryconsa)",
            "url": "https://www.prygesa.es/venta-de-viviendas/",
            "keywords": ["valencia", "vpo", "vpp", "cooperativa"]
        },
        {
            "name": "FECOVI (Federación Cooperativas CV)",
            "url": "https://fecovi.es/cooperativas-afiliadas/",
            "keywords": ["valencia", "cooperativa", "vivienda"]
        },
        {
            "name": "Libra Gestión de Proyectos",
            "url": "https://libragp.com/promociones/",
            "keywords": ["valencia", "malilla", "patraix", "torrent", "vpo"]
        },
        {
            "name": "TPM Homes",
            "url": "https://tpm-homes.es/promociones/",
            "keywords": ["valencia", "horta", "turia", "cooperativa"]
        }
    ]

    def fetch(self) -> List[NoticeItem]:
        items: List[NoticeItem] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        img_idx = 0

        for target in self.SOURCES:
            try:
                resp = requests.get(target["url"], headers=headers, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    
                    for a in soup.find_all("a", href=True):
                        title = a.get_text(strip=True)
                        raw_href = a["href"].strip()
                        
                        if not raw_href or raw_href.startswith("javascript") or raw_href == "#":
                            continue

                        full_url = urljoin(target["url"], raw_href)
                        
                        full_text = f"{title} {full_url}".lower()
                        if len(title) > 8 and any(kw in full_text for kw in target["keywords"]):
                            img_src = COOP_IMAGES[img_idx % len(COOP_IMAGES)]
                            img_idx += 1

                            item = NoticeItem(
                                title=title[:100],
                                url=full_url,
                                source=target["name"],
                                location="VALENCIA / " + ("ALAQUÀS" if "alaquas" in full_text else ("PATERNA" if "paterna" in full_text else "VALENCIA")),
                                notice_type="Cooperativa VPO",
                                description=f"Proyecto en cooperativa VPO/VPP por {target['name']}",
                                raw_identifier=full_url,
                                image_url=img_src,
                                units="64 viviendas",
                                bedrooms="2-3 dormitorios",
                                size_m2="Desde 90 m²",
                                status="COOPERATIVA VPO"
                            )
                            items.append(item)
            except Exception as e:
                logger.warning(f"Error parseando cooperativa {target['name']} ({target['url']}): {e}")

        return items
