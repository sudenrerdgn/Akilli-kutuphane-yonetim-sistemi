# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Repository Katmanı
# ============================================

from utils.db_connection import db
from models import Kullanici, Kitap, Yazar, Kategori, OduncIslem, Ceza, SistemLog
from typing import List, Optional
from datetime import datetime


class KullaniciRepository:
    """Kullanıcı Repository Sınıfı"""
    
    @staticmethod
    def get_all() -> List[dict]:
        """Tüm kullanıcıları getirir"""
        query = """
            SELECT KullaniciID, Ad, Soyad, Email, Telefon, Rol, Durum, 
                   KayitTarihi, SonGirisTarihi 
            FROM Kullanicilar 
            WHERE Durum = 1
            ORDER BY Ad, Soyad
        """
        return db.execute_query(query)
    
    @staticmethod
    def get_by_id(kullanici_id: int) -> Optional[dict]:
        """ID'ye göre kullanıcı getirir"""
        query = """
            SELECT KullaniciID, Ad, Soyad, Email, Telefon, Rol, Durum, 
                   KayitTarihi, SonGirisTarihi 
            FROM Kullanicilar 
            WHERE KullaniciID = ?
        """
        results = db.execute_query(query, (kullanici_id,))
        return results[0] if results else None
    
    @staticmethod
    def get_by_email(email: str) -> Optional[dict]:
        """Email'e göre kullanıcı getirir (şifre dahil)"""
        query = """
            SELECT KullaniciID, Ad, Soyad, Email, Sifre, Telefon, Rol, Durum
            FROM Kullanicilar 
            WHERE Email = ? AND Durum = 1
        """
        results = db.execute_query(query, (email,))
        return results[0] if results else None
    
    @staticmethod
    def create(kullanici: dict) -> int:
        """Yeni kullanıcı oluşturur"""
        query = """
            INSERT INTO Kullanicilar (Ad, Soyad, Email, Sifre, Telefon, Rol)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            kullanici['ad'],
            kullanici['soyad'],
            kullanici['email'],
            kullanici['sifre'],
            kullanici.get('telefon'),
            kullanici.get('rol', 'uye')
        )
        return db.execute_insert_get_id(query, params)
    
    @staticmethod
    def update(kullanici_id: int, kullanici: dict) -> int:
        """Kullanıcı günceller"""
        query = """
            UPDATE Kullanicilar 
            SET Ad = ?, Soyad = ?, Email = ?, Telefon = ?, Rol = ?
            WHERE KullaniciID = ?
        """
        params = (
            kullanici['ad'],
            kullanici['soyad'],
            kullanici['email'],
            kullanici.get('telefon'),
            kullanici.get('rol', 'uye'),
            kullanici_id
        )
        return db.execute_non_query(query, params)
    
    @staticmethod
    def update_password(kullanici_id: int, hashed_password: str) -> int:
        """Şifre günceller"""
        query = "UPDATE Kullanicilar SET Sifre = ? WHERE KullaniciID = ?"
        return db.execute_non_query(query, (hashed_password, kullanici_id))
    
    @staticmethod
    def update_last_login(kullanici_id: int) -> int:
        """Son giriş tarihini günceller"""
        query = "UPDATE Kullanicilar SET SonGirisTarihi = GETDATE() WHERE KullaniciID = ?"
        return db.execute_non_query(query, (kullanici_id,))
    
    @staticmethod
    def delete(kullanici_id: int) -> int:
        """Kullanıcıyı pasif yapar (soft delete)"""
        query = "UPDATE Kullanicilar SET Durum = 0 WHERE KullaniciID = ?"
        return db.execute_non_query(query, (kullanici_id,))
    
    @staticmethod
    def check_email_exists(email: str, exclude_id: int = None) -> bool:
        """Email'in mevcut olup olmadığını kontrol eder"""
        if exclude_id:
            query = "SELECT COUNT(*) FROM Kullanicilar WHERE Email = ? AND KullaniciID != ?"
            count = db.execute_scalar(query, (email, exclude_id))
        else:
            query = "SELECT COUNT(*) FROM Kullanicilar WHERE Email = ?"
            count = db.execute_scalar(query, (email,))
        return count > 0


class KitapRepository:
    """Kitap Repository Sınıfı"""
    
    @staticmethod
    def get_all() -> List[dict]:
        """Tüm kitapları getirir"""
        query = """
            SELECT k.KitapID, k.ISBN, k.KitapAdi, k.YazarID, 
                   y.Ad + ' ' + y.Soyad AS YazarAdi,
                   k.KategoriID, kat.KategoriAdi,
                   k.YayinYili, k.YayinEvi, k.SayfaSayisi, k.Dil,
                   k.Aciklama, k.KapakResmi, k.ToplamAdet, k.MevcutAdet,
                   k.Durum, k.EklenmeTarihi
            FROM Kitaplar k
            LEFT JOIN Yazarlar y ON k.YazarID = y.YazarID
            LEFT JOIN Kategoriler kat ON k.KategoriID = kat.KategoriID
            WHERE k.Durum = 1
            ORDER BY k.KitapAdi
        """
        return db.execute_query(query)
    
    @staticmethod
    def get_by_id(kitap_id: int) -> Optional[dict]:
        """ID'ye göre kitap getirir"""
        query = """
            SELECT k.KitapID, k.ISBN, k.KitapAdi, k.YazarID, 
                   y.Ad + ' ' + y.Soyad AS YazarAdi,
                   k.KategoriID, kat.KategoriAdi,
                   k.YayinYili, k.YayinEvi, k.SayfaSayisi, k.Dil,
                   k.Aciklama, k.KapakResmi, k.ToplamAdet, k.MevcutAdet,
                   k.Durum, k.EklenmeTarihi
            FROM Kitaplar k
            LEFT JOIN Yazarlar y ON k.YazarID = y.YazarID
            LEFT JOIN Kategoriler kat ON k.KategoriID = kat.KategoriID
            WHERE k.KitapID = ?
        """
        results = db.execute_query(query, (kitap_id,))
        return results[0] if results else None
    
    @staticmethod
    def search(arama: str = None, kategori_id: int = None, 
               yazar_id: int = None, sadece_mevcut: bool = False) -> List[dict]:
        """Kitap arar (Stored Procedure kullanarak)"""
        return db.execute_stored_procedure(
            'sp_KitapAra', 
            (arama, kategori_id, yazar_id, 1 if sadece_mevcut else 0)
        )
    
    @staticmethod
    def create(kitap: dict) -> int:
        """Yeni kitap oluşturur"""
        query = """
            INSERT INTO Kitaplar (ISBN, KitapAdi, YazarID, KategoriID, YayinYili, 
                                  YayinEvi, SayfaSayisi, Dil, Aciklama, KapakResmi, 
                                  ToplamAdet, MevcutAdet)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            kitap['isbn'],
            kitap['kitap_adi'],
            kitap.get('yazar_id'),
            kitap.get('kategori_id'),
            kitap.get('yayin_yili'),
            kitap.get('yayin_evi'),
            kitap.get('sayfa_sayisi'),
            kitap.get('dil', 'Türkçe'),
            kitap.get('aciklama'),
            kitap.get('kapak_resmi'),
            kitap.get('toplam_adet', 1),
            kitap.get('mevcut_adet', 1)
        )
        return db.execute_insert_get_id(query, params)
    
    @staticmethod
    def update(kitap_id: int, kitap: dict) -> int:
        """Kitap günceller"""
        query = """
            UPDATE Kitaplar 
            SET ISBN = ?, KitapAdi = ?, YazarID = ?, KategoriID = ?, 
                YayinYili = ?, YayinEvi = ?, SayfaSayisi = ?, Dil = ?,
                Aciklama = ?, KapakResmi = ?, ToplamAdet = ?, MevcutAdet = ?
            WHERE KitapID = ?
        """
        params = (
            kitap['isbn'],
            kitap['kitap_adi'],
            kitap.get('yazar_id'),
            kitap.get('kategori_id'),
            kitap.get('yayin_yili'),
            kitap.get('yayin_evi'),
            kitap.get('sayfa_sayisi'),
            kitap.get('dil', 'Türkçe'),
            kitap.get('aciklama'),
            kitap.get('kapak_resmi'),
            kitap.get('toplam_adet', 1),
            kitap.get('mevcut_adet', 1),
            kitap_id
        )
        return db.execute_non_query(query, params)
    
    @staticmethod
    def delete(kitap_id: int) -> int:
        """Kitabı pasif yapar"""
        query = "UPDATE Kitaplar SET Durum = 0 WHERE KitapID = ?"
        return db.execute_non_query(query, (kitap_id,))
    
    @staticmethod
    def check_isbn_exists(isbn: str, exclude_id: int = None) -> bool:
        """ISBN'in mevcut olup olmadığını kontrol eder"""
        if exclude_id:
            query = "SELECT COUNT(*) FROM Kitaplar WHERE ISBN = ? AND KitapID != ?"
            count = db.execute_scalar(query, (isbn, exclude_id))
        else:
            query = "SELECT COUNT(*) FROM Kitaplar WHERE ISBN = ?"
            count = db.execute_scalar(query, (isbn,))
        return count > 0


class YazarRepository:
    """Yazar Repository Sınıfı"""
    
    @staticmethod
    def get_all() -> List[dict]:
        """Tüm yazarları getirir"""
        query = """
            SELECT YazarID, Ad, Soyad, Ad + ' ' + Soyad AS TamAd,
                   Biyografi, DogumTarihi, Ulke, OlusturmaTarihi
            FROM Yazarlar
            ORDER BY Ad, Soyad
        """
        return db.execute_query(query)
    
    @staticmethod
    def get_by_id(yazar_id: int) -> Optional[dict]:
        """ID'ye göre yazar getirir"""
        query = """
            SELECT YazarID, Ad, Soyad, Biyografi, DogumTarihi, Ulke, OlusturmaTarihi
            FROM Yazarlar
            WHERE YazarID = ?
        """
        results = db.execute_query(query, (yazar_id,))
        return results[0] if results else None
    
    @staticmethod
    def create(yazar: dict) -> int:
        """Yeni yazar oluşturur"""
        query = """
            INSERT INTO Yazarlar (Ad, Soyad, Biyografi, DogumTarihi, Ulke)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            yazar['ad'],
            yazar['soyad'],
            yazar.get('biyografi'),
            yazar.get('dogum_tarihi'),
            yazar.get('ulke')
        )
        return db.execute_insert_get_id(query, params)
    
    @staticmethod
    def update(yazar_id: int, yazar: dict) -> int:
        """Yazar günceller"""
        query = """
            UPDATE Yazarlar 
            SET Ad = ?, Soyad = ?, Biyografi = ?, DogumTarihi = ?, Ulke = ?
            WHERE YazarID = ?
        """
        params = (
            yazar['ad'],
            yazar['soyad'],
            yazar.get('biyografi'),
            yazar.get('dogum_tarihi'),
            yazar.get('ulke'),
            yazar_id
        )
        return db.execute_non_query(query, params)
    
    @staticmethod
    def delete(yazar_id: int) -> int:
        """Yazarı siler"""
        query = "DELETE FROM Yazarlar WHERE YazarID = ?"
        return db.execute_non_query(query, (yazar_id,))


class KategoriRepository:
    """Kategori Repository Sınıfı"""
    
    @staticmethod
    def get_all() -> List[dict]:
        """Tüm kategorileri getirir"""
        query = """
            SELECT KategoriID, KategoriAdi, Aciklama, OlusturmaTarihi
            FROM Kategoriler
            ORDER BY KategoriAdi
        """
        return db.execute_query(query)
    
    @staticmethod
    def get_by_id(kategori_id: int) -> Optional[dict]:
        """ID'ye göre kategori getirir"""
        query = """
            SELECT KategoriID, KategoriAdi, Aciklama, OlusturmaTarihi
            FROM Kategoriler
            WHERE KategoriID = ?
        """
        results = db.execute_query(query, (kategori_id,))
        return results[0] if results else None
    
    @staticmethod
    def create(kategori: dict) -> int:
        """Yeni kategori oluşturur"""
        query = "INSERT INTO Kategoriler (KategoriAdi, Aciklama) VALUES (?, ?)"
        return db.execute_insert_get_id(query, (kategori['kategori_adi'], kategori.get('aciklama')))
    
    @staticmethod
    def update(kategori_id: int, kategori: dict) -> int:
        """Kategori günceller"""
        query = "UPDATE Kategoriler SET KategoriAdi = ?, Aciklama = ? WHERE KategoriID = ?"
        return db.execute_non_query(query, (kategori['kategori_adi'], kategori.get('aciklama'), kategori_id))
    
    @staticmethod
    def delete(kategori_id: int) -> int:
        """Kategori siler"""
        query = "DELETE FROM Kategoriler WHERE KategoriID = ?"
        return db.execute_non_query(query, (kategori_id,))


class OduncRepository:
    """Ödünç İşlemi Repository Sınıfı"""
    
    @staticmethod
    def get_all() -> List[dict]:
        """Tüm ödünç işlemlerini getirir"""
        query = """
            SELECT o.OduncID, o.KitapID, k.KitapAdi, o.KullaniciID,
                   u.Ad + ' ' + u.Soyad AS KullaniciAdi,
                   o.OduncTarihi, o.TeslimTarihi, o.IadeTarihi, o.Durum, o.Notlar,
                   CASE 
                       WHEN o.Durum = 'odunc' AND GETDATE() > o.TeslimTarihi 
                       THEN DATEDIFF(MINUTE, o.TeslimTarihi, GETDATE())
                       ELSE 0 
                   END AS GecikmeGunu
            FROM OduncIslemleri o
            INNER JOIN Kitaplar k ON o.KitapID = k.KitapID
            INNER JOIN Kullanicilar u ON o.KullaniciID = u.KullaniciID
            ORDER BY o.OduncTarihi DESC
        """
        return db.execute_query(query)
    
    @staticmethod
    def get_by_id(odunc_id: int) -> Optional[dict]:
        """ID'ye göre ödünç işlemi getirir"""
        query = """
            SELECT o.OduncID, o.KitapID, k.KitapAdi, o.KullaniciID,
                   u.Ad + ' ' + u.Soyad AS KullaniciAdi, u.Email,
                   o.OduncTarihi, o.TeslimTarihi, o.IadeTarihi, o.Durum, o.Notlar
            FROM OduncIslemleri o
            INNER JOIN Kitaplar k ON o.KitapID = k.KitapID
            INNER JOIN Kullanicilar u ON o.KullaniciID = u.KullaniciID
            WHERE o.OduncID = ?
        """
        results = db.execute_query(query, (odunc_id,))
        return results[0] if results else None
    
    @staticmethod
    def get_by_user(kullanici_id: int) -> List[dict]:
        """Kullanıcının ödünç geçmişini getirir"""
        query = """
            SELECT o.OduncID, o.KitapID, k.KitapAdi, o.KullaniciID,
                   u.Ad + ' ' + u.Soyad AS KullaniciAdi,
                   o.OduncTarihi, o.TeslimTarihi, o.IadeTarihi, o.Durum,
                   CASE 
                       WHEN o.Durum = 'odunc' AND GETDATE() > o.TeslimTarihi 
                       THEN DATEDIFF(MINUTE, o.TeslimTarihi, GETDATE())
                       ELSE 0 
                   END AS GecikmeGunu
            FROM OduncIslemleri o
            INNER JOIN Kitaplar k ON o.KitapID = k.KitapID
            INNER JOIN Kullanicilar u ON o.KullaniciID = u.KullaniciID
            WHERE o.KullaniciID = ?
            ORDER BY o.OduncTarihi DESC
        """
        return db.execute_query(query, (kullanici_id,))
    
    @staticmethod
    def get_active_by_user(kullanici_id: int) -> List[dict]:
        """Kullanıcının aktif ödünçlerini getirir"""
        query = """
            SELECT o.OduncID, o.KitapID, k.KitapAdi, k.ISBN,
                   o.KullaniciID, o.OduncTarihi, o.TeslimTarihi, o.Durum,
                   CASE 
                       WHEN GETDATE() > o.TeslimTarihi 
                       THEN DATEDIFF(MINUTE, o.TeslimTarihi, GETDATE())
                       ELSE 0 
                   END AS GecikmeGunu
            FROM OduncIslemleri o
            INNER JOIN Kitaplar k ON o.KitapID = k.KitapID
            WHERE o.KullaniciID = ? AND o.Durum = 'odunc'
            ORDER BY o.TeslimTarihi
        """
        return db.execute_query(query, (kullanici_id,))
    
    @staticmethod
    def get_overdue() -> List[dict]:
        """Geciken kitapları getirir"""
        query = """
            SELECT o.OduncID, o.KitapID, k.KitapAdi, o.KullaniciID,
                   u.Ad + ' ' + u.Soyad AS KullaniciAdi, u.Email,
                   o.OduncTarihi, o.TeslimTarihi, o.Durum,
                   DATEDIFF(MINUTE, o.TeslimTarihi, GETDATE()) AS GecikmeGunu
            FROM OduncIslemleri o
            INNER JOIN Kitaplar k ON o.KitapID = k.KitapID
            INNER JOIN Kullanicilar u ON o.KullaniciID = u.KullaniciID
            WHERE o.Durum = 'odunc' AND GETDATE() > o.TeslimTarihi
            ORDER BY o.TeslimTarihi
        """
        return db.execute_query(query)
    
    @staticmethod
    def create(odunc: dict) -> int:
        """
        Yeni ödünç işlemi oluşturur
        
        Parametreler:
        - odunc_gun: Gün cinsinden süre
        - odunc_saat: Saat cinsinden süre
        - odunc_dakika: Dakika cinsinden süre
        
        Toplam süre = (gün * 24 * 60) + (saat * 60) + dakika olarak hesaplanır
        """
        # Değerleri al (varsayılan 0)
        gun = int(odunc.get('odunc_gun') or 0)
        saat = int(odunc.get('odunc_saat') or 0)
        dakika = int(odunc.get('odunc_dakika') or 0)
        
        # Hiçbiri verilmemişse varsayılan 14 gün
        if gun == 0 and saat == 0 and dakika == 0:
            gun = 14
        
        # Toplam dakikayı hesapla
        toplam_dakika = (gun * 24 * 60) + (saat * 60) + dakika
        
        # Süre mesajı oluştur
        sure_parcalari = []
        if gun > 0:
            sure_parcalari.append(f"{gun} gün")
        if saat > 0:
            sure_parcalari.append(f"{saat} saat")
        if dakika > 0:
            sure_parcalari.append(f"{dakika} dakika")
        sure_mesaj = " ".join(sure_parcalari) if sure_parcalari else "14 gün"
        
        # DATEADD ile dakika ekle
        query = """
            INSERT INTO OduncIslemleri (KitapID, KullaniciID, TeslimTarihi, Notlar)
            VALUES (?, ?, DATEADD(MINUTE, ?, GETDATE()), ?)
        """
        
        params = (
            int(odunc['kitap_id']),
            int(odunc['kullanici_id']),
            toplam_dakika,
            odunc.get('notlar')
        )
        
        # Süre mesajını odunc dict'e ekle
        odunc['_sure_mesaj'] = sure_mesaj
        
        return db.execute_insert_get_id(query, params)
    
    @staticmethod
    def return_book(odunc_id: int) -> int:
        """Kitap iade eder"""
        query = """
            UPDATE OduncIslemleri 
            SET Durum = 'iade', IadeTarihi = GETDATE()
            WHERE OduncID = ? AND Durum = 'odunc'
        """
        return db.execute_non_query(query, (odunc_id,))
    
    @staticmethod
    def check_book_available(kitap_id: int) -> bool:
        """Kitabın mevcut olup olmadığını kontrol eder"""
        query = "SELECT MevcutAdet FROM Kitaplar WHERE KitapID = ? AND Durum = 1"
        mevcut = db.execute_scalar(query, (kitap_id,))
        return mevcut is not None and mevcut > 0
    
    @staticmethod
    def count_user_active_borrows(kullanici_id: int) -> int:
        """Kullanıcının aktif ödünç sayısını döndürür"""
        query = "SELECT COUNT(*) FROM OduncIslemleri WHERE KullaniciID = ? AND Durum = 'odunc'"
        return db.execute_scalar(query, (kullanici_id,)) or 0


class CezaRepository:
    """Ceza Repository Sınıfı"""
    
    # Ceza oranları (Python tarafında hesaplama için)
    CEZA_DAKIKA_BASI = 0.50    # Dakika başına 0.50 TL (test için)
    CEZA_SAAT_BASI = 2.00      # Saat başına 2 TL (test için)
    CEZA_GUN_BASI = 5.00       # Gün başına 5 TL (normal)
    
    @staticmethod
    def get_all() -> List[dict]:
        """Tüm cezaları getirir"""
        query = """
            SELECT c.CezaID, c.OduncID, c.KullaniciID,
                   u.Ad + ' ' + u.Soyad AS KullaniciAdi,
                   k.KitapAdi,
                   c.GecikmeGunu, c.CezaTutari, c.OdenmeDurumu,
                   c.OlusturmaTarihi, c.OdemeTarihi
            FROM Cezalar c
            INNER JOIN Kullanicilar u ON c.KullaniciID = u.KullaniciID
            INNER JOIN OduncIslemleri o ON c.OduncID = o.OduncID
            INNER JOIN Kitaplar k ON o.KitapID = k.KitapID
            ORDER BY c.OlusturmaTarihi DESC
        """
        return db.execute_query(query)
    
    @staticmethod
    def get_by_id(ceza_id: int) -> Optional[dict]:
        """ID'ye göre ceza getirir"""
        query = """
            SELECT c.CezaID, c.OduncID, c.KullaniciID,
                   u.Ad + ' ' + u.Soyad AS KullaniciAdi,
                   k.KitapAdi,
                   c.GecikmeGunu, c.CezaTutari, c.OdenmeDurumu,
                   c.OlusturmaTarihi, c.OdemeTarihi
            FROM Cezalar c
            INNER JOIN Kullanicilar u ON c.KullaniciID = u.KullaniciID
            INNER JOIN OduncIslemleri o ON c.OduncID = o.OduncID
            INNER JOIN Kitaplar k ON o.KitapID = k.KitapID
            WHERE c.CezaID = ?
        """
        results = db.execute_query(query, (ceza_id,))
        return results[0] if results else None
    
    @staticmethod
    def create(odunc_id: int, kullanici_id: int, gecikme_dakika: int, ceza_tutari: float) -> int:
        """
        Yeni ceza kaydı oluşturur
        
        Args:
            odunc_id: İlgili ödünç ID
            kullanici_id: Kullanıcı ID
            gecikme_dakika: Toplam gecikme (dakika cinsinden)
            ceza_tutari: Hesaplanmış ceza tutarı
        """
        query = """
            INSERT INTO Cezalar (OduncID, KullaniciID, GecikmeGunu, CezaTutari, OdenmeDurumu)
            VALUES (?, ?, ?, ?, 0)
        """
        # GecikmeGunu alanına dakikayı da yazıyoruz (tablo yapısı gün bekliyor ama)
        # İsterseniz tabloyu da güncelleyebiliriz
        params = (odunc_id, kullanici_id, gecikme_dakika, ceza_tutari)
        return db.execute_insert_get_id(query, params)
    
    @staticmethod
    def check_exists_for_odunc(odunc_id: int) -> bool:
        """Bu ödünç için ceza var mı kontrol eder"""
        query = "SELECT COUNT(*) FROM Cezalar WHERE OduncID = ?"
        count = db.execute_scalar(query, (odunc_id,))
        return count > 0
    
    @staticmethod
    def get_by_user(kullanici_id: int) -> List[dict]:
        """Kullanıcının cezalarını getirir"""
        query = """
            SELECT c.CezaID, c.OduncID, k.KitapAdi,
                   c.GecikmeGunu, c.CezaTutari, c.OdenmeDurumu,
                   c.OlusturmaTarihi, c.OdemeTarihi
            FROM Cezalar c
            INNER JOIN OduncIslemleri o ON c.OduncID = o.OduncID
            INNER JOIN Kitaplar k ON o.KitapID = k.KitapID
            WHERE c.KullaniciID = ?
            ORDER BY c.OlusturmaTarihi DESC
        """
        return db.execute_query(query, (kullanici_id,))
    
    @staticmethod
    def get_unpaid_by_user(kullanici_id: int) -> List[dict]:
        """Kullanıcının ödenmemiş cezalarını getirir"""
        query = """
            SELECT c.CezaID, c.OduncID, k.KitapAdi,
                   c.GecikmeGunu, c.CezaTutari, c.OlusturmaTarihi
            FROM Cezalar c
            INNER JOIN OduncIslemleri o ON c.OduncID = o.OduncID
            INNER JOIN Kitaplar k ON o.KitapID = k.KitapID
            WHERE c.KullaniciID = ? AND c.OdenmeDurumu = 0
        """
        return db.execute_query(query, (kullanici_id,))
    
    @staticmethod
    def pay_penalty(ceza_id: int) -> int:
        """Cezayı ödenmiş olarak işaretler"""
        query = "UPDATE Cezalar SET OdenmeDurumu = 1, OdemeTarihi = GETDATE() WHERE CezaID = ?"
        return db.execute_non_query(query, (ceza_id,))
    
    @staticmethod
    def get_total_unpaid(kullanici_id: int) -> float:
        """Kullanıcının toplam ödenmemiş ceza tutarını döndürür"""
        query = "SELECT ISNULL(SUM(CezaTutari), 0) FROM Cezalar WHERE KullaniciID = ? AND OdenmeDurumu = 0"
        return db.execute_scalar(query, (kullanici_id,)) or 0.0


class IstatistikRepository:
    """İstatistik Repository Sınıfı"""
    
    @staticmethod
    def get_dashboard_stats() -> dict:
        """Dashboard istatistiklerini getirir"""
        results = db.execute_stored_procedure('sp_Istatistikler')
        return results[0] if results else {}
    
    @staticmethod
    def get_popular_books(limit: int = 10) -> List[dict]:
        """En çok ödünç alınan kitapları getirir"""
        query = """
            SELECT TOP (?) k.KitapID, k.KitapAdi, k.ISBN,
                   y.Ad + ' ' + y.Soyad AS YazarAdi,
                   COUNT(o.OduncID) AS OduncSayisi
            FROM Kitaplar k
            LEFT JOIN Yazarlar y ON k.YazarID = y.YazarID
            LEFT JOIN OduncIslemleri o ON k.KitapID = o.KitapID
            WHERE k.Durum = 1
            GROUP BY k.KitapID, k.KitapAdi, k.ISBN, y.Ad, y.Soyad
            ORDER BY OduncSayisi DESC
        """
        return db.execute_query(query, (limit,))
    
    @staticmethod
    def get_active_users(limit: int = 10) -> List[dict]:
        """En aktif kullanıcıları getirir"""
        query = """
            SELECT TOP (?) u.KullaniciID, u.Ad + ' ' + u.Soyad AS KullaniciAdi,
                   COUNT(o.OduncID) AS OduncSayisi
            FROM Kullanicilar u
            LEFT JOIN OduncIslemleri o ON u.KullaniciID = o.KullaniciID
            WHERE u.Durum = 1
            GROUP BY u.KullaniciID, u.Ad, u.Soyad
            ORDER BY OduncSayisi DESC
        """
        return db.execute_query(query, (limit,))
