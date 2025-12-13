# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Ceza Controller
# ============================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from services import CezaService

ceza_bp = Blueprint('cezalar', __name__)


@ceza_bp.route('', methods=['GET'])
@jwt_required()
def get_all():
    """Tüm Cezaları Getir
    ---
    tags:
      - Cezalar
    security:
      - Bearer: []
    responses:
      200:
        description: Cezalar listesi
      403:
        description: Yetki yok
    """
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    cezalar = CezaService.get_all()
    return jsonify({
        'hata': False,
        'data': cezalar,
        'toplam': len(cezalar)
    }), 200


@ceza_bp.route('/benim', methods=['GET'])
@jwt_required()
def get_my_penalties():
    """Kendi Cezalarımı Getir
    ---
    tags:
      - Cezalar
    security:
      - Bearer: []
    responses:
      200:
        description: Kullanıcının cezaları
    """
    kullanici_id = get_jwt_identity()
    cezalar = CezaService.get_by_kullanici(kullanici_id)
    return jsonify({
        'hata': False,
        'data': cezalar,
        'toplam': len(cezalar)
    }), 200


@ceza_bp.route('/odenmemis', methods=['GET'])
@jwt_required()
def get_unpaid():
    """Ödenmemiş Cezalarımı Getir
    ---
    tags:
      - Cezalar
    security:
      - Bearer: []
    responses:
      200:
        description: Ödenmemiş cezalar listesi
    """
    kullanici_id = get_jwt_identity()
    cezalar = CezaService.get_unpaid_by_kullanici(kullanici_id)
    
    toplam_borc = sum(c.get('CezaTutari', 0) for c in cezalar)
    
    return jsonify({
        'hata': False,
        'data': cezalar,
        'toplam_ceza': len(cezalar),
        'toplam_borc': toplam_borc
    }), 200


@ceza_bp.route('/kullanici/<int:kullanici_id>', methods=['GET'])
@jwt_required()
def get_by_kullanici(kullanici_id):
    """Kullanıcının Cezalarını Getir
    ---
    tags:
      - Cezalar
    security:
      - Bearer: []
    parameters:
      - name: kullanici_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Kullanıcının cezaları
      403:
        description: Yetki yok
    """
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    cezalar = CezaService.get_by_kullanici(kullanici_id)
    return jsonify({
        'hata': False,
        'data': cezalar,
        'toplam': len(cezalar)
    }), 200


@ceza_bp.route('/ode/<int:ceza_id>', methods=['POST'])
@jwt_required()
def pay_penalty(ceza_id):
    """Ceza Öde
    ---
    tags:
      - Cezalar
    security:
      - Bearer: []
    parameters:
      - name: ceza_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Ceza ödendi
      400:
        description: Ödeme hatası
      403:
        description: Yetki yok
    """
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    success, message = CezaService.pay(ceza_id)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message}), 200
    return jsonify({'hata': True, 'mesaj': message}), 400


@ceza_bp.route('/<int:ceza_id>', methods=['GET'])
@jwt_required()
def get_by_id(ceza_id):
    """Ceza Detayı Getir
    ---
    tags:
      - Cezalar
    security:
      - Bearer: []
    parameters:
      - name: ceza_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Ceza detayı
      404:
        description: Ceza bulunamadı
    """
    ceza = CezaService.get_by_id(ceza_id)
    
    if ceza:
        return jsonify({'hata': False, 'data': ceza}), 200
    return jsonify({'hata': True, 'mesaj': 'Ceza bulunamadı.'}), 404
