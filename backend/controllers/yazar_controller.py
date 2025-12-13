# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Yazar Controller
# ============================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from services import YazarService

yazar_bp = Blueprint('yazarlar', __name__)


@yazar_bp.route('', methods=['GET'])
def get_all():
    """Tüm Yazarları Getir
    ---
    tags:
      - Yazarlar
    responses:
      200:
        description: Yazarlar listesi
    """
    yazarlar = YazarService.get_all()
    return jsonify({
        'hata': False,
        'data': yazarlar,
        'toplam': len(yazarlar)
    }), 200


@yazar_bp.route('/<int:yazar_id>', methods=['GET'])
def get_by_id(yazar_id):
    """ID'ye Göre Yazar Getir
    ---
    tags:
      - Yazarlar
    parameters:
      - name: yazar_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Yazar detayı
      404:
        description: Yazar bulunamadı
    """
    yazar = YazarService.get_by_id(yazar_id)
    
    if yazar:
        return jsonify({'hata': False, 'data': yazar}), 200
    return jsonify({'hata': True, 'mesaj': 'Yazar bulunamadı.'}), 404


@yazar_bp.route('', methods=['POST'])
@jwt_required()
def create():
    """Yeni Yazar Ekle
    ---
    tags:
      - Yazarlar
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - ad
            - soyad
          properties:
            ad:
              type: string
              example: Orhan
            soyad:
              type: string
              example: Pamuk
            biyografi:
              type: string
              example: Nobel ödüllü yazar
            ulke:
              type: string
              example: Türkiye
    responses:
      201:
        description: Yazar eklendi
      400:
        description: Geçersiz veri
      403:
        description: Yetki yok
    """
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    data = request.get_json()
    
    if not data.get('ad') or not data.get('soyad'):
        return jsonify({'hata': True, 'mesaj': 'Ad ve soyad zorunludur.'}), 400
    
    success, message, yazar_id = YazarService.create(data)
    
    if success:
        return jsonify({
            'hata': False,
            'mesaj': message,
            'data': {'yazar_id': yazar_id}
        }), 201
    return jsonify({'hata': True, 'mesaj': message}), 400


@yazar_bp.route('/<int:yazar_id>', methods=['PUT'])
@jwt_required()
def update(yazar_id):
    """Yazar Güncelle
    ---
    tags:
      - Yazarlar
    security:
      - Bearer: []
    parameters:
      - name: yazar_id
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
            soyad:
              type: string
            biyografi:
              type: string
            ulke:
              type: string
    responses:
      200:
        description: Yazar güncellendi
      400:
        description: Güncelleme hatası
      403:
        description: Yetki yok
    """
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    data = request.get_json()
    success, message = YazarService.update(yazar_id, data)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message}), 200
    return jsonify({'hata': True, 'mesaj': message}), 400


@yazar_bp.route('/<int:yazar_id>', methods=['DELETE'])
@jwt_required()
def delete(yazar_id):
    """Yazar Sil
    ---
    tags:
      - Yazarlar
    security:
      - Bearer: []
    parameters:
      - name: yazar_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Yazar silindi
      400:
        description: Silme hatası
      403:
        description: Admin yetkisi gerekli
    """
    claims = get_jwt()
    if claims.get('rol') != 'admin':
        return jsonify({'hata': True, 'mesaj': 'Admin yetkisi gerekli.'}), 403
    
    success, message = YazarService.delete(yazar_id)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message}), 200
    return jsonify({'hata': True, 'mesaj': message}), 400
