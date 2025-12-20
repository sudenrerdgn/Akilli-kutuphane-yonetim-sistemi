# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Flask Backend - Ana Uygulama
# ============================================

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from datetime import timedelta

# Controller imports
from controllers.auth_controller import auth_bp
from controllers.kitap_controller import kitap_bp
from controllers.kullanici_controller import kullanici_bp
from controllers.yazar_controller import yazar_bp
from controllers.kategori_controller import kategori_bp
from controllers.odunc_controller import odunc_bp
from controllers.ceza_controller import ceza_bp
from controllers.istatistik_controller import istatistik_bp


app = Flask(__name__)

# Konfigürasyon
app.config['SECRET_KEY'] = 'super-secret-key-change-in-production'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# SQL Server
app.config['SQLSERVER_HOST'] = 'Resul\\SQLEXPRESS'
app.config['SQLSERVER_DATABASE'] = 'KutuphaneDB'
app.config['SQLSERVER_USERNAME'] = 'sa' 
app.config['SQLSERVER_PASSWORD'] = 'k9NN66CC'
app.config['SQLSERVER_DRIVER'] = 'ODBC Driver 17 for SQL Server'

# E-posta
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'

CORS(app, resources={r"/api/*": {"origins": "*"}})
jwt = JWTManager(app)

# ==========================================
# SWAGGER - TAM MANUEL MOD
# ==========================================
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: False,
            "model_filter": lambda tag: False,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Akıllı Kütüphane Yönetim Sistemi API",
        "description": "Kütüphane otomasyonu için RESTful API.\n\n**Yetkilendirme:** Login sonrası dönen token'ı Authorize butonuna 'Bearer {token}' formatında girin.",
        "version": "1.0.0"
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Token: 'Bearer {token}'"
        }
    },
    "tags": [
        {"name": "Auth", "description": "Kimlik doğrulama"},
        {"name": "Kitaplar", "description": "Kitap CRUD"},
        {"name": "Yazarlar", "description": "Yazar CRUD"},
        {"name": "Kategoriler", "description": "Kategori CRUD"},
        {"name": "Odunc", "description": "Ödünç işlemleri"},
        {"name": "Cezalar", "description": "Ceza işlemleri"},
        {"name": "Kullanicilar", "description": "Kullanıcı yönetimi"},
        {"name": "Istatistikler", "description": "Dashboard"}
    ],
    "paths": {
        "/api/auth/register": {
            "post": {
                "tags": ["Auth"],
                "summary": "Yeni kullanıcı kaydı",
                "parameters": [{"name": "body", "in": "body", "required": True, "schema": {
                    "type": "object",
                    "properties": {
                        "ad": {"type": "string", "example": "Ahmet"},
                        "soyad": {"type": "string", "example": "Yılmaz"},
                        "email": {"type": "string", "example": "ahmet@mail.com"},
                        "sifre": {"type": "string", "example": "sifre123"},
                        "telefon": {"type": "string", "example": "05551234567"}
                    },
                    "required": ["ad", "soyad", "email", "sifre"]
                }}],
                "responses": {"201": {"description": "Başarılı"}, "400": {"description": "Hata"}}
            }
        },
        "/api/auth/login": {
            "post": {
                "tags": ["Auth"],
                "summary": "Giriş yap",
                "parameters": [{"name": "body", "in": "body", "required": True, "schema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "example": "admin@kutuphane.com"},
                        "sifre": {"type": "string", "example": "Admin123!"}
                    },
                    "required": ["email", "sifre"]
                }}],
                "responses": {"200": {"description": "Token döner"}, "401": {"description": "Hatalı"}}
            }
        },
        "/api/auth/me": {
            "get": {
                "tags": ["Auth"],
                "summary": "Mevcut kullanıcı",
                "security": [{"Bearer": []}],
                "responses": {"200": {"description": "Kullanıcı bilgisi"}}
            }
        },
        "/api/kitaplar": {
            "get": {
                "tags": ["Kitaplar"],
                "summary": "Tüm kitaplar",
                "responses": {"200": {"description": "Liste"}}
            },
            "post": {
                "tags": ["Kitaplar"],
                "summary": "Kitap ekle",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "body", "in": "body", "required": True, "schema": {
                    "type": "object",
                    "properties": {
                        "isbn": {"type": "string", "example": "9789750719387"},
                        "kitap_adi": {"type": "string", "example": "Suç ve Ceza"},
                        "yazar_id": {"type": "integer", "example": 1},
                        "kategori_id": {"type": "integer", "example": 1},
                        "yayin_yili": {"type": "integer", "example": 2020},
                        "yayin_evi": {"type": "string", "example": "İş Bankası"},
                        "sayfa_sayisi": {"type": "integer", "example": 500},
                        "dil": {"type": "string", "example": "Türkçe"},
                        "toplam_adet": {"type": "integer", "example": 5},
                        "mevcut_adet": {"type": "integer", "example": 5}
                    },
                    "required": ["isbn", "kitap_adi"]
                }}],
                "responses": {"201": {"description": "Eklendi"}, "403": {"description": "Yetki yok"}}
            }
        },
        "/api/kitaplar/{kitap_id}": {
            "get": {
                "tags": ["Kitaplar"],
                "summary": "Kitap detay",
                "parameters": [{"name": "kitap_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "Detay"}, "404": {"description": "Bulunamadı"}}
            },
            "put": {
                "tags": ["Kitaplar"],
                "summary": "Kitap güncelle",
                "security": [{"Bearer": []}],
                "parameters": [
                    {"name": "kitap_id", "in": "path", "type": "integer", "required": True},
                    {"name": "body", "in": "body", "schema": {"type": "object"}}
                ],
                "responses": {"200": {"description": "Güncellendi"}}
            },
            "delete": {
                "tags": ["Kitaplar"],
                "summary": "Kitap sil",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "kitap_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "Silindi"}}
            }
        },
        "/api/kitaplar/ara": {
            "get": {
                "tags": ["Kitaplar"],
                "summary": "Kitap ara",
                "parameters": [
                    {"name": "q", "in": "query", "type": "string"},
                    {"name": "kategori_id", "in": "query", "type": "integer"},
                    {"name": "yazar_id", "in": "query", "type": "integer"},
                    {"name": "sadece_mevcut", "in": "query", "type": "boolean"}
                ],
                "responses": {"200": {"description": "Sonuçlar"}}
            }
        },
        "/api/yazarlar": {
            "get": {
                "tags": ["Yazarlar"],
                "summary": "Tüm yazarlar",
                "responses": {"200": {"description": "Liste"}}
            },
            "post": {
                "tags": ["Yazarlar"],
                "summary": "Yazar ekle",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "body", "in": "body", "required": True, "schema": {
                    "type": "object",
                    "properties": {
                        "ad": {"type": "string", "example": "Fyodor"},
                        "soyad": {"type": "string", "example": "Dostoyevski"},
                        "ulke": {"type": "string", "example": "Rusya"},
                        "biyografi": {"type": "string"}
                    },
                    "required": ["ad", "soyad"]
                }}],
                "responses": {"201": {"description": "Eklendi"}}
            }
        },
        "/api/yazarlar/{yazar_id}": {
            "get": {
                "tags": ["Yazarlar"],
                "summary": "Yazar detay",
                "parameters": [{"name": "yazar_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "Detay"}}
            },
            "put": {
                "tags": ["Yazarlar"],
                "summary": "Yazar güncelle",
                "security": [{"Bearer": []}],
                "parameters": [
                    {"name": "yazar_id", "in": "path", "type": "integer", "required": True},
                    {"name": "body", "in": "body", "schema": {"type": "object"}}
                ],
                "responses": {"200": {"description": "Güncellendi"}}
            },
            "delete": {
                "tags": ["Yazarlar"],
                "summary": "Yazar sil",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "yazar_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "Silindi"}}
            }
        },
        "/api/kategoriler": {
            "get": {
                "tags": ["Kategoriler"],
                "summary": "Tüm kategoriler",
                "responses": {"200": {"description": "Liste"}}
            },
            "post": {
                "tags": ["Kategoriler"],
                "summary": "Kategori ekle",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "body", "in": "body", "required": True, "schema": {
                    "type": "object",
                    "properties": {
                        "kategori_adi": {"type": "string", "example": "Roman"},
                        "aciklama": {"type": "string"}
                    },
                    "required": ["kategori_adi"]
                }}],
                "responses": {"201": {"description": "Eklendi"}}
            }
        },
        "/api/kategoriler/{kategori_id}": {
            "get": {
                "tags": ["Kategoriler"],
                "summary": "Kategori detay",
                "parameters": [{"name": "kategori_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "Detay"}}
            },
            "put": {
                "tags": ["Kategoriler"],
                "summary": "Kategori güncelle",
                "security": [{"Bearer": []}],
                "parameters": [
                    {"name": "kategori_id", "in": "path", "type": "integer", "required": True},
                    {"name": "body", "in": "body", "schema": {"type": "object"}}
                ],
                "responses": {"200": {"description": "Güncellendi"}}
            },
            "delete": {
                "tags": ["Kategoriler"],
                "summary": "Kategori sil",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "kategori_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "Silindi"}}
            }
        },
        "/api/odunc": {
            "get": {
                "tags": ["Odunc"],
                "summary": "Ödünç listesi",
                "security": [{"Bearer": []}],
                "responses": {"200": {"description": "Liste"}}
            },
            "post": {
                "tags": ["Odunc"],
                "summary": "Kitap ödünç al",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "body", "in": "body", "required": True, "schema": {
                    "type": "object",
                    "properties": {
                        "kitap_id": {"type": "integer", "example": 1},
                        "gun": {"type": "integer", "example": 0},
                        "saat": {"type": "integer", "example": 0},
                        "dakika": {"type": "integer", "example": 5}
                    },
                    "required": ["kitap_id"]
                }}],
                "responses": {"201": {"description": "Ödünç alındı"}}
            }
        },
        "/api/odunc/{odunc_id}/iade": {
            "put": {
                "tags": ["Odunc"],
                "summary": "Kitap iade et",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "odunc_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "İade edildi"}}
            }
        },
        "/api/odunc/aktif": {
            "get": {
                "tags": ["Odunc"],
                "summary": "Aktif ödünçlerim",
                "security": [{"Bearer": []}],
                "responses": {"200": {"description": "Liste"}}
            }
        },
        "/api/odunc/gecmis": {
            "get": {
                "tags": ["Odunc"],
                "summary": "Ödünç geçmişim",
                "security": [{"Bearer": []}],
                "responses": {"200": {"description": "Liste"}}
            }
        },
        "/api/odunc/geciken": {
            "get": {
                "tags": ["Odunc"],
                "summary": "Geciken kitaplar",
                "security": [{"Bearer": []}],
                "responses": {"200": {"description": "Liste"}}
            }
        },
        "/api/cezalar": {
            "get": {
                "tags": ["Cezalar"],
                "summary": "Ceza listesi",
                "security": [{"Bearer": []}],
                "responses": {"200": {"description": "Liste"}}
            }
        },
        "/api/cezalar/benim": {
            "get": {
                "tags": ["Cezalar"],
                "summary": "Cezalarım",
                "security": [{"Bearer": []}],
                "responses": {"200": {"description": "Liste"}}
            }
        },
        "/api/cezalar/{ceza_id}/ode": {
            "post": {
                "tags": ["Cezalar"],
                "summary": "Ceza öde",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "ceza_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "Ödendi"}}
            }
        },
        "/api/kullanicilar": {
            "get": {
                "tags": ["Kullanicilar"],
                "summary": "Kullanıcı listesi",
                "security": [{"Bearer": []}],
                "responses": {"200": {"description": "Liste"}}
            }
        },
        "/api/kullanicilar/{kullanici_id}": {
            "get": {
                "tags": ["Kullanicilar"],
                "summary": "Kullanıcı detay",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "kullanici_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "Detay"}}
            },
            "delete": {
                "tags": ["Kullanicilar"],
                "summary": "Kullanıcı sil",
                "security": [{"Bearer": []}],
                "parameters": [{"name": "kullanici_id", "in": "path", "type": "integer", "required": True}],
                "responses": {"200": {"description": "Silindi"}}
            }
        },
        "/api/istatistikler/dashboard": {
            "get": {
                "tags": ["Istatistikler"],
                "summary": "Dashboard istatistikleri",
                "security": [{"Bearer": []}],
                "responses": {"200": {"description": "İstatistikler"}}
            }
        },
        "/api/istatistikler/populer-kitaplar": {
            "get": {
                "tags": ["Istatistikler"],
                "summary": "Popüler kitaplar",
                "parameters": [{"name": "limit", "in": "query", "type": "integer", "default": 10}],
                "responses": {"200": {"description": "Liste"}}
            }
        }
    }
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

@app.route('/')
def home():
    return jsonify({
        'mesaj': 'Akıllı Kütüphane Yönetim Sistemi API',
        'versiyon': '1.0.0',
        'swagger': '/swagger/'
    })

@app.route('/api/health')
def health_check():
    return jsonify({'durum': 'aktif'})

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'hata': True, 'mesaj': 'Token süresi dolmuş.'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'hata': True, 'mesaj': 'Geçersiz token.'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'hata': True, 'mesaj': 'Token bulunamadı.'}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({'hata': True, 'mesaj': 'Kaynak bulunamadı.'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'hata': True, 'mesaj': 'Sunucu hatası.'}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ")
    print("API: http://localhost:5000")
    print("Swagger: http://localhost:5000/swagger/")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
