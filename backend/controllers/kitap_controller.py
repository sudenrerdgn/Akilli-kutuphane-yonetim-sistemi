# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Kitap Controller
# ============================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from services import KitapService

kitap_bp = Blueprint('kitaplar', __name__)


@kitap_bp.route('', methods=['GET'])
def get_all():
    """
    Tüm Kitapları Getir
    ---
    tags:
      - Kitaplar
    responses:
      200:
        description: Kitap listesi
    """
    kitaplar = KitapService.get_all()
    return jsonify({
        'hata': False,
        'data': kitaplar,
        'toplam': len(kitaplar)
    }), 200


@kitap_bp.route('/<int:kitap_id>', methods=['GET'])
def get_by_id(kitap_id):
    """
    ID'ye Göre Kitap Getir
    ---
    tags:
      - Kitaplar
    parameters:
      - name: kitap_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Kitap detayı
      404:
        description: Kitap bulunamadı
    """
    kitap = KitapService.get_by_id(kitap_id)
    
    if kitap:
        return jsonify({
            'hata': False,
            'data': kitap
        }), 200
    
    return jsonify({
        'hata': True,
        'mesaj': 'Kitap bulunamadı.'
    }), 404


@kitap_bp.route('/ara', methods=['GET'])
def search():
    """
    Kitap Ara
    ---
    tags:
      - Kitaplar
    parameters:
      - name: q
        in: query
        type: string
        description: Arama metni (kitap adı veya ISBN)
      - name: kategori_id
        in: query
        type: integer
      - name: yazar_id
        in: query
        type: integer
      - name: sadece_mevcut
        in: query
        type: boolean
    responses:
      200:
        description: Arama sonuçları
    """
    arama = request.args.get('q')
    kategori_id = request.args.get('kategori_id', type=int)
    yazar_id = request.args.get('yazar_id', type=int)
    sadece_mevcut = request.args.get('sadece_mevcut', 'false').lower() == 'true'
    
    sonuclar = KitapService.search(arama, kategori_id, yazar_id, sadece_mevcut)
    
    return jsonify({
        'hata': False,
        'data': sonuclar,
        'toplam': len(sonuclar)
    }), 200


@kitap_bp.route('', methods=['POST'])
@jwt_required()
def create():
    """
    Yeni Kitap Ekle
    ---
    tags:
      - Kitaplar
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - isbn
            - kitap_adi
          properties:
            isbn:
              type: string
              example: "9789750718533"
            kitap_adi:
              type: string
              example: "Yeni Kitap"
            yazar_id:
              type: integer
            kategori_id:
              type: integer
            yayin_yili:
              type: integer
            yayin_evi:
              type: string
            sayfa_sayisi:
              type: integer
            dil:
              type: string
              default: "Türkçe"
            aciklama:
              type: string
            toplam_adet:
              type: integer
              default: 1
            mevcut_adet:
              type: integer
              default: 1
    responses:
      201:
        description: Kitap eklendi
      400:
        description: Hata
      403:
        description: Yetki hatası
    """
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({
            'hata': True,
            'mesaj': 'Bu işlem için yetkiniz yok.'
        }), 403
    
    data = request.get_json()
    
    if not data.get('isbn') or not data.get('kitap_adi'):
        return jsonify({
            'hata': True,
            'mesaj': 'ISBN ve kitap adı zorunludur.'
        }), 400
    
    success, message, kitap_id = KitapService.create(data)
    
    if success:
        return jsonify({
            'hata': False,
            'mesaj': message,
            'data': {'kitap_id': kitap_id}
        }), 201
    
    return jsonify({
        'hata': True,
        'mesaj': message
    }), 400


@kitap_bp.route('/<int:kitap_id>', methods=['PUT'])
@jwt_required()
def update(kitap_id):
    """
    Kitap Güncelle
    ---
    tags:
      - Kitaplar
    security:
      - Bearer: []
    parameters:
      - name: kitap_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            isbn:
              type: string
            kitap_adi:
              type: string
            yazar_id:
              type: integer
            kategori_id:
              type: integer
    responses:
      200:
        description: Kitap güncellendi
      400:
        description: Hata
      403:
        description: Yetki hatası
    """
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({
            'hata': True,
            'mesaj': 'Bu işlem için yetkiniz yok.'
        }), 403
    
    data = request.get_json()
    success, message = KitapService.update(kitap_id, data)
    
    if success:
        return jsonify({
            'hata': False,
            'mesaj': message
        }), 200
    
    return jsonify({
        'hata': True,
        'mesaj': message
    }), 400


@kitap_bp.route('/<int:kitap_id>', methods=['DELETE'])
@jwt_required()
def delete(kitap_id):
    """
    Kitap Sil
    ---
    tags:
      - Kitaplar
    security:
      - Bearer: []
    parameters:
      - name: kitap_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Kitap silindi
      400:
        description: Hata
      403:
        description: Yetki hatası
    """
    claims = get_jwt()
    if claims.get('rol') != 'admin':
        return jsonify({
            'hata': True,
            'mesaj': 'Bu işlem için admin yetkisi gereklidir.'
        }), 403
    
    success, message = KitapService.delete(kitap_id)
    
    if success:
        return jsonify({
            'hata': False,
            'mesaj': message
        }), 200
    
    return jsonify({
        'hata': True,
        'mesaj': message
    }), 400
