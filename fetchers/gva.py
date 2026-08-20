import logging
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import List, Tuple
from fetchers.base import BaseFetcher, NoticeItem

logger = logging.getLogger(__name__)

# Diccionario de Municipios, Distritos y Zonas Relevantes en la CV
KNOWN_LOCATIONS = [
    # Valencia Capital y Distritos / Barrios
    ("LA TORRE", "VALENCIA / LA TORRE"),
    ("MALILLA", "VALENCIA / MALILLA"),
    ("PATRAIX", "VALENCIA / PATRAIX"),
    ("QUATRE CARRERES", "VALENCIA / QUATRE CARRERES"),
    ("BENIMACLET", "VALENCIA / BENIMACLET"),
    ("TURIANOVA", "VALENCIA / TURIANOVA"),
    ("NOU MOLES", "VALENCIA / NOU MOLES"),
    ("MORERAS", "VALENCIA / LAS MORERAS"),
    ("SAFRANAR", "VALENCIA / SAFRANAR"),
    ("BENICALAP", "VALENCIA / BENICALAP"),
    ("VALÈNCIA", "VALENCIA CAPITAL"),
    ("VALENCIA", "VALENCIA CAPITAL"),

    # L'Horta Sud
    ("TORRENT", "L'HORTA SUD / TORRENT"),
    ("MISLATA", "L'HORTA SUD / MISLATA"),
    ("QUART DE POBLET", "L'HORTA SUD / QUART DE POBLET"),
    ("ALAQUÀS", "L'HORTA SUD / ALAQUÀS"),
    ("ALAQUAS", "L'HORTA SUD / ALAQUÀS"),
    ("ALDAIA", "L'HORTA SUD / ALDAIA"),
    ("XIRIVELLA", "L'HORTA SUD / XIRIVELLA"),
    ("ALFAFAR", "L'HORTA SUD / ALFAFAR"),
    ("CATARROJA", "L'HORTA SUD / CATARROJA"),
    ("MASSANASSA", "L'HORTA SUD / MASSANASSA"),
    ("PAIPORTA", "L'HORTA SUD / PAIPORTA"),
    ("PICANYA", "L'HORTA SUD / PICANYA"),
    ("SEDAVÍ", "L'HORTA SUD / SEDAVÍ"),
    ("BENETÚSSER", "L'HORTA SUD / BENETÚSSER"),
    ("SILLA", "L'HORTA SUD / SILLA"),
    ("MANISES", "L'HORTA SUD / MANISES"),

    # L'Horta Nord y Camp de Túria
    ("PATERNA", "L'HORTA NORD / PATERNA"),
    ("BURJASSOT", "L'HORTA NORD / BURJASSOT"),
    ("GODELLA", "L'HORTA NORD / GODELLA"),
    ("L'ELIANA", "CAMP DE TÚRIA / L'ELIANA"),
    ("ELIANA", "CAMP DE TÚRIA / L'ELIANA"),
    ("BÉTERA", "CAMP DE TÚRIA / BÉTERA"),
    ("SAGUNTO", "CAMP DE MORVEDRE / SAGUNTO"),
    ("SAGUNT", "CAMP DE MORVEDRE / SAGUNTO"),
    ("MONCADA", "L'HORTA NORD / MONCADA"),
    ("ROCAFORT", "L'HORTA NORD / ROCAFORT"),
    ("PUÇOL", "L'HORTA NORD / PUÇOL"),
    ("POBLA DE VALLBONA", "CAMP DE TÚRIA / LA POBLA"),
    ("RIBA-ROJA", "CAMP DE TÚRIA / RIBA-ROJA"),
    ("ALBORAYA", "L'HORTA NORD / ALBORAYA"),
    ("EL PUIG", "L'HORTA NORD / EL PUIG"),
    ("BENIFAIÓ", "RIBERA ALTA / BENIFAIÓ"),

    # Otras zonas destacadas de la CV
    ("GANDIA", "LA SAFOR / GANDIA"),
    ("ALZIRA", "RIBERA ALTA / ALZIRA"),
    ("BENIDORM", "MARINA BAIXA / BENIDORM"),
    ("TORREVIEJA", "VEGA BAJA / TORREVIEJA"),
    ("ALICANTE", "ALICANTE / ALACANT"),
    ("CASTELLÓN", "CASTELLÓN / CASTELLÓ"),
    ("TEULADA", "MARINA ALTA / TEULADA"),
    ("VILLAJOYOSA", "MARINA BAIXA / VILLAJOYOSA"),
    ("XÀBIA", "MARINA ALTA / XÀBIA")
]

def extract_specific_location_and_details(title: str, text: str = "") -> Tuple[str, str]:
    """
    Analiza el titulo y texto de la noticia para extraer la ubicacion concreta
    (municipio, barrio, sector) y detalles de la parcela o calle.
    """
    full_content = f"{title} {text}".upper()

    # 1. Buscar coincidencia de municipio/barrio
    matched_loc = "VALENCIA / PROVINCIA"
    for keyword, formatted_loc in KNOWN_LOCATIONS:
        if keyword in full_content:
            matched_loc = formatted_loc
            break

    # 2. Buscar detalles de parcelas, sectores o calles
    parcel_details = []
    
    # Buscar patrones de parcela (ej: Parcela R-3, Parcela 12, PAI Malilla)
    parcel_match = re.search(r'(PARCELA\s*[\w\d-]+|PAI\s*[\w\d-]+|SECTOR\s*[\w\d-]+|FINCA\s*[\w\d-]+)', full_content)
    if parcel_match:
        parcel_details.append(f"📍 {parcel_match.group(1).title()}")

    # Buscar patrones de número de viviendas en la licitación
    viviendas_match = re.search(r'(\d+\s*VIVIENDAS|\d+\s*PARCELAS)', full_content)
    if viviendas_match:
        parcel_details.append(f"🏗️ {viviendas_match.group(1).title()}")

    # Buscar calles o avenidas
    street_match = re.search(r'(CALLE\s+[\w\s]+|AVENIDA\s+[\w\s]+|PLAZA\s+[\w\s]+)', full_content)
    if street_match:
        street_clean = street_match.group(1).title()[:40]
        parcel_details.append(f"🛣️ {street_clean}")

    extra_desc = " | ".join(parcel_details) if parcel_details else "Licitación pública de parcela residencial / Plan VIVE"

    return matched_loc, extra_desc


class GVAFetcher(BaseFetcher):
    """
    Fetcher para la Entidad Valenciana de Vivienda y Suelo (EVha) y Conselleria.
    Filtra estrictamente licitaciones de suelo, pliegos, permutas y concursos de suelo del Plan VIVE,
    extrayendo el municipio concreto y detalles de parcela/calle.
    """
    name = "EVha & Plan VIVE (Licitaciones de Suelo)"

    URLS = [
        "https://www.evha.es/portal/castellano/prensa.php",
        "https://habitatge.gva.es/es/novetats-conselleria"
    ]

    TENDER_KEYWORDS = [
        "licitaci", "concurso", "suelo", "parcela", "permuta", 
        "derecho de superficie", "plan vive", "plan viu", "enajenaci", 
        "adjudicaci", "pliego", "vpo", "vpp"
    ]

    REJECT_KEYWORDS = [
        "protección de datos", "normativa jurídica", "guía vecindad", 
        "servicios a cooperativas", "visita las obras", "demolición", 
        "violencia", "nombra presidente", "convivencia",
        "aplaza el pago", "atención", "reparación de",
        "presenta la nueva web", "punto de información", "registro único"
    ]

    def fetch(self) -> List[NoticeItem]:
        items: List[NoticeItem] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        for base_url in self.URLS:
            try:
                resp = requests.get(base_url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    
                    for a in soup.find_all("a", href=True):
                        title = a.get_text(strip=True)
                        raw_href = a["href"].strip()

                        if not raw_href or raw_href.startswith("javascript") or raw_href == "#":
                            continue

                        full_url = urljoin(base_url, raw_href)
                        title_lower = title.lower()

                        if any(rej in title_lower for rej in self.REJECT_KEYWORDS):
                            continue

                        if len(title) > 15 and any(kw in title_lower for kw in self.TENDER_KEYWORDS):
                            # Extraer ubicación específica y detalles de parcela
                            location, details = extract_specific_location_and_details(title)

                            item = NoticeItem(
                                title=title[:90].upper(),
                                url=full_url,
                                source="EVha / Plan VIVE",
                                location=location,
                                notice_type="Licitación Suelo / Plan VIVE",
                                description=details,
                                raw_identifier=full_url,
                                image_url="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80",
                                units="Parcela / Licitación",
                                bedrooms="Plurifamiliar VPO",
                                size_m2="Suelo Residencial",
                                status="LICITACIÓN SUELO"
                            )
                            items.append(item)
            except Exception as e:
                logger.warning(f"Error parseando fuente oficial {base_url}: {e}")

        return items
