import logging
from typing import List, Tuple
from fetchers.base import NoticeItem
from config import TARGET_LOCATIONS, POSITIVE_KEYWORDS, NEGATIVE_KEYWORDS, MAX_PRICE_EUR

logger = logging.getLogger(__name__)

class FilterEngine:
    """
    Motor de filtrado para evaluar si un NoticeItem cumple con todos los criterios de busqueda:
    1. Match de Palabras Clave Obligatorias
    2. Ausencia de Palabras Clave Excluyentes (Blacklist)
    3. Coincidencia de Ubicación Geográfica (Valencia y Área Metropolitana)
    4. Umbral Económico (Precio <= 300.000 €)
    """

    def evaluate(self, item: NoticeItem) -> Tuple[bool, str]:
        text_to_analyze = f"{item.title} {item.description} {item.location} {item.url}".lower()

        # 1. Comprobar palabras clave excluyentes (Blacklist)
        for neg in NEGATIVE_KEYWORDS:
            if neg.lower() in text_to_analyze:
                return False, f"Descartado por palabra clave rechazada: '{neg}'"

        # 2. Comprobar palabras clave obligatorias (Match Positivo)
        has_positive = any(pos.lower() in text_to_analyze for pos in POSITIVE_KEYWORDS)
        # Si la fuente proviene de una cooperativa conocida o licitacion VPO, se presupone positiva
        is_trusted_source = any(ts in item.source.lower() for ts in ["cooperativa", "vpo", "placsp", "dogv", "sfi", "prygesa", "fecovi", "olivares"])
        
        if not (has_positive or is_trusted_source):
            return False, "Descartado: no contiene palabras clave obligatorias de VPO/VPP/Obra Nueva"

        # 3. Comprobar ubicación geográfica
        has_location = any(loc.lower() in text_to_analyze for loc in TARGET_LOCATIONS)
        # Si no especifica ubicacion concreta o es general de la fuente, aceptamos por defecto
        if item.location and not has_location:
            # Si el texto explicito de ubicación difiere totalmente y no es Valencia/provincia
            if "madrid" in text_to_analyze or "barcelona" in text_to_analyze or "sevilla" in text_to_analyze:
                return False, "Descartado por ubicacion fuera de la provincia de Valencia"

        # 4. Comprobar precio máximo (si está disponible)
        if item.price > 0 and item.price > MAX_PRICE_EUR:
            return False, f"Descartado por exceder el presupuesto máximo ({item.price:.2f} € > {MAX_PRICE_EUR:.2f} €)"

        return True, "Apto para notificación"

    def filter_items(self, items: List[NoticeItem]) -> List[NoticeItem]:
        valid_items: List[NoticeItem] = []
        for item in items:
            passed, reason = self.evaluate(item)
            if passed:
                valid_items.append(item)
            else:
                logger.debug(f"Item omitido '{item.title}': {reason}")
        return valid_items
