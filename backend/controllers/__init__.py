# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Controllers Paketi
# ============================================

from .auth_controller import auth_bp
from .kitap_controller import kitap_bp
from .kullanici_controller import kullanici_bp
from .yazar_controller import yazar_bp
from .kategori_controller import kategori_bp
from .odunc_controller import odunc_bp
from .ceza_controller import ceza_bp
from .istatistik_controller import istatistik_bp

__all__ = [
    'auth_bp',
    'kitap_bp',
    'kullanici_bp',
    'yazar_bp',
    'kategori_bp',
    'odunc_bp',
    'ceza_bp',
    'istatistik_bp'
]
