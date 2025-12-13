📚 Akıllı Kütüphane Yönetim Sistemi

Akıllı Kütüphane Yönetim Sistemi, kütüphanedeki kitapların, kullanıcıların ve ödünç işlemlerinin dijital olarak yönetilmesini sağlayan bir otomasyon projesidir.
Proje, öğrencilerin veritabanı tasarımı, REST API geliştirme ve katmanlı mimari konularında deneyim kazanmasını amaçlar.

## 📱 Özellikler

- ✅ JWT tabanlı kimlik doğrulama
- ✅ Rol tabanlı yetkilendirme (Admin, Personel, Üye)
- ✅ Kitap, Yazar, Kategori CRUD işlemleri
- ✅ Ödünç alma ve iade sistemi
- ✅ Otomatik gecikme cezası hesaplama
- ✅ Trigger ve Stored Procedure kullanımı
- ✅ Swagger API dokümantasyonu
- ✅ Modern responsive arayüz
- ✅ Gerçek zamanlı arama
- ✅ Dashboard istatistikleri


## 📁 Proje Yapısı

kutuphane_sistemi/
├── backend/
│   ├── app.py                    # Ana Flask uygulaması
│   ├── requirements.txt          # Python paketleri
│   ├── controllers/              # API Controller'ları
│   │   ├── auth_controller.py
│   │   ├── kitap_controller.py
│   │   ├── kullanici_controller.py
│   │   ├── yazar_controller.py
│   │   ├── kategori_controller.py
│   │   ├── odunc_controller.py
│   │   ├── ceza_controller.py
│   │   └── istatistik_controller.py
│   ├── models/                   # Entity sınıfları
│   ├── repositories/             # Veritabanı işlemleri
│   ├── services/                 # İş mantığı
│   └── utils/                    # Yardımcı fonksiyonlar
├── frontend/
│   ├── index.html               # Ana sayfa
│   ├── css/
│   │   └── style.css            # Stiller
│   └── js/
│       ├── api.js               # API helper
│       └── app.js               # Ana uygulama
├── database/
│   └── kutuphane_db.sql         # SQL Server scripti


🛠 Kullanılan Teknolojiler

-🐍 Backend (Python / Flask)
Mimari: Katmanlı yapı (Model, Repository, Service, Controller)
API: REST mimarisi (GET, POST, PUT, DELETE)
Kimlik Doğrulama: JWT (JSON Web Token)
Bağımlılıklar: Flask, Flask-JWT-Extended, pyodbc

-🗄 Veritabanı (Microsoft SQL Server)
Tablolar, ilişkiler, TRIGGER ve STORED PROCEDURE kullanılmıştır.

-📦 Veritabanını kurmak için
SQL Server Management Studio’yu aç
database_setup.sql dosyasını çalıştır
Database otomatik oluşur
Tablolar + Trigger + SP + View + Test verileri hepsi hazır olur

-💻 Frontend
HTML, CSS ve JavaScript tabanlı arayüz
Giriş, kitap arama/listeleme, ödünç alma ve iade ekranları


🧪 Test ve Demo
API’ler Postman veya Swagger üzerinden test edilmiştir.

## 🔑 Varsayılan Kullanıcılar

| E-posta | Şifre | Rol |
|---------|-------|-----|
| admin@test.com | 067272 | Admin |
| sude.100@gmail.com | sudesıla1 | Üye |


🎯 Öğrenim Hedefleri
İlişkisel veritabanı tasarımı (SQL Server)
CRUD ve JOIN sorguları
Trigger ve Stored Procedure kullanımı
Flask ile REST API geliştirme
JWT tabanlı kimlik doğrulama
Katmanlı mimari uygulaması
