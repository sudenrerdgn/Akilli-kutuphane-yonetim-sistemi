# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Kimlik Doğrulama Yardımcı Fonksiyonları
# ============================================

import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta

def hash_password(password: str) -> str:
    """Şifreyi hash'ler"""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Şifreyi doğrular"""
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def create_tokens(kullanici_id: int, email: str, rol: str) -> dict:
    """JWT Access ve Refresh token oluşturur"""
    identity = {
        'kullanici_id': kullanici_id,
        'email': email,
        'rol': rol
    }
    
    access_token = create_access_token(
        identity=kullanici_id,
        additional_claims=identity,
        expires_delta=timedelta(hours=24)
    )
    
    refresh_token = create_refresh_token(
        identity=kullanici_id,
        additional_claims=identity,
        expires_delta=timedelta(days=30)
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': 86400  # 24 saat (saniye)
    }

def require_role(*allowed_roles):
    """Rol tabanlı yetkilendirme decorator'ı"""
    from functools import wraps
    from flask import jsonify
    from flask_jwt_extended import get_jwt
    
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('rol', 'uye')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'hata': True,
                    'mesaj': 'Bu işlem için yetkiniz bulunmamaktadır.'
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator
