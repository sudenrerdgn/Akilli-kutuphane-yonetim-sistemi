# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Models Katmanı veritabanındaki her tablo için sınıf tanımlanır python karşılığı burası



from datetime import datetime 
from dataclasses import dataclass
from typing import Optional # Optional[int]: int veya None olabilir anlamında

@dataclass 
class Kullanici:
    """Kullanici varlik sinifi"""
    kullanici_id: Optional[int] = None #Bu alan int olabilir ama boş da olabilir; = None: Varsayılan değer atanır
    ad: str = "" # boş bırakılabilir ama string girilmeli
    soyad: str = ""
    email: str = ""
    sifre: str = "" #hashlenmiş şifre koyulur
    telefon: Optional[str] = None 
    rol: str = "uye"  # admin, personel, uye
    durum: bool = True #kullanıcı aktif mi
    kayit_tarihi: Optional[datetime] = None #Kayıt sırasında otomatik atanır
    son_giris_tarihi: Optional[datetime] = None
    
    def to_dict(self): # Nesneyi sözlüğe çevirir. API cevap olarak gönderebilmesi için bu dönüşüm şarttır. key-value şeklinde döndürür. veri tabanı sonuçlarını temiz sunmayı sağlar
        # Şifre güvenlik nedeniyle dahil edilmez!
        # datetime'ı string'e çevir (JSON serializable olması için)
        #gerekirse hesaplama yapar vs vs
        # to_dict, nesneyi güvenli, okunabilir ve JSON uyumlu hale getirmek için kullanılır.
        return {
            'kullanici_id': self.kullanici_id,
            'ad': self.ad,
            'soyad': self.soyad,
            'email': self.email,
            'telefon': self.telefon,
            'rol': self.rol,
            'durum': self.durum,
            'kayit_tarihi': str(self.kayit_tarihi) if self.kayit_tarihi else None,
            """datetime nesneleri JSON’a çevrilemez, None ise "None" string’i dönmemeli"""
            'son_giris_tarihi': str(self.son_giris_tarihi) if self.son_giris_tarihi else None
        }


@dataclass
class Kategori:
    """Kategori varlik sinifi"""
    kategori_id: Optional[int] = None
    kategori_adi: str = ""
    aciklama: Optional[str] = None
    olusturma_tarihi: Optional[datetime] = None
    
    def to_dict(self): #self=this denilebilir 
        return {
            'kategori_id': self.kategori_id,
            'kategori_adi': self.kategori_adi,
            'aciklama': self.aciklama,
            'olusturma_tarihi': str(self.olusturma_tarihi) if self.olusturma_tarihi else None
        }


@dataclass
class Yazar:
    """Yazar varlik sinifi"""
    yazar_id: Optional[int] = None
    ad: str = ""
    soyad: str = ""
    biyografi: Optional[str] = None
    dogum_tarihi: Optional[datetime] = None
    ulke: Optional[str] = None
    olusturma_tarihi: Optional[datetime] = None
    
    def to_dict(self): #varligi szöluge çeviriyorum  
        return {
            'yazar_id': self.yazar_id,
            'ad': self.ad,
            'soyad': self.soyad,
            'tam_ad': f"{self.ad} {self.soyad}", # f-string ile birleştirilmiş tam ad
            'biyografi': self.biyografi,
            'dogum_tarihi': str(self.dogum_tarihi) if self.dogum_tarihi else None,
            'ulke': self.ulke,
            'olusturma_tarihi': str(self.olusturma_tarihi) if self.olusturma_tarihi else None
        }


@dataclass
class Kitap:
    """Kitap varlik sinifi"""
    kitap_id: Optional[int] = None
    isbn: str = ""
    kitap_adi: str = ""
    yazar_id: Optional[int] = None
    kategori_id: Optional[int] = None
    yayin_yili: Optional[int] = None
    yayin_evi: Optional[str] = None
    sayfa_sayisi: Optional[int] = None
    dil: str = "Türkçe"
    aciklama: Optional[str] = None
    kapak_resmi: Optional[str] = None
    toplam_adet: int = 1    
    mevcut_adet: int = 1
    durum: bool = True
    eklenme_tarihi: Optional[datetime] = None
    
    # İlişkili alanlar (JOIN ile gelir)
    # Bu alanlar veritabanında yok, sorgu sonucunda doldurulur
    yazar_adi: Optional[str] = None
    kategori_adi: Optional[str] = None
    
    def to_dict(self):
        return {
            'kitap_id': self.kitap_id,
            'isbn': self.isbn, #uluslararası kitap numarası
            'kitap_adi': self.kitap_adi,
            'yazar_id': self.yazar_id,
            'yazar_adi': self.yazar_adi,
            'kategori_id': self.kategori_id,
            'kategori_adi': self.kategori_adi,
            'yayin_yili': self.yayin_yili,
            'yayin_evi': self.yayin_evi,
            'sayfa_sayisi': self.sayfa_sayisi,
            'dil': self.dil,
            'aciklama': self.aciklama,
            'kapak_resmi': self.kapak_resmi,
            'toplam_adet': self.toplam_adet,
            'mevcut_adet': self.mevcut_adet,
            'durum': 'Aktif' if self.durum else 'Pasif',
            'mevcut_durum': 'Mevcut' if self.mevcut_adet > 0 else 'Tükendi',
            'eklenme_tarihi': str(self.eklenme_tarihi) if self.eklenme_tarihi else None
        }


@dataclass
class OduncIslem:
    """Ödünç İşlemi varlik sinifi"""
    odunc_id: Optional[int] = None
    kitap_id: int = 0
    kullanici_id: int = 0
    odunc_tarihi: Optional[datetime] = None
    teslim_tarihi: Optional[datetime] = None
    iade_tarihi: Optional[datetime] = None
    durum: str = "odunc"  # odunc, iade, geciken
    notlar: Optional[str] = None
    
    # İlişkili alanlar
    kitap_adi: Optional[str] = None
    kullanici_adi: Optional[str] = None
    gecikme_gunu: int = 0
    
    def to_dict(self): #varlık sözlüğe çevrilir
        return {
            'odunc_id': self.odunc_id,
            'kitap_id': self.kitap_id,
            'kitap_adi': self.kitap_adi,
            'kullanici_id': self.kullanici_id,
            'kullanici_adi': self.kullanici_adi,
            'odunc_tarihi': str(self.odunc_tarihi) if self.odunc_tarihi else None,
            'teslim_tarihi': str(self.teslim_tarihi) if self.teslim_tarihi else None,
            'iade_tarihi': str(self.iade_tarihi) if self.iade_tarihi else None,
            'durum': self.durum,
            'durum_aciklama': self._durum_aciklama(), # Private metod çağrısı
            'notlar': self.notlar,
            'gecikme_gunu': self.gecikme_gunu
        }
    
    def _durum_aciklama(self): # _ ile başlayan metodlar private (özel) kabul edilir.
        durumlar = {
            'odunc': 'Ödünç Alındı', #key-value kısımları
            'iade': 'İade Edildi',
            'geciken': 'Gecikmiş'
        }
        # .get(): Key yoksa varsayılan değer döndür
        return durumlar.get(self.durum, 'Bilinmiyor') #self.durum sözlükte varsa karşılığı döndürülür yoksa "bilinmiyor" döner


@dataclass
class Ceza:
    """Ceza varlik sinifi"""
    ceza_id: Optional[int] = None
    odunc_id: int = 0
    kullanici_id: int = 0
    gecikme_gunu: int = 0
    ceza_tutari: float = 0.0
    odenme_durumu: bool = False
    olusturma_tarihi: Optional[datetime] = None
    odeme_tarihi: Optional[datetime] = None
    
    # İlişkili alanlar
    kullanici_adi: Optional[str] = None
    kitap_adi: Optional[str] = None
    
    def to_dict(self): #varlığı sözlüğe çevirme
        return {
            'ceza_id': self.ceza_id,
            'odunc_id': self.odunc_id,
            'kullanici_id': self.kullanici_id,
            'kullanici_adi': self.kullanici_adi,
            'kitap_adi': self.kitap_adi,
            'gecikme_gunu': self.gecikme_gunu,
            'ceza_tutari': self.ceza_tutari,
            'odenme_durumu': self.odenme_durumu,
            'odenme_durumu_aciklama': 'Ödendi' if self.odenme_durumu else 'Ödenmedi',
            'olusturma_tarihi': str(self.olusturma_tarihi) if self.olusturma_tarihi else None,
            'odeme_tarihi': str(self.odeme_tarihi) if self.odeme_tarihi else None
        }


@dataclass
class SistemLog:
    """Sistem Log varlik sinifi"""
    log_id: Optional[int] = None
    kullanici_id: Optional[int] = None
    islem: str = ""
    detay: Optional[str] = None
    ip_adresi: Optional[str] = None
    tarih: Optional[datetime] = None
    
    def to_dict(self): #varlığı sözlüğe çevirir
        return {
            'log_id': self.log_id,
            'kullanici_id': self.kullanici_id,
            'islem': self.islem,
            'detay': self.detay,
            'ip_adresi': self.ip_adresi,
            'tarih': str(self.tarih) if self.tarih else None # tarih varsa stringe çevrilir yoksa none atanır
        }
