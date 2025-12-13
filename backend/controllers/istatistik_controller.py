# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# İstatistik Controller
# ============================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from services import IstatistikService

istatistik_bp = Blueprint('istatistikler', __name__)


@istatistik_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Dashboard İstatistikleri
    ---
    tags:
      - İstatistikler
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard istatistikleri
      403:
        description: Yetki yok
    """
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    stats = IstatistikService.get_dashboard()
    return jsonify({
        'hata': False,
        'data': stats
    }), 200


@istatistik_bp.route('/populer-kitaplar', methods=['GET'])
def get_popular_books():
    """En Popüler Kitaplar
    ---
    tags:
      - İstatistikler
    parameters:
      - name: limit
        in: query
        type: integer
        default: 10
        description: Kaç kitap getirileceği
    responses:
      200:
        description: Popüler kitaplar listesi
    """
    limit = request.args.get('limit', 10, type=int)
    kitaplar = IstatistikService.get_popular_books(limit)
    return jsonify({
        'hata': False,
        'data': kitaplar
    }), 200


@istatistik_bp.route('/aktif-uyeler', methods=['GET'])
@jwt_required()
def get_active_users():
    """En Aktif Üyeler
    ---
    tags:
      - İstatistikler
    security:
      - Bearer: []
    parameters:
      - name: limit
        in: query
        type: integer
        default: 10
        description: Kaç üye getirileceği
    responses:
      200:
        description: Aktif üyeler listesi
      403:
        description: Yetki yok
    """
    claims = get_jwt()
    if claims.get('rol') not in ['admin', 'personel']:
        return jsonify({'hata': True, 'mesaj': 'Yetkiniz yok.'}), 403
    
    limit = request.args.get('limit', 10, type=int)
    uyeler = IstatistikService.get_active_users(limit)
    return jsonify({
        'hata': False,
        'data': uyeler
    }), 200
