# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Auth Controller
# ============================================
# DEĞİŞİKLİK: SQL INJECTION & XSS KORUMASI
# - register(): Input validation eklendi
# - login(): SQL injection kontrolü eklendi

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services import AuthService
from utils.security import SecurityHelper

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Yeni Kullanıcı Kaydı"""
    data = request.get_json()
    
    # Zorunlu alan kontrolü
    required_fields = ['ad', 'soyad', 'email', 'sifre']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'hata': True, 'mesaj': f'{field} alanı zorunludur.'}), 400
    
    # ==========================================
    # SQL INJECTION & XSS KORUMASI
    # ==========================================
    
    # Ad kontrolü
    if SecurityHelper.check_sql_injection(data['ad']) or SecurityHelper.check_xss(data['ad']):
        return jsonify({'hata': True, 'mesaj': 'Ad alanında geçersiz karakter!'}), 400
    if not SecurityHelper.validate_length(data['ad'], 2, 50):
        return jsonify({'hata': True, 'mesaj': 'Ad 2-50 karakter olmalı.'}), 400
    
    # Soyad kontrolü
    if SecurityHelper.check_sql_injection(data['soyad']) or SecurityHelper.check_xss(data['soyad']):
        return jsonify({'hata': True, 'mesaj': 'Soyad alanında geçersiz karakter!'}), 400
    if not SecurityHelper.validate_length(data['soyad'], 2, 50):
        return jsonify({'hata': True, 'mesaj': 'Soyad 2-50 karakter olmalı.'}), 400
    
    # Email kontrolü
    if SecurityHelper.check_sql_injection(data['email']):
        return jsonify({'hata': True, 'mesaj': 'Email alanında geçersiz karakter!'}), 400
    if not SecurityHelper.validate_email(data['email']):
        return jsonify({'hata': True, 'mesaj': 'Geçersiz email formatı.'}), 400
    
    # Şifre kontrolü
    if not SecurityHelper.validate_length(data['sifre'], 6, 100):
        return jsonify({'hata': True, 'mesaj': 'Şifre en az 6 karakter olmalı.'}), 400
    
    # Telefon kontrolü (opsiyonel)
    if data.get('telefon'):
        if SecurityHelper.check_sql_injection(data['telefon']):
            return jsonify({'hata': True, 'mesaj': 'Telefon alanında geçersiz karakter!'}), 400
        if not SecurityHelper.validate_phone(data['telefon']):
            return jsonify({'hata': True, 'mesaj': 'Geçersiz telefon formatı.'}), 400
    
    # Sanitize
    clean_data = {
        'ad': SecurityHelper.sanitize_string(data['ad']),
        'soyad': SecurityHelper.sanitize_string(data['soyad']),
        'email': SecurityHelper.sanitize_string(data['email']).lower(),
        'sifre': data['sifre'],
        'telefon': SecurityHelper.sanitize_string(data.get('telefon'))
    }
    
    # ==========================================
    
    success, message, kullanici = AuthService.register(clean_data)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message, 'data': kullanici}), 201
    return jsonify({'hata': True, 'mesaj': message}), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    """Kullanıcı Girişi"""
    data = request.get_json()
    
    email = data.get('email')
    sifre = data.get('sifre')
    
    if not email or not sifre:
        return jsonify({'hata': True, 'mesaj': 'Email ve şifre zorunludur.'}), 400
    
    # ==========================================
    # SQL INJECTION KORUMASI
    # ==========================================
    if SecurityHelper.check_sql_injection(email):
        return jsonify({'hata': True, 'mesaj': 'Geçersiz karakter tespit edildi!'}), 400
    
    if not SecurityHelper.validate_email(email):
        return jsonify({'hata': True, 'mesaj': 'Geçersiz email formatı.'}), 400
    
    clean_email = SecurityHelper.sanitize_string(email).lower()
    # ==========================================
    
    success, message, result = AuthService.login(clean_email, sifre)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message, 'data': result}), 200
    return jsonify({'hata': True, 'mesaj': message}), 401


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Mevcut Kullanıcı Bilgisi"""
    claims = get_jwt()
    return jsonify({
        'hata': False,
        'data': {
            'kullanici_id': claims.get('kullanici_id'),
            'email': claims.get('email'),
            'rol': claims.get('rol')
        }
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Şifre Değiştirme"""
    data = request.get_json()
    kullanici_id = get_jwt_identity()
    
    eski_sifre = data.get('eski_sifre')
    yeni_sifre = data.get('yeni_sifre')
    
    if not eski_sifre or not yeni_sifre:
        return jsonify({'hata': True, 'mesaj': 'Eski ve yeni şifre zorunludur.'}), 400
    
    # Şifre uzunluk kontrolü
    if not SecurityHelper.validate_length(yeni_sifre, 6, 100):
        return jsonify({'hata': True, 'mesaj': 'Yeni şifre en az 6 karakter olmalı.'}), 400
    
    success, message = AuthService.change_password(kullanici_id, eski_sifre, yeni_sifre)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message}), 200
    return jsonify({'hata': True, 'mesaj': message}), 400
