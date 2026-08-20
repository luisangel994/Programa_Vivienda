from dataclasses import dataclass

@dataclass
class NoticeItem:
    title: str
    url: str
    source: str
    location: str = "Valencia / Área Metropolitana"
    price: float = 0.0
    notice_type: str = "Plurifamiliar"
    description: str = ""
    raw_identifier: str = ""
    image_url: str = ""
    units: str = "Consultar"
    bedrooms: str = "Consultar"
    size_m2: str = "Consultar"
    status: str = "EN VENTA"

class BaseFetcher:
    """Clase base para todos los extractores de noticias/promociones."""
    name: str = "BaseFetcher"

    def fetch(self):
        raise NotImplementedError("Cada fetcher debe implementar el metodo fetch()")
