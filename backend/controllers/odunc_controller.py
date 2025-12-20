# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Ödünç Controller
# ============================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from services import OduncService

odunc_bp = Blueprint('odunc', __name__)


@odunc_bp.route('', methods=['GET'])
@jwt_required()
def get_all():
    """Tüm Ödünç İşlemlerini Getir (Admin/Personel)"""
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    oduncler = OduncService.get_all()
    return jsonify({
        'hata': False,
        'data': oduncler,
        'toplam': len(oduncler)
    }), 200


@odunc_bp.route('/<int:odunc_id>', methods=['GET'])
@jwt_required()
def get_by_id(odunc_id):
    """ID'ye Göre Ödünç İşlemi Getir"""
    odunc = OduncService.get_by_id(odunc_id)
    
    if odunc:
        return jsonify({'hata': False, 'data': odunc}), 200
    return jsonify({'hata': True, 'mesaj': 'Ödünç kaydı bulunamadı.'}), 404


@odunc_bp.route('/gecmisim', methods=['GET'])
@jwt_required()
def get_my_history():
    """Kendi Ödünç Geçmişimi Getir"""
    kullanici_id = get_jwt_identity()
    oduncler = OduncService.get_by_kullanici(kullanici_id)
    return jsonify({
        'hata': False,
        'data': oduncler,
        'toplam': len(oduncler) if oduncler else 0
    }), 200


@odunc_bp.route('/aktif', methods=['GET'])
@jwt_required()
def get_my_active():
    """Kendi Aktif Ödünçlerimi Getir"""
    kullanici_id = get_jwt_identity()
    oduncler = OduncService.get_aktif_by_kullanici(kullanici_id)
    return jsonify({
        'hata': False,
        'data': oduncler,
        'toplam': len(oduncler) if oduncler else 0
    }), 200


@odunc_bp.route('/geciken', methods=['GET'])
@jwt_required()
def get_overdue():
    """Geciken Kitapları Getir (Admin/Personel)"""
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    gecikenler = OduncService.get_geciken()
    return jsonify({
        'hata': False,
        'data': gecikenler,
        'toplam': len(gecikenler) if gecikenler else 0
    }), 200


@odunc_bp.route('/al', methods=['POST'])
@jwt_required()
def borrow_book():
    """
    Kitap Ödünç Al
    ---
    tags:
      - Ödünç
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - kitap_id
          properties:
            kitap_id:
              type: integer
              example: 1
            gun:
              type: integer
              example: 14
              description: Ödünç gün sayısı (varsayılan 14)
            saat:
              type: integer
              example: 1
              description: Ödünç saat sayısı (test için)
            dakika:
              type: integer
              example: 5
              description: Ödünç dakika sayısı (test için, öncelikli)
    responses:
      200:
        description: Kitap ödünç alındı
      400:
        description: Hata
    """
    kullanici_id = get_jwt_identity()
    data = request.get_json()
    
    kitap_id = data.get('kitap_id')
    gun = data.get('gun')
    saat = data.get('saat')
    dakika = data.get('dakika')
    
    if not kitap_id:
        return jsonify({'hata': True, 'mesaj': 'Kitap ID zorunludur.'}), 400
    
    # Integer'a çevir
    try:
        kitap_id = int(kitap_id)
        if gun is not None:
            gun = int(gun)
        if saat is not None:
            saat = int(saat)
        if dakika is not None:
            dakika = int(dakika)
    except (ValueError, TypeError):
        return jsonify({'hata': True, 'mesaj': 'Geçersiz parametre tipi.'}), 400
    
    # Yeni metodu çağır
    success, message = OduncService.odunc_al(
        kullanici_id=kullanici_id, 
        kitap_id=kitap_id, 
        gun=gun,
        saat=saat,
        dakika=dakika
    )
    
    if success:
        return jsonify({'hata': False, 'mesaj': message}), 200
    return jsonify({'hata': True, 'mesaj': message}), 400


@odunc_bp.route('/iade/<int:odunc_id>', methods=['POST'])
@jwt_required()
def return_book(odunc_id):
    """
    Kitap İade Et
    ---
    tags:
      - Ödünç
    security:
      - Bearer: []
    parameters:
      - name: odunc_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Kitap iade edildi
      400:
        description: Hata
    """
    # Yeni metodu çağır
    success, message, ceza_tutari = OduncService.iade_et(odunc_id)
    
    if success:
        response = {'hata': False, 'mesaj': message}
        if ceza_tutari is not None:
            response['ceza_tutari'] = ceza_tutari
        return jsonify(response), 200
    return jsonify({'hata': True, 'mesaj': message}), 400


@odunc_bp.route('/kullanici/<int:kullanici_id>', methods=['GET'])
@jwt_required()
def get_user_history(kullanici_id):
    """Belirli Kullanıcının Ödünç Geçmişi (Admin/Personel)"""
    claims = get_jwt()
    current_id = get_jwt_identity()
    
    if current_id != kullanici_id and claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    oduncler = OduncService.get_by_kullanici(kullanici_id)
    return jsonify({
        'hata': False,
        'data': oduncler,
        'toplam': len(oduncler) if oduncler else 0
    }), 200
