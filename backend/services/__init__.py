# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Service Katmanı
# ============================================

from repositories import (
    KullaniciRepository, KitapRepository, YazarRepository,
    KategoriRepository, OduncRepository, CezaRepository, IstatistikRepository
)
from utils.auth_helper import hash_password, verify_password, create_tokens
from utils.email_service import EmailService
from typing import Tuple, Optional, List
from datetime import datetime


class AuthService:
    """Kimlik Doğrulama Servisi"""
    
    @staticmethod
    def register(data: dict) -> Tuple[bool, str, Optional[dict]]:
        """Yeni kullanıcı kaydı"""
        # Email kontrolü
        if KullaniciRepository.check_email_exists(data['email']):
            return False, "Bu e-posta adresi zaten kayıtlı.", None
        
        # Şifre hash'le
        data['sifre'] = hash_password(data['sifre'])
        
        # Kullanıcı oluştur
        kullanici_id = KullaniciRepository.create(data)
        
        if kullanici_id:
            # Hoş geldiniz e-postası
            EmailService.send_welcome_email(data['email'], f"{data['ad']} {data['soyad']}")
            
            kullanici = KullaniciRepository.get_by_id(kullanici_id)
            return True, "Kayıt başarılı.", kullanici
        
        return False, "Kayıt sırasında bir hata oluştu.", None
    
    @staticmethod
    def login(email: str, sifre: str) -> Tuple[bool, str, Optional[dict]]:
        """Kullanıcı girişi"""
        kullanici = KullaniciRepository.get_by_email(email)
        
        if not kullanici:
            return False, "E-posta veya şifre hatalı.", None
        
        if not verify_password(sifre, kullanici['Sifre']):
            return False, "E-posta veya şifre hatalı.", None
        
        # Son giriş tarihini güncelle
        KullaniciRepository.update_last_login(kullanici['KullaniciID'])
        
        # Token oluştur
        tokens = create_tokens(
            kullanici['KullaniciID'],
            kullanici['Email'],
            kullanici['Rol']
        )
        
        return True, "Giriş başarılı.", {
            'kullanici': {
                'kullanici_id': kullanici['KullaniciID'],
                'ad': kullanici['Ad'],
                'soyad': kullanici['Soyad'],
                'email': kullanici['Email'],
                'rol': kullanici['Rol']
            },
            'tokens': tokens
        }
    
    @staticmethod
    def change_password(kullanici_id: int, eski_sifre: str, yeni_sifre: str) -> Tuple[bool, str]:
        """Şifre değiştirme"""
        kullanici = KullaniciRepository.get_by_id(kullanici_id)
        if not kullanici:
            return False, "Kullanıcı bulunamadı."
        
        # Eski şifre kontrolü
        full_user = KullaniciRepository.get_by_email(kullanici['Email'])
        if not verify_password(eski_sifre, full_user['Sifre']):
            return False, "Mevcut şifre hatalı."
        
        # Yeni şifre hash'le ve güncelle
        hashed = hash_password(yeni_sifre)
        KullaniciRepository.update_password(kullanici_id, hashed)
        
        return True, "Şifre başarıyla değiştirildi."


class KullaniciService:
    """Kullanıcı Servisi"""
    
    @staticmethod
    def get_all() -> List[dict]:
        """Tüm kullanıcıları getirir"""
        return KullaniciRepository.get_all()
    
    @staticmethod
    def get_by_id(kullanici_id: int) -> Optional[dict]:
        """ID'ye göre kullanıcı getirir"""
        return KullaniciRepository.get_by_id(kullanici_id)
    
    @staticmethod
    def update(kullanici_id: int, data: dict) -> Tuple[bool, str]:
        """Kullanıcı günceller"""
        # Mevcut kullanıcı kontrolü
        if not KullaniciRepository.get_by_id(kullanici_id):
            return False, "Kullanıcı bulunamadı."
        
        # Email kontrolü (başka kullanıcıda var mı)
        if KullaniciRepository.check_email_exists(data['email'], kullanici_id):
            return False, "Bu e-posta adresi başka bir kullanıcıya ait."
        
        KullaniciRepository.update(kullanici_id, data)
        return True, "Kullanıcı güncellendi."
    
    @staticmethod
    def delete(kullanici_id: int) -> Tuple[bool, str]:
        """Kullanıcı siler"""
        if not KullaniciRepository.get_by_id(kullanici_id):
            return False, "Kullanıcı bulunamadı."
        
        # Aktif ödünç kontrolü
        aktif_odunc = OduncRepository.count_user_active_borrows(kullanici_id)
        if aktif_odunc > 0:
            return False, f"Kullanıcının {aktif_odunc} adet aktif ödüncü bulunmaktadır."
        
        KullaniciRepository.delete(kullanici_id)
        return True, "Kullanıcı silindi."


class KitapService:
    """Kitap Servisi"""
    
    @staticmethod
    def get_all() -> List[dict]:
        """Tüm kitapları getirir"""
        return KitapRepository.get_all()
    
    @staticmethod
    def get_by_id(kitap_id: int) -> Optional[dict]:
        """ID'ye göre kitap getirir"""
        return KitapRepository.get_by_id(kitap_id)
    
    @staticmethod
    def search(arama: str = None, kategori_id: int = None,
               yazar_id: int = None, sadece_mevcut: bool = False) -> List[dict]:
        """Kitap arar"""
        return KitapRepository.search(arama, kategori_id, yazar_id, sadece_mevcut)
    
    @staticmethod
    def create(data: dict) -> Tuple[bool, str, Optional[int]]:
        """Yeni kitap oluşturur"""
        # ISBN kontrolü
        if KitapRepository.check_isbn_exists(data['isbn']):
            return False, "Bu ISBN numarası zaten kayıtlı.", None
        
        kitap_id = KitapRepository.create(data)
        if kitap_id:
            return True, "Kitap başarıyla eklendi.", kitap_id
        return False, "Kitap eklenirken hata oluştu.", None
    
    @staticmethod
    def update(kitap_id: int, data: dict) -> Tuple[bool, str]:
        """Kitap günceller"""
        if not KitapRepository.get_by_id(kitap_id):
            return False, "Kitap bulunamadı."
        
        # ISBN kontrolü
        if KitapRepository.check_isbn_exists(data['isbn'], kitap_id):
            return False, "Bu ISBN numarası başka bir kitaba ait."
        
        KitapRepository.update(kitap_id, data)
        return True, "Kitap güncellendi."
    
    @staticmethod
    def delete(kitap_id: int) -> Tuple[bool, str]:
        """Kitap siler"""
        if not KitapRepository.get_by_id(kitap_id):
            return False, "Kitap bulunamadı."
        
        KitapRepository.delete(kitap_id)
        return True, "Kitap silindi."


class YazarService:
    """Yazar Servisi"""
    
    @staticmethod
    def get_all() -> List[dict]:
        return YazarRepository.get_all()
    
    @staticmethod
    def get_by_id(yazar_id: int) -> Optional[dict]:
        return YazarRepository.get_by_id(yazar_id)
    
    @staticmethod
    def create(data: dict) -> Tuple[bool, str, Optional[int]]:
        yazar_id = YazarRepository.create(data)
        if yazar_id:
            return True, "Yazar eklendi.", yazar_id
        return False, "Yazar eklenirken hata oluştu.", None
    
    @staticmethod
    def update(yazar_id: int, data: dict) -> Tuple[bool, str]:
        if not YazarRepository.get_by_id(yazar_id):
            return False, "Yazar bulunamadı."
        YazarRepository.update(yazar_id, data)
        return True, "Yazar güncellendi."
    
    @staticmethod
    def delete(yazar_id: int) -> Tuple[bool, str]:
        if not YazarRepository.get_by_id(yazar_id):
            return False, "Yazar bulunamadı."
        try:
            YazarRepository.delete(yazar_id)
            return True, "Yazar silindi."
        except:
            return False, "Bu yazara ait kitaplar bulunduğu için silinemez."


class KategoriService:
    """Kategori Servisi"""
    
    @staticmethod
    def get_all() -> List[dict]:
        return KategoriRepository.get_all()
    
    @staticmethod
    def get_by_id(kategori_id: int) -> Optional[dict]:
        return KategoriRepository.get_by_id(kategori_id)
    
    @staticmethod
    def create(data: dict) -> Tuple[bool, str, Optional[int]]:
        kategori_id = KategoriRepository.create(data)
        if kategori_id:
            return True, "Kategori eklendi.", kategori_id
        return False, "Kategori eklenirken hata oluştu.", None
    
    @staticmethod
    def update(kategori_id: int, data: dict) -> Tuple[bool, str]:
        if not KategoriRepository.get_by_id(kategori_id):
            return False, "Kategori bulunamadı."
        KategoriRepository.update(kategori_id, data)
        return True, "Kategori güncellendi."
    
    @staticmethod
    def delete(kategori_id: int) -> Tuple[bool, str]:
        if not KategoriRepository.get_by_id(kategori_id):
            return False, "Kategori bulunamadı."
        try:
            KategoriRepository.delete(kategori_id)
            return True, "Kategori silindi."
        except:
            return False, "Bu kategoriye ait kitaplar bulunduğu için silinemez."


class OduncService:
    """Ödünç İşlemi Servisi"""
    
    MAX_BORROW_LIMIT = 5
    DEFAULT_BORROW_DAYS = 14
    
    # Ceza oranı - DAKİKA BAŞINA SABİT
    CEZA_DAKIKA_BASI = 0.10    # Her dakika 0.10 TL
    
    @staticmethod
    def get_all() -> List[dict]:
        return OduncRepository.get_all()
    
    @staticmethod
    def get_by_id(odunc_id: int) -> Optional[dict]:
        return OduncRepository.get_by_id(odunc_id)
    
    @staticmethod
    def get_by_kullanici(kullanici_id: int) -> List[dict]:
        """Kullanıcının ödünç geçmişini getirir"""
        return OduncRepository.get_by_user(kullanici_id)
    
    @staticmethod
    def get_aktif_by_kullanici(kullanici_id: int) -> List[dict]:
        """Kullanıcının aktif ödünçlerini getirir"""
        return OduncRepository.get_active_by_user(kullanici_id)
    
    @staticmethod
    def get_geciken() -> List[dict]:
        """Geciken kitapları getirir"""
        return OduncRepository.get_overdue()
    
    @staticmethod
    def odunc_al(kullanici_id: int, kitap_id: int, gun: int = 0, 
                 saat: int = 0, dakika: int = 0) -> Tuple[bool, str]:
        """
        Kitap ödünç alma
        
        Args:
            kullanici_id: Ödünç alan kullanıcı
            kitap_id: Ödünç alınacak kitap
            gun: Gün sayısı
            saat: Saat sayısı
            dakika: Dakika sayısı
            
        Toplam süre = (gün × 24 × 60) + (saat × 60) + dakika
        """
        # Kitap mevcut mu?
        if not OduncRepository.check_book_available(kitap_id):
            return False, "Kitap stokta mevcut değil."
        
        # Kullanıcı limit kontrolü
        aktif_odunc = OduncRepository.count_user_active_borrows(kullanici_id)
        if aktif_odunc >= OduncService.MAX_BORROW_LIMIT:
            return False, f"Maksimum ödünç limitine ({OduncService.MAX_BORROW_LIMIT}) ulaştınız."
        
        # Ödenmemiş ceza kontrolü
        odenmemis_ceza = CezaRepository.get_total_unpaid(kullanici_id)
        if odenmemis_ceza > 0:
            return False, f"Ödenmemiş {odenmemis_ceza:.2f} TL cezanız bulunmaktadır."
        
        # Ödünç verisi hazırla
        odunc_data = {
            'kitap_id': kitap_id,
            'kullanici_id': kullanici_id,
            'odunc_gun': gun or 0,
            'odunc_saat': saat or 0,
            'odunc_dakika': dakika or 0
        }
        
        # Ödünç işlemi
        odunc_id = OduncRepository.create(odunc_data)
        if odunc_id:
            sure_mesaj = odunc_data.get('_sure_mesaj', '14 gün')
            return True, f"Kitap {sure_mesaj} süreyle ödünç alındı."
        return False, "Ödünç işlemi sırasında hata oluştu."
    
    @staticmethod
    def iade_et(odunc_id: int) -> Tuple[bool, str, Optional[float]]:
        """
        Kitap iade et ve ceza hesapla
        
        Ceza = Gecikme dakikası × 0.10 TL
        
        Returns:
            Tuple[bool, str, Optional[float]]: (başarı, mesaj, ceza_tutarı)
        """
        odunc = OduncRepository.get_by_id(odunc_id)
        if not odunc:
            return False, "Ödünç kaydı bulunamadı.", None
        
        if odunc['Durum'] == 'iade':
            return False, "Bu kitap zaten iade edilmiş.", None
        
        # İade işlemi
        result = OduncRepository.return_book(odunc_id)
        if not result:
            return False, "İade işlemi sırasında hata oluştu.", None
        
        # Gecikme hesapla (dakika bazında)
        teslim_tarihi = odunc['TeslimTarihi']
        simdi = datetime.now()
        
        if simdi > teslim_tarihi:
            # Gecikme var!
            fark = simdi - teslim_tarihi
            gecikme_dakika = int(fark.total_seconds() / 60)  # Toplam dakika
            
            # Ceza hesapla - SABİT 0.10 TL / dakika
            ceza_tutari = gecikme_dakika * OduncService.CEZA_DAKIKA_BASI
            ceza_tutari = round(ceza_tutari, 2)
            
            # Gecikme mesajı oluştur
            gun = gecikme_dakika // (24 * 60)
            kalan = gecikme_dakika % (24 * 60)
            saat = kalan // 60
            dk = kalan % 60
            
            gecikme_parcalari = []
            if gun > 0:
                gecikme_parcalari.append(f"{gun} gün")
            if saat > 0:
                gecikme_parcalari.append(f"{saat} saat")
            if dk > 0 or (gun == 0 and saat == 0):
                gecikme_parcalari.append(f"{dk} dakika")
            gecikme_mesaj = " ".join(gecikme_parcalari)
            
            # Trigger zaten ceza oluşturmuş olabilir, kontrol et
            if not CezaRepository.check_exists_for_odunc(odunc_id):
                CezaRepository.create(
                    odunc_id=odunc_id,
                    kullanici_id=odunc['KullaniciID'],
                    gecikme_dakika=gecikme_dakika,
                    ceza_tutari=ceza_tutari
                )
            
            return True, f"Kitap iade edildi. {gecikme_mesaj} gecikme - {ceza_tutari:.2f} TL ceza oluşturuldu.", ceza_tutari
        
        return True, "Kitap zamanında iade edildi.", None


class CezaService:
    """Ceza Servisi"""
    
    @staticmethod
    def get_all() -> List[dict]:
        return CezaRepository.get_all()
    
    @staticmethod
    def get_by_id(ceza_id: int) -> Optional[dict]:
        """ID'ye göre ceza getirir"""
        return CezaRepository.get_by_id(ceza_id)
    
    @staticmethod
    def get_by_kullanici(kullanici_id: int) -> List[dict]:
        """Kullanıcının cezalarını getirir"""
        return CezaRepository.get_by_user(kullanici_id)
    
    @staticmethod
    def get_unpaid_by_kullanici(kullanici_id: int) -> List[dict]:
        """Kullanıcının ödenmemiş cezalarını getirir"""
        return CezaRepository.get_unpaid_by_user(kullanici_id)
    
    @staticmethod
    def pay(ceza_id: int) -> Tuple[bool, str]:
        """Ceza öder"""
        result = CezaRepository.pay_penalty(ceza_id)
        if result:
            return True, "Ceza ödendi."
        return False, "Ceza ödenirken hata oluştu."
    
    @staticmethod
    def get_user_total_unpaid(kullanici_id: int) -> float:
        """Kullanıcının toplam ödenmemiş ceza tutarını döndürür"""
        return CezaRepository.get_total_unpaid(kullanici_id)


class IstatistikService:
    """İstatistik Servisi"""
    
    @staticmethod
    def get_dashboard() -> dict:
        return IstatistikRepository.get_dashboard_stats()
    
    @staticmethod
    def get_popular_books(limit: int = 10) -> List[dict]:
        return IstatistikRepository.get_popular_books(limit)
    
    @staticmethod
    def get_active_users(limit: int = 10) -> List[dict]:
        return IstatistikRepository.get_active_users(limit)
