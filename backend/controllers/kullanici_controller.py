# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Kullanıcı Controller
# ============================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from services import KullaniciService

kullanici_bp = Blueprint('kullanicilar', __name__)


@kullanici_bp.route('', methods=['GET'])
@jwt_required()
def get_all():
    """Tüm Kullanıcıları Getir
    ---
    tags:
      - Kullanıcılar
    security:
      - Bearer: []
    responses:
      200:
        description: Kullanıcılar listesi
      403:
        description: Yetki yok
    """
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    kullanicilar = KullaniciService.get_all()
    return jsonify({
        'hata': False,
        'data': kullanicilar,
        'toplam': len(kullanicilar)
    }), 200


@kullanici_bp.route('/<int:kullanici_id>', methods=['GET'])
@jwt_required()
def get_by_id(kullanici_id):
    """ID'ye Göre Kullanıcı Getir
    ---
    tags:
      - Kullanıcılar
    security:
      - Bearer: []
    parameters:
      - name: kullanici_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Kullanıcı detayı
      404:
        description: Kullanıcı bulunamadı
    """
    kullanici = KullaniciService.get_by_id(kullanici_id)
    
    if kullanici:
        return jsonify({'hata': False, 'data': kullanici}), 200
    return jsonify({'hata': True, 'mesaj': 'Kullanıcı bulunamadı.'}), 404


@kullanici_bp.route('/<int:kullanici_id>', methods=['PUT'])
@jwt_required()
def update(kullanici_id):
    """Kullanıcı Güncelle
    ---
    tags:
      - Kullanıcılar
    security:
      - Bearer: []
    parameters:
      - name: kullanici_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            ad:
              type: string
              example: Ahmet
            soyad:
              type: string
              example: Yılmaz
            email:
              type: string
              example: ahmet@mail.com
            telefon:
              type: string
              example: "05551234567"
            rol:
              type: string
              enum: [admin, personel, uye]
              example: uye
    responses:
      200:
        description: Kullanıcı güncellendi
      400:
        description: Güncelleme hatası
      403:
        description: Yetki yok
    """
    claims = get_jwt()
    current_user_id = claims.get('sub')
    
    # Sadece admin başkalarını güncelleyebilir, kullanıcı kendini güncelleyebilir
    if claims.get('rol') != 'admin' and str(current_user_id) != str(kullanici_id):
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    data = request.get_json()
    
    # Rol değiştirme sadece admin yapabilir
    if 'rol' in data and claims.get('rol') != 'admin':
        return jsonify({'hata': True, 'mesaj': 'Rol değiştirme yetkisi yok.'}), 403
    
    success, message = KullaniciService.update(kullanici_id, data)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message}), 200
    return jsonify({'hata': True, 'mesaj': message}), 400


@kullanici_bp.route('/<int:kullanici_id>', methods=['DELETE'])
@jwt_required()
def delete(kullanici_id):
    """Kullanıcı Sil
    ---
    tags:
      - Kullanıcılar
    security:
      - Bearer: []
    parameters:
      - name: kullanici_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Kullanıcı silindi
      400:
        description: Silme hatası
      403:
        description: Admin yetkisi gerekli
    """
    claims = get_jwt()
    if claims.get('rol') != 'admin':
        return jsonify({'hata': True, 'mesaj': 'Admin yetkisi gerekli.'}), 403
    
    success, message = KullaniciService.delete(kullanici_id)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message}), 200
    return jsonify({'hata': True, 'mesaj': message}), 400
