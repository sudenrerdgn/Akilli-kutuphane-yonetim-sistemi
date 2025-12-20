# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Ceza Controller
# ============================================

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from services import CezaService

ceza_bp = Blueprint('cezalar', __name__)


@ceza_bp.route('', methods=['GET'])
@jwt_required()
def get_all():
    """Tüm Cezaları Getir (Admin/Personel)"""
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    cezalar = CezaService.get_all()
    return jsonify({
        'hata': False,
        'data': cezalar,
        'toplam': len(cezalar) if cezalar else 0
    }), 200


@ceza_bp.route('/<int:ceza_id>', methods=['GET'])
@jwt_required()
def get_by_id(ceza_id):
    """ID'ye Göre Ceza Getir"""
    ceza = CezaService.get_by_id(ceza_id)
    
    if ceza:
        return jsonify({'hata': False, 'data': ceza}), 200
    return jsonify({'hata': True, 'mesaj': 'Ceza bulunamadı.'}), 404


@ceza_bp.route('/benim', methods=['GET'])
@jwt_required()
def get_my_penalties():
    """Kendi Cezalarımı Getir"""
    kullanici_id = get_jwt_identity()
    cezalar = CezaService.get_by_kullanici(kullanici_id)
    toplam_odenmemis = CezaService.get_user_total_unpaid(kullanici_id)
    
    return jsonify({
        'hata': False,
        'data': cezalar,
        'toplam': len(cezalar) if cezalar else 0,
        'toplam_odenmemis': toplam_odenmemis
    }), 200


@ceza_bp.route('/odenmemis', methods=['GET'])
@jwt_required()
def get_my_unpaid():
    """Kendi Ödenmemiş Cezalarımı Getir"""
    kullanici_id = get_jwt_identity()
    cezalar = CezaService.get_unpaid_by_kullanici(kullanici_id)
    toplam = CezaService.get_user_total_unpaid(kullanici_id)
    
    return jsonify({
        'hata': False,
        'data': cezalar,
        'toplam_tutar': toplam
    }), 200


@ceza_bp.route('/ode/<int:ceza_id>', methods=['POST'])
@jwt_required()
def pay_penalty(ceza_id):
    """
    Ceza Öde
    - Sadece ceza sahibi kullanıcı kendi cezasını ödeyebilir
    - Admin/Personel bile başkasının cezasını ödeyemez
    """
    current_user_id = get_jwt_identity()
    
    # Cezayı getir
    ceza = CezaService.get_by_id(ceza_id)
    if not ceza:
        return jsonify({'hata': True, 'mesaj': 'Ceza bulunamadı.'}), 404
    
    # Sadece ceza sahibi ödeyebilir
    if ceza['KullaniciID'] != current_user_id:
        return jsonify({'hata': True, 'mesaj': 'Sadece kendi cezanızı ödeyebilirsiniz.'}), 403
    
    success, message = CezaService.pay(ceza_id)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message}), 200
    return jsonify({'hata': True, 'mesaj': message}), 400


@ceza_bp.route('/kullanici/<int:kullanici_id>', methods=['GET'])
@jwt_required()
def get_user_penalties(kullanici_id):
    """Belirli Kullanıcının Cezaları (Admin/Personel)"""
    claims = get_jwt()
    current_id = get_jwt_identity()
    
    if current_id != kullanici_id and claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    cezalar = CezaService.get_by_kullanici(kullanici_id)
    return jsonify({
        'hata': False,
        'data': cezalar,
        'toplam': len(cezalar) if cezalar else 0
    }), 200
