# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Auth Controller
# ============================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services import AuthService
from flasgger import swag_from

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Yeni Kullanıcı Kaydı
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - ad
            - soyad
            - email
            - sifre
          properties:
            ad:
              type: string
              example: "Ahmet"
            soyad:
              type: string
              example: "Yılmaz"
            email:
              type: string
              example: "ahmet@mail.com"
            sifre:
              type: string
              example: "sifre123"
            telefon:
              type: string
              example: "05551234567"
    responses:
      201:
        description: Kayıt başarılı
      400:
        description: Geçersiz veri
    """
    data = request.get_json()
    
    # Zorunlu alan kontrolü
    required_fields = ['ad', 'soyad', 'email', 'sifre']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'hata': True,
                'mesaj': f'{field} alanı zorunludur.'
            }), 400
    
    success, message, kullanici = AuthService.register(data)
    
    if success:
        return jsonify({
            'hata': False,
            'mesaj': message,
            'data': kullanici
        }), 201
    
    return jsonify({
        'hata': True,
        'mesaj': message
    }), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Kullanıcı Girişi
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - sifre
          properties:
            email:
              type: string
              example: "admin@kutuphane.com"
            sifre:
              type: string
              example: "Admin123!"
    responses:
      200:
        description: Giriş başarılı
      401:
        description: Yetkilendirme hatası
    """
    data = request.get_json()
    
    email = data.get('email')
    sifre = data.get('sifre')
    
    if not email or not sifre:
        return jsonify({
            'hata': True,
            'mesaj': 'E-posta ve şifre zorunludur.'
        }), 400
    
    success, message, result = AuthService.login(email, sifre)
    
    if success:
        return jsonify({
            'hata': False,
            'mesaj': message,
            'data': result
        }), 200
    
    return jsonify({
        'hata': True,
        'mesaj': message
    }), 401


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Mevcut Kullanıcı Bilgisi
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: Kullanıcı bilgisi
      401:
        description: Yetkilendirme gerekli
    """
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
    """
    Şifre Değiştirme
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - eski_sifre
            - yeni_sifre
          properties:
            eski_sifre:
              type: string
            yeni_sifre:
              type: string
    responses:
      200:
        description: Şifre değiştirildi
      400:
        description: Hata
    """
    data = request.get_json()
    kullanici_id = get_jwt_identity()
    
    eski_sifre = data.get('eski_sifre')
    yeni_sifre = data.get('yeni_sifre')
    
    if not eski_sifre or not yeni_sifre:
        return jsonify({
            'hata': True,
            'mesaj': 'Eski ve yeni şifre zorunludur.'
        }), 400
    
    success, message = AuthService.change_password(kullanici_id, eski_sifre, yeni_sifre)
    
    if success:
        return jsonify({
            'hata': False,
            'mesaj': message
        }), 200
    
    return jsonify({
        'hata': True,
        'mesaj': message
    }), 400
