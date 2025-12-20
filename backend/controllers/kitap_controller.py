# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Kitap Controller
# ============================================
#
# DEĞİŞİKLİK: SQL INJECTION & XSS KORUMASI
# - search(): Arama parametresi kontrol ediliyor
# - create(): Tüm inputlar validate ediliyor
# - update(): Tüm inputlar validate ediliyor

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from services import KitapService
from utils.security import SecurityHelper

kitap_bp = Blueprint('kitaplar', __name__)


@kitap_bp.route('', methods=['GET'])
def get_all():
    """Tüm Kitapları Getir"""
    kitaplar = KitapService.get_all()
    return jsonify({
        'hata': False,
        'data': kitaplar,
        'toplam': len(kitaplar)
    }), 200


@kitap_bp.route('/<int:kitap_id>', methods=['GET'])
def get_by_id(kitap_id):
    """ID'ye Göre Kitap Getir"""
    kitap = KitapService.get_by_id(kitap_id)
    
    if kitap:
        return jsonify({'hata': False, 'data': kitap}), 200
    return jsonify({'hata': True, 'mesaj': 'Kitap bulunamadı.'}), 404


@kitap_bp.route('/ara', methods=['GET'])
def search():
    """Kitap Ara"""
    arama = request.args.get('q')
    kategori_id = request.args.get('kategori_id', type=int)
    yazar_id = request.args.get('yazar_id', type=int)
    sadece_mevcut = request.args.get('sadece_mevcut', 'false').lower() == 'true'
    
    # ==========================================
    # SQL INJECTION KORUMASI
    # ==========================================
    if arama:
        if SecurityHelper.check_sql_injection(arama):
            return jsonify({'hata': True, 'mesaj': 'Geçersiz arama terimi!'}), 400
        arama = SecurityHelper.sanitize_string(arama)
    # ==========================================
    
    sonuclar = KitapService.search(arama, kategori_id, yazar_id, sadece_mevcut)
    
    return jsonify({
        'hata': False,
        'data': sonuclar,
        'toplam': len(sonuclar)
    }), 200


@kitap_bp.route('', methods=['POST'])
@jwt_required()
def create():
    """Yeni Kitap Ekle"""
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Bu işlem için yetkiniz yok.'}), 403
    
    data = request.get_json()
    
    if not data.get('isbn') or not data.get('kitap_adi'):
        return jsonify({'hata': True, 'mesaj': 'ISBN ve kitap adı zorunludur.'}), 400
    
    # ==========================================
    # SQL INJECTION & XSS KORUMASI
    # ==========================================
    fields_to_check = ['isbn', 'kitap_adi', 'yayin_evi', 'dil', 'aciklama']
    for field in fields_to_check:
        if data.get(field):
            if SecurityHelper.check_sql_injection(data[field]) or SecurityHelper.check_xss(data[field]):
                return jsonify({'hata': True, 'mesaj': f'{field} alanında geçersiz karakter!'}), 400
    
    # Sanitize
    clean_data = {
        'isbn': SecurityHelper.sanitize_string(data['isbn']),
        'kitap_adi': SecurityHelper.sanitize_string(data['kitap_adi']),
        'yazar_id': data.get('yazar_id'),
        'kategori_id': data.get('kategori_id'),
        'yayin_yili': data.get('yayin_yili'),
        'yayin_evi': SecurityHelper.sanitize_string(data.get('yayin_evi')),
        'sayfa_sayisi': data.get('sayfa_sayisi'),
        'dil': SecurityHelper.sanitize_string(data.get('dil', 'Türkçe')),
        'aciklama': SecurityHelper.sanitize_string(data.get('aciklama')),
        'toplam_adet': data.get('toplam_adet', 1),
        'mevcut_adet': data.get('mevcut_adet', 1)
    }
    # ==========================================
    
    success, message, kitap_id = KitapService.create(clean_data)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message, 'data': {'kitap_id': kitap_id}}), 201
    return jsonify({'hata': True, 'mesaj': message}), 400


@kitap_bp.route('/<int:kitap_id>', methods=['PUT'])
@jwt_required()
def update(kitap_id):
    """Kitap Güncelle"""
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Bu işlem için yetkiniz yok.'}), 403
    
    data = request.get_json()
    
    # ==========================================
    # SQL INJECTION & XSS KORUMASI
    # ==========================================
    fields_to_check = ['isbn', 'kitap_adi', 'yayin_evi', 'dil', 'aciklama']
    for field in fields_to_check:
        if data.get(field):
            if SecurityHelper.check_sql_injection(data[field]) or SecurityHelper.check_xss(data[field]):
                return jsonify({'hata': True, 'mesaj': f'{field} alanında geçersiz karakter!'}), 400
    
    # Sanitize
    clean_data = {}
    if data.get('isbn'):
        clean_data['isbn'] = SecurityHelper.sanitize_string(data['isbn'])
    if data.get('kitap_adi'):
        clean_data['kitap_adi'] = SecurityHelper.sanitize_string(data['kitap_adi'])
    if data.get('yayin_evi'):
        clean_data['yayin_evi'] = SecurityHelper.sanitize_string(data['yayin_evi'])
    if data.get('dil'):
        clean_data['dil'] = SecurityHelper.sanitize_string(data['dil'])
    if data.get('aciklama'):
        clean_data['aciklama'] = SecurityHelper.sanitize_string(data['aciklama'])
    
    # Integer alanlar
    for int_field in ['yazar_id', 'kategori_id', 'yayin_yili', 'sayfa_sayisi', 'toplam_adet', 'mevcut_adet']:
        if int_field in data:
            clean_data[int_field] = data[int_field]
    # ==========================================
    
    success, message = KitapService.update(kitap_id, clean_data)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message}), 200
    return jsonify({'hata': True, 'mesaj': message}), 400


@kitap_bp.route('/<int:kitap_id>', methods=['DELETE'])
@jwt_required()
def delete(kitap_id):
    """Kitap Sil"""
    claims = get_jwt()
    if claims.get('rol') != 'admin':
        return jsonify({'hata': True, 'mesaj': 'Bu işlem için admin yetkisi gereklidir.'}), 403
    
    success, message = KitapService.delete(kitap_id)
    
    if success:
        return jsonify({'hata': False, 'mesaj': message}), 200
    return jsonify({'hata': True, 'mesaj': message}), 400
