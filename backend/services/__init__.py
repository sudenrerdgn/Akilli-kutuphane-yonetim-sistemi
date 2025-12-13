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
        try:
            print(f"YAZAR DATA: {data}")
            yazar_id = YazarRepository.create(data)
            print(f"YAZAR ID: {yazar_id}")
            if yazar_id:
                return True, "Yazar eklendi.", yazar_id
            return False, "Yazar eklenirken hata oluştu.", None
        except Exception as e:
            print(f"YAZAR HATASI: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Hata: {str(e)}", None
    
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
    """Ödünç İşlemleri Servisi"""
    
    @staticmethod
    def get_all() -> List[dict]:
        return OduncRepository.get_all()
    
    @staticmethod
    def get_by_id(odunc_id: int) -> Optional[dict]:
        return OduncRepository.get_by_id(odunc_id)
    
    @staticmethod
    def get_by_kullanici(kullanici_id: int) -> List[dict]:
        return OduncRepository.get_by_user(kullanici_id)
    
    @staticmethod
    def get_aktif_by_kullanici(kullanici_id: int) -> List[dict]:
        return OduncRepository.get_active_by_user(kullanici_id)
    
    @staticmethod
    def get_geciken() -> List[dict]:
        return OduncRepository.get_overdue()
    
    @staticmethod
    def odunc_al(kullanici_id: int, kitap_id: int, gun: int = 14):
        try:
            # Kitap mevcut mu kontrol et
            if not OduncRepository.check_book_available(kitap_id):
                return False, "Kitap mevcut değil veya stokta yok."
            
            # Kullanıcının aktif ödünç sayısını kontrol et
            aktif_sayi = OduncRepository.count_user_active_borrows(kullanici_id)
            if aktif_sayi >= 5:
                return False, "En fazla 5 kitap ödünç alabilirsiniz."
            
            # Ödünç kaydı oluştur
            odunc_data = {
                'kitap_id': kitap_id,
                'kullanici_id': kullanici_id,
                'odunc_gun': gun
            }
            odunc_id = OduncRepository.create(odunc_data)
            
            if odunc_id:
                return True, "Kitap başarıyla ödünç alındı."
            return False, "Ödünç alma işlemi başarısız."
        except Exception as e:
            print(f"ÖDÜNÇ ALMA HATASI: {e}")
            return False, f"Hata: {str(e)}"
    
    @staticmethod
    def iade_et(odunc_id: int):
        try:
            odunc = OduncRepository.get_by_id(odunc_id)
            if not odunc:
                return False, "Ödünç kaydı bulunamadı.", None
            
            if odunc.get('Durum') == 'iade':
                return False, "Bu kitap zaten iade edilmiş.", None
            
            OduncRepository.return_book(odunc_id)
            return True, "Kitap başarıyla iade edildi.", 0
        except Exception as e:
            print(f"İADE HATASI: {e}")
            return False, f"Hata: {str(e)}", None


class CezaService:
    """Ceza Servisi"""
    
    @staticmethod
    def get_all() -> List[dict]:
        return CezaRepository.get_all()
    
    @staticmethod
    def get_by_id(ceza_id: int) -> Optional[dict]:
        return CezaRepository.get_by_id(ceza_id)
    
    @staticmethod
    def get_by_kullanici(kullanici_id: int) -> List[dict]:
        return CezaRepository.get_by_user(kullanici_id)
    
    @staticmethod
    def get_unpaid_by_kullanici(kullanici_id: int) -> List[dict]:
        return CezaRepository.get_unpaid_by_user(kullanici_id)
    
    @staticmethod
    def pay(ceza_id: int):
        try:
            ceza = CezaRepository.get_by_id(ceza_id)
            if not ceza:
                return False, "Ceza bulunamadı."
            
            if ceza.get('OdenmeDurumu'):
                return False, "Bu ceza zaten ödenmiş."
            
            CezaRepository.pay_penalty(ceza_id)
            return True, "Ceza başarıyla ödendi."
        except Exception as e:
            print(f"CEZA ÖDEME HATASI: {e}")
            return False, f"Hata: {str(e)}"


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
