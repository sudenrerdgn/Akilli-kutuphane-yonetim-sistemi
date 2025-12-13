# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Kategori Controller
# ============================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from services import KategoriService

kategori_bp = Blueprint('kategoriler', __name__)


@kategori_bp.route('', methods=['GET'])
def get_all():
    """Tüm Kategorileri Getir
    ---
    tags:
      - Kategoriler
    responses:
      200:
        description: Kategoriler listesi
    """
    kategoriler = KategoriService.get_all()
    return jsonify({
        'hata': False,
        'data': kategoriler,
        'toplam': len(kategoriler)
    }), 200


@kategori_bp.route('/<int:kategori_id>', methods=['GET'])
def get_by_id(kategori_id):
    """ID'ye Göre Kategori Getir
    ---
    tags:
      - Kategoriler
    parameters:
      - name: kategori_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Kategori detayı
      404:
        description: Kategori bulunamadı
    """
    kategori = KategoriService.get_by_id(kategori_id)
    
    if kategori:
        return jsonify({'hata': False, 'data': kategori}), 200
    return jsonify({'hata': True, 'mesaj': 'Kategori bulunamadı.'}), 404


@kategori_bp.route('', methods=['POST'])
@jwt_required()
def create():
    """Yeni Kategori Ekle
    ---
    tags:
      - Kategoriler
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - kategori_adi
          properties:
            kategori_adi:
              type: string
              example: Bilim Kurgu
            aciklama:
              type: string
              example: Bilim kurgu kitapları
    responses:
      201:
        description: Kategori eklendi
      400:
        description: Geçersiz veri
      403:
        description: Yetki yok
    """
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    data = request.get_json()
    
    if not data.get('kategori_adi'):
        return jsonify({'hata': True, 'mesaj': 'Kategori adı zorunludur.'}), 400
    
    success, message, kategori_id = KategoriService.create(data)
    
    if success:
        return jsonify({
            'hata': False,
            'mesaj': message,
            'data': {'kategori_id': kategori_id}
        }), 201
    return jsonify({'hata': True, 'mesaj': message}), 400


@kategori_bp.route('/<int:kategori_id>', methods=['PUT'])
@jwt_required()
def update(kategori_id):
    """Kategori Güncelle
    ---
    tags:
      - Kategoriler
    security:
      - Bearer: []
    parameters:
      - name: kategori_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            kategori_adi:
              type: string
            aciklama:
              type: string
    responses:
      200:
        description: Kategori güncellendi
      400:
        description: Güncelleme hatası
      403:
        description: Yetki yok
    """
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    data = request.get_json()
    success, message = KategoriService.update(kategori_id, data)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message}), 200
    return jsonify({'hata': True, 'mesaj': message}), 400


@kategori_bp.route('/<int:kategori_id>', methods=['DELETE'])
@jwt_required()
def delete(kategori_id):
    """Kategori Sil
    ---
    tags:
      - Kategoriler
    security:
      - Bearer: []
    parameters:
      - name: kategori_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Kategori silindi
      400:
        description: Silme hatası
      403:
        description: Admin yetkisi gerekli
    """
    claims = get_jwt()
    if claims.get('rol') != 'admin':
        return jsonify({'hata': True, 'mesaj': 'Admin yetkisi gerekli.'}), 403
    
    success, message = KategoriService.delete(kategori_id)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message}), 200
    return jsonify({'hata': True, 'mesaj': message}), 400
