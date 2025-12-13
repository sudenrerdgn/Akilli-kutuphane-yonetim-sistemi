# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Flask Backend - Ana Uygulama
# ============================================

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from datetime import timedelta
import os

# Controller imports
from controllers.auth_controller import auth_bp
from controllers.kitap_controller import kitap_bp
from controllers.kullanici_controller import kullanici_bp
from controllers.yazar_controller import yazar_bp
from controllers.kategori_controller import kategori_bp
from controllers.odunc_controller import odunc_bp
from controllers.ceza_controller import ceza_bp
from controllers.istatistik_controller import istatistik_bp

# Uygulama oluştur
app = Flask(__name__)

# Konfigürasyon
app.config['SECRET_KEY'] = 'super-secret-key-change-in-production'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# SQL Server Bağlantı Bilgileri
app.config['SQLSERVER_HOST'] = 'Resul\\SQLEXPRESS'
app.config['SQLSERVER_DATABASE'] = 'KutuphaneDB'
app.config['SQLSERVER_USERNAME'] = 'sa'  # Kendi kullanıcı adınızı yazın
app.config['SQLSERVER_PASSWORD'] = 'k9NN66CC'  # Kendi şifrenizi yazın
app.config['SQLSERVER_DRIVER'] = 'ODBC Driver 17 for SQL Server'

# E-posta Konfigürasyonu
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'

# CORS - Tüm kaynaklardan gelen isteklere izin ver
CORS(app, resources={r"/api/*": {"origins": "*"}})

# JWT Manager
jwt = JWTManager(app)

# Swagger Konfigürasyonu
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/"
}

swagger_template = {
    "info": {
        "title": "Akıllı Kütüphane Yönetim Sistemi API",
        "description": "Kütüphane otomasyonu için RESTful API",
        "version": "1.0.0",
        "contact": {
            "name": "Kütüphane Sistemi",
            "email": "destek@kutuphane.com"
        }
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Token. Örnek: 'Bearer {token}'"
        }
    },
    "security": [{"Bearer": []}]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Blueprint'leri kaydet
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(kitap_bp, url_prefix='/api/kitaplar')
app.register_blueprint(kullanici_bp, url_prefix='/api/kullanicilar')
app.register_blueprint(yazar_bp, url_prefix='/api/yazarlar')
app.register_blueprint(kategori_bp, url_prefix='/api/kategoriler')
app.register_blueprint(odunc_bp, url_prefix='/api/odunc')
app.register_blueprint(ceza_bp, url_prefix='/api/cezalar')
app.register_blueprint(istatistik_bp, url_prefix='/api/istatistikler')

# Ana sayfa
@app.route('/')
def home():
    return jsonify({
        'mesaj': 'Akıllı Kütüphane Yönetim Sistemi API',
        'versiyon': '1.0.0',
        'dokumantasyon': '/swagger/',
        'endpoints': {
            'auth': '/api/auth',
            'kitaplar': '/api/kitaplar',
            'kullanicilar': '/api/kullanicilar',
            'yazarlar': '/api/yazarlar',
            'kategoriler': '/api/kategoriler',
            'odunc': '/api/odunc',
            'cezalar': '/api/cezalar',
            'istatistikler': '/api/istatistikler'
        }
    })

# Sağlık kontrolü
@app.route('/api/health')
def health_check():
    return jsonify({
        'durum': 'aktif',
        'veritabani': 'bagli',
        'mesaj': 'Sistem çalışıyor'
    })

# JWT Hata İşleyicileri
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'hata': True,
        'mesaj': 'Token süresi dolmuş. Lütfen tekrar giriş yapın.'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'hata': True,
        'mesaj': 'Geçersiz token.'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'hata': True,
        'mesaj': 'Token bulunamadı. Lütfen giriş yapın.'
    }), 401

# Genel hata işleyicileri
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'hata': True,
        'mesaj': 'Kaynak bulunamadı.'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'hata': True,
        'mesaj': 'Sunucu hatası oluştu.'
    }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ")
    print("=" * 50)
    print(f"API Başlatılıyor: http://localhost:5000")
    print(f"Swagger UI: http://localhost:5000/swagger/")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
