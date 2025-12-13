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
    """Tüm Ödünç İşlemlerini Getir
    ---
    tags:
      - Ödünç İşlemleri
    security:
      - Bearer: []
    responses:
      200:
        description: Ödünç işlemleri listesi
      403:
        description: Yetki yok
    """
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
    """Ödünç Detayı Getir
    ---
    tags:
      - Ödünç İşlemleri
    security:
      - Bearer: []
    parameters:
      - name: odunc_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Ödünç detayı
      404:
        description: Ödünç bulunamadı
    """
    odunc = OduncService.get_by_id(odunc_id)
    
    if odunc:
        return jsonify({'hata': False, 'data': odunc}), 200
    return jsonify({'hata': True, 'mesaj': 'Ödünç kaydı bulunamadı.'}), 404


@odunc_bp.route('/gecmisim', methods=['GET'])
@jwt_required()
def get_my_history():
    """Kendi Ödünç Geçmişim
    ---
    tags:
      - Ödünç İşlemleri
    security:
      - Bearer: []
    responses:
      200:
        description: Kullanıcının ödünç geçmişi
    """
    kullanici_id = get_jwt_identity()
    oduncler = OduncService.get_by_kullanici(kullanici_id)
    return jsonify({
        'hata': False,
        'data': oduncler,
        'toplam': len(oduncler)
    }), 200


@odunc_bp.route('/aktif', methods=['GET'])
@jwt_required()
def get_my_active():
    """Aktif Ödünçlerim
    ---
    tags:
      - Ödünç İşlemleri
    security:
      - Bearer: []
    responses:
      200:
        description: Kullanıcının aktif ödünçleri
    """
    kullanici_id = get_jwt_identity()
    oduncler = OduncService.get_aktif_by_kullanici(kullanici_id)
    return jsonify({
        'hata': False,
        'data': oduncler,
        'toplam': len(oduncler)
    }), 200


@odunc_bp.route('/geciken', methods=['GET'])
@jwt_required()
def get_overdue():
    """Geciken Kitaplar
    ---
    tags:
      - Ödünç İşlemleri
    security:
      - Bearer: []
    responses:
      200:
        description: Geciken kitaplar listesi
      403:
        description: Yetki yok
    """
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    geciken = OduncService.get_geciken()
    return jsonify({
        'hata': False,
        'data': geciken,
        'toplam': len(geciken) if geciken else 0
    }), 200


@odunc_bp.route('/al', methods=['POST'])
@jwt_required()
def borrow():
    """Kitap Ödünç Al
    ---
    tags:
      - Ödünç İşlemleri
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
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
              description: Ödünç süresi (gün)
    responses:
      201:
        description: Kitap ödünç alındı
      400:
        description: İşlem hatası
    """
    kullanici_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('kitap_id'):
        return jsonify({'hata': True, 'mesaj': 'Kitap ID zorunludur.'}), 400
    
    gun = data.get('gun', 14)
    success, message = OduncService.odunc_al(kullanici_id, data['kitap_id'], gun)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message}), 201
    return jsonify({'hata': True, 'mesaj': message}), 400


@odunc_bp.route('/iade/<int:odunc_id>', methods=['POST'])
@jwt_required()
def return_book(odunc_id):
    """Kitap İade Et
    ---
    tags:
      - Ödünç İşlemleri
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
        description: İade hatası
    """
    success, message, ceza = OduncService.iade_et(odunc_id)
    
    if success:
        response = {'hata': False, 'mesaj': message}
        if ceza and ceza > 0:
            response['ceza'] = ceza
        return jsonify(response), 200
    return jsonify({'hata': True, 'mesaj': message}), 400


@odunc_bp.route('/kullanici/<int:kullanici_id>', methods=['GET'])
@jwt_required()
def get_by_kullanici(kullanici_id):
    """Kullanıcının Ödünç Geçmişi
    ---
    tags:
      - Ödünç İşlemleri
    security:
      - Bearer: []
    parameters:
      - name: kullanici_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Kullanıcının ödünç geçmişi
      403:
        description: Yetki yok
    """
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    oduncler = OduncService.get_by_kullanici(kullanici_id)
    return jsonify({
        'hata': False,
        'data': oduncler,
        'toplam': len(oduncler)
    }), 200
