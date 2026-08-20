import sqlite3
import hashlib
from datetime import datetime, timedelta
from config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Inicializa y actualiza las tablas de la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id TEXT PRIMARY KEY,
            url TEXT,
            title TEXT,
            source TEXT,
            location TEXT,
            price REAL,
            notice_type TEXT,
            created_at TIMESTAMP,
            notified BOOLEAN DEFAULT 0,
            image_url TEXT DEFAULT '',
            units TEXT DEFAULT 'Consultar',
            bedrooms TEXT DEFAULT 'Consultar',
            size_m2 TEXT DEFAULT 'Consultar',
            status TEXT DEFAULT 'EN VENTA',
            last_seen TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    
    cursor.execute("PRAGMA table_info(notices)")
    columns = [row[1] for row in cursor.fetchall()]
    
    new_cols = {
        "image_url": "TEXT DEFAULT ''",
        "units": "TEXT DEFAULT 'Consultar'",
        "bedrooms": "TEXT DEFAULT 'Consultar'",
        "size_m2": "TEXT DEFAULT 'Consultar'",
        "status": "TEXT DEFAULT 'EN VENTA'",
        "last_seen": "TIMESTAMP",
        "is_active": "BOOLEAN DEFAULT 1"
    }
    
    for col_name, col_type in new_cols.items():
        if col_name not in columns:
            cursor.execute(f"ALTER TABLE notices ADD COLUMN {col_name} {col_type}")

    conn.commit()
    conn.close()

def generate_notice_id(source: str, identifier: str) -> str:
    return hashlib.sha256(f"{source}:{identifier}".encode('utf-8')).hexdigest()

def is_notice_seen(notice_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM notices WHERE id = ?", (notice_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_notice(notice_id: str, url: str, title: str, source: str, location: str = "", price: float = 0.0, 
                notice_type: str = "Plurifamiliar", notified: bool = False, image_url: str = "", 
                units: str = "Consultar", bedrooms: str = "Consultar", size_m2: str = "Consultar", 
                status: str = "EN VENTA"):
    """Guarda o actualiza una vivienda y refresca la fecha de última detección (last_seen)."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        INSERT OR REPLACE INTO notices 
        (id, url, title, source, location, price, notice_type, created_at, notified, image_url, units, bedrooms, size_m2, status, last_seen, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (notice_id, url, title, source, location, price, notice_type, now, 
          1 if notified else 0, image_url, units, bedrooms, size_m2, status, now))
    conn.commit()
    conn.close()

def sync_active_status(current_run_notice_ids: set):
    """
    Marca como inactivas o vendidas las viviendas que ya no aparecen en los portales
    tras las últimas ejecuciones.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Marcar como inactivas las que no fueron vistas en el rastreo actual
    cursor.execute("SELECT id FROM notices WHERE is_active = 1")
    all_active_ids = [row[0] for row in cursor.fetchall()]
    
    for nid in all_active_ids:
        if nid not in current_run_notice_ids:
            cursor.execute("UPDATE notices SET is_active = 0, status = 'VENDIDA / FINALIZADA' WHERE id = ?", (nid,))
            
    conn.commit()
    conn.close()

def get_recent_notices(limit: int = 300, only_active: bool = True):
    """Obtiene las viviendas activas registradas con todos sus atributos."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT id, title, source, location, price, url, created_at, notified, image_url, units, bedrooms, size_m2, status
        FROM notices
    """
    if only_active:
        query += " WHERE is_active = 1 "
        
    query += " ORDER BY created_at DESC LIMIT ?"
    
    cursor.execute(query, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

init_db()
