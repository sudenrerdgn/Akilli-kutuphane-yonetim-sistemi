SQL KODLARI:
-- ============================================
-- AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
-- SQL Server Veritabanı Scripti
-- ============================================

-- Veritabanı Oluşturma
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'KutuphaneDB')
BEGIN
    CREATE DATABASE KutuphaneDB;
END
GO

USE KutuphaneDB;
GO

-- ============================================
-- TABLOLAR
-- ============================================

-- 1. Kullanıcılar Tablosu
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Kullanicilar')
BEGIN
    CREATE TABLE Kullanicilar (
        KullaniciID INT IDENTITY(1,1) PRIMARY KEY,
        Ad NVARCHAR(50) NOT NULL,
        Soyad NVARCHAR(50) NOT NULL,
        Email NVARCHAR(100) UNIQUE NOT NULL,
        Sifre NVARCHAR(255) NOT NULL,
        Telefon NVARCHAR(15),
        Rol NVARCHAR(20) DEFAULT 'uye' CHECK (Rol IN ('admin', 'personel', 'uye')),
        Durum BIT DEFAULT 1,
        KayitTarihi DATETIME DEFAULT GETDATE(),
        SonGirisTarihi DATETIME
    );
END
GO

-- 2. Kategoriler Tablosu
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Kategoriler')
BEGIN
    CREATE TABLE Kategoriler (
        KategoriID INT IDENTITY(1,1) PRIMARY KEY,
        KategoriAdi NVARCHAR(100) NOT NULL UNIQUE,
        Aciklama NVARCHAR(500),
        OlusturmaTarihi DATETIME DEFAULT GETDATE()
    );
END
GO

-- 3. Yazarlar Tablosu
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Yazarlar')
BEGIN
    CREATE TABLE Yazarlar (
        YazarID INT IDENTITY(1,1) PRIMARY KEY,
        Ad NVARCHAR(50) NOT NULL,
        Soyad NVARCHAR(50) NOT NULL,
        Biyografi NVARCHAR(MAX),
        DogumTarihi DATE,
        Ulke NVARCHAR(50),
        OlusturmaTarihi DATETIME DEFAULT GETDATE()
    );
END
GO

-- 4. Kitaplar Tablosu
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Kitaplar')
BEGIN
    CREATE TABLE Kitaplar (
        KitapID INT IDENTITY(1,1) PRIMARY KEY,
        ISBN NVARCHAR(20) UNIQUE NOT NULL,
        KitapAdi NVARCHAR(200) NOT NULL,
        YazarID INT FOREIGN KEY REFERENCES Yazarlar(YazarID),
        KategoriID INT FOREIGN KEY REFERENCES Kategoriler(KategoriID),
        YayinYili INT,
        YayinEvi NVARCHAR(100),
        SayfaSayisi INT,
        Dil NVARCHAR(30) DEFAULT 'Türkçe',
        Aciklama NVARCHAR(MAX),
        KapakResmi NVARCHAR(500),
        ToplamAdet INT DEFAULT 1,
        MevcutAdet INT DEFAULT 1,
        Durum BIT DEFAULT 1,
        EklenmeTarihi DATETIME DEFAULT GETDATE()
    );
END
GO

-- 5. Ödünç İşlemleri Tablosu
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'OduncIslemleri')
BEGIN
    CREATE TABLE OduncIslemleri (
        OduncID INT IDENTITY(1,1) PRIMARY KEY,
        KitapID INT FOREIGN KEY REFERENCES Kitaplar(KitapID),
        KullaniciID INT FOREIGN KEY REFERENCES Kullanicilar(KullaniciID),
        OduncTarihi DATETIME DEFAULT GETDATE(),
        TeslimTarihi DATETIME,
        IadeTarihi DATETIME NULL,
        Durum NVARCHAR(20) DEFAULT 'odunc' CHECK (Durum IN ('odunc', 'iade', 'geciken')),
        Notlar NVARCHAR(500)
    );
END
GO

-- 6. Cezalar Tablosu
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Cezalar')
BEGIN
    CREATE TABLE Cezalar (
        CezaID INT IDENTITY(1,1) PRIMARY KEY,
        OduncID INT FOREIGN KEY REFERENCES OduncIslemleri(OduncID),
        KullaniciID INT FOREIGN KEY REFERENCES Kullanicilar(KullaniciID),
        GecikmeGunu INT NOT NULL,
        CezaTutari DECIMAL(10,2) NOT NULL,
        OdenmeDurumu BIT DEFAULT 0,
        OlusturmaTarihi DATETIME DEFAULT GETDATE(),
        OdemeTarihi DATETIME NULL
    );
END
GO

-- 7. Kitap-Yazar İlişki Tablosu (Çoklu Yazar İçin)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'KitapYazarlar')
BEGIN
    CREATE TABLE KitapYazarlar (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        KitapID INT FOREIGN KEY REFERENCES Kitaplar(KitapID),
        YazarID INT FOREIGN KEY REFERENCES Yazarlar(YazarID)
    );
END
GO

-- 8. Sistem Logları Tablosu
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SistemLoglari')
BEGIN
    CREATE TABLE SistemLoglari (
        LogID INT IDENTITY(1,1) PRIMARY KEY,
        KullaniciID INT,
        Islem NVARCHAR(100) NOT NULL,
        Detay NVARCHAR(MAX),
        IPAdresi NVARCHAR(50),
        Tarih DATETIME DEFAULT GETDATE()
    );
END
GO

-- ============================================
-- TRIGGER'LAR
-- ============================================

-- Trigger 1: Kitap ödünç alındığında mevcut adeti azalt
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'trg_OduncAlindikta')
    DROP TRIGGER trg_OduncAlindikta;
GO

CREATE TRIGGER trg_OduncAlindikta
ON OduncIslemleri
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE Kitaplar
    SET MevcutAdet = MevcutAdet - 1
    FROM Kitaplar k
    INNER JOIN inserted i ON k.KitapID = i.KitapID;
    
    -- Log kaydı
    INSERT INTO SistemLoglari (KullaniciID, Islem, Detay)
    SELECT i.KullaniciID, 'ODUNC_ALMA', 
           'Kitap ID: ' + CAST(i.KitapID AS NVARCHAR) + ' ödünç alındı.'
    FROM inserted i;
END
GO

-- Trigger 2: Kitap iade edildiğinde mevcut adeti artır ve gecikme cezası hesapla
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'trg_IadeEdildiginde')
    DROP TRIGGER trg_IadeEdildiginde;
GO

CREATE TRIGGER trg_IadeEdildiginde
ON OduncIslemleri
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Sadece iade durumuna geçenleri kontrol et
    IF EXISTS (SELECT 1 FROM inserted i 
               INNER JOIN deleted d ON i.OduncID = d.OduncID 
               WHERE i.Durum = 'iade' AND d.Durum != 'iade')
    BEGIN
        -- Mevcut adeti artır
        UPDATE Kitaplar
        SET MevcutAdet = MevcutAdet + 1
        FROM Kitaplar k
        INNER JOIN inserted i ON k.KitapID = i.KitapID
        INNER JOIN deleted d ON i.OduncID = d.OduncID
        WHERE i.Durum = 'iade' AND d.Durum != 'iade';
        
        -- Gecikme varsa ceza hesapla (Günlük 5 TL)
        INSERT INTO Cezalar (OduncID, KullaniciID, GecikmeGunu, CezaTutari)
        SELECT i.OduncID, i.KullaniciID, 
               DATEDIFF(DAY, i.TeslimTarihi, i.IadeTarihi),
               DATEDIFF(DAY, i.TeslimTarihi, i.IadeTarihi) * 5.00
        FROM inserted i
        INNER JOIN deleted d ON i.OduncID = d.OduncID
        WHERE i.Durum = 'iade' 
          AND d.Durum != 'iade'
          AND i.IadeTarihi > i.TeslimTarihi;
        
        -- Log kaydı
        INSERT INTO SistemLoglari (KullaniciID, Islem, Detay)
        SELECT i.KullaniciID, 'IADE', 
               'Kitap ID: ' + CAST(i.KitapID AS NVARCHAR) + ' iade edildi.'
        FROM inserted i
        INNER JOIN deleted d ON i.OduncID = d.OduncID
        WHERE i.Durum = 'iade' AND d.Durum != 'iade';
    END
END
GO

-- Trigger 3: Kullanıcı silindiğinde log tut
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'trg_KullaniciSilindi')
    DROP TRIGGER trg_KullaniciSilindi;
GO

CREATE TRIGGER trg_KullaniciSilindi
ON Kullanicilar
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    INSERT INTO SistemLoglari (Islem, Detay)
    SELECT 'KULLANICI_SILME', 
           'Kullanıcı silindi: ' + d.Ad + ' ' + d.Soyad + ' (' + d.Email + ')'
    FROM deleted d;
END
GO

-- ============================================
-- STORED PROCEDURE'LAR
-- ============================================

-- SP 1: Kitap Arama Prosedürü
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_KitapAra')
    DROP PROCEDURE sp_KitapAra;
GO

CREATE PROCEDURE sp_KitapAra
    @AramaMetni NVARCHAR(200) = NULL,
    @KategoriID INT = NULL,
    @YazarID INT = NULL,
    @SadeceMevcut BIT = 0
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        k.KitapID,
        k.ISBN,
        k.KitapAdi,
        y.Ad + ' ' + y.Soyad AS YazarAdi,
        kat.KategoriAdi,
        k.YayinYili,
        k.YayinEvi,
        k.SayfaSayisi,
        k.ToplamAdet,
        k.MevcutAdet,
        CASE WHEN k.MevcutAdet > 0 THEN 'Mevcut' ELSE 'Tükendi' END AS Durum
    FROM Kitaplar k
    LEFT JOIN Yazarlar y ON k.YazarID = y.YazarID
    LEFT JOIN Kategoriler kat ON k.KategoriID = kat.KategoriID
    WHERE k.Durum = 1
      AND (@AramaMetni IS NULL OR k.KitapAdi LIKE '%' + @AramaMetni + '%' OR k.ISBN LIKE '%' + @AramaMetni + '%')
      AND (@KategoriID IS NULL OR k.KategoriID = @KategoriID)
      AND (@YazarID IS NULL OR k.YazarID = @YazarID)
      AND (@SadeceMevcut = 0 OR k.MevcutAdet > 0)
    ORDER BY k.KitapAdi;
END
GO

-- SP 2: Kullanıcının Ödünç Geçmişi
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_KullaniciOduncGecmisi')
    DROP PROCEDURE sp_KullaniciOduncGecmisi;
GO

CREATE PROCEDURE sp_KullaniciOduncGecmisi
    @KullaniciID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        o.OduncID,
        k.KitapAdi,
        k.ISBN,
        y.Ad + ' ' + y.Soyad AS YazarAdi,
        o.OduncTarihi,
        o.TeslimTarihi,
        o.IadeTarihi,
        o.Durum,
        CASE 
            WHEN o.Durum = 'odunc' AND GETDATE() > o.TeslimTarihi 
            THEN DATEDIFF(DAY, o.TeslimTarihi, GETDATE())
            ELSE 0 
        END AS GecikmeGunu,
        c.CezaTutari
    FROM OduncIslemleri o
    INNER JOIN Kitaplar k ON o.KitapID = k.KitapID
    LEFT JOIN Yazarlar y ON k.YazarID = y.YazarID
    LEFT JOIN Cezalar c ON o.OduncID = c.OduncID
    WHERE o.KullaniciID = @KullaniciID
    ORDER BY o.OduncTarihi DESC;
END
GO

-- SP 3: Geciken Kitapları Getir
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_GecikenKitaplar')
    DROP PROCEDURE sp_GecikenKitaplar;
GO

CREATE PROCEDURE sp_GecikenKitaplar
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        o.OduncID,
        k.KitapAdi,
        u.Ad + ' ' + u.Soyad AS KullaniciAdi,
        u.Email,
        u.Telefon,
        o.OduncTarihi,
        o.TeslimTarihi,
        DATEDIFF(DAY, o.TeslimTarihi, GETDATE()) AS GecikmeGunu,
        DATEDIFF(DAY, o.TeslimTarihi, GETDATE()) * 5.00 AS TahminiCeza
    FROM OduncIslemleri o
    INNER JOIN Kitaplar k ON o.KitapID = k.KitapID
    INNER JOIN Kullanicilar u ON o.KullaniciID = u.KullaniciID
    WHERE o.Durum = 'odunc' 
      AND GETDATE() > o.TeslimTarihi
    ORDER BY GecikmeGunu DESC;
END
GO

-- SP 4: Ödünç Alma İşlemi
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_OduncAl')
    DROP PROCEDURE sp_OduncAl;
GO

CREATE PROCEDURE sp_OduncAl
    @KitapID INT,
    @KullaniciID INT,
    @OduncGunSayisi INT = 14,
    @Sonuc NVARCHAR(200) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @MevcutAdet INT;
    DECLARE @AktifOdunc INT;
    
    -- Mevcut adet kontrolü
    SELECT @MevcutAdet = MevcutAdet FROM Kitaplar WHERE KitapID = @KitapID;
    
    IF @MevcutAdet IS NULL
    BEGIN
        SET @Sonuc = 'HATA: Kitap bulunamadı.';
        RETURN;
    END
    
    IF @MevcutAdet <= 0
    BEGIN
        SET @Sonuc = 'HATA: Kitap stokta mevcut değil.';
        RETURN;
    END
    
    -- Kullanıcının aktif ödünç sayısı kontrolü (max 5)
    SELECT @AktifOdunc = COUNT(*) 
    FROM OduncIslemleri 
    WHERE KullaniciID = @KullaniciID AND Durum = 'odunc';
    
    IF @AktifOdunc >= 5
    BEGIN
        SET @Sonuc = 'HATA: Maksimum ödünç limitine ulaşıldı (5 kitap).';
        RETURN;
    END
    
    -- Ödünç işlemi
    INSERT INTO OduncIslemleri (KitapID, KullaniciID, OduncTarihi, TeslimTarihi, Durum)
    VALUES (@KitapID, @KullaniciID, GETDATE(), DATEADD(DAY, @OduncGunSayisi, GETDATE()), 'odunc');
    
    SET @Sonuc = 'BASARILI: Kitap ödünç alındı. Teslim tarihi: ' + 
                 CONVERT(NVARCHAR, DATEADD(DAY, @OduncGunSayisi, GETDATE()), 103);
END
GO

-- SP 5: İade İşlemi
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_KitapIade')
    DROP PROCEDURE sp_KitapIade;
GO

CREATE PROCEDURE sp_KitapIade
    @OduncID INT,
    @Sonuc NVARCHAR(200) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @Durum NVARCHAR(20);
    DECLARE @TeslimTarihi DATETIME;
    DECLARE @GecikmeGunu INT;
    
    -- Ödünç durumu kontrolü
    SELECT @Durum = Durum, @TeslimTarihi = TeslimTarihi 
    FROM OduncIslemleri 
    WHERE OduncID = @OduncID;
    
    IF @Durum IS NULL
    BEGIN
        SET @Sonuc = 'HATA: Ödünç kaydı bulunamadı.';
        RETURN;
    END
    
    IF @Durum = 'iade'
    BEGIN
        SET @Sonuc = 'HATA: Bu kitap zaten iade edilmiş.';
        RETURN;
    END
    
    -- İade işlemi
    UPDATE OduncIslemleri
    SET Durum = 'iade', IadeTarihi = GETDATE()
    WHERE OduncID = @OduncID;
    
    -- Gecikme kontrolü
    SET @GecikmeGunu = DATEDIFF(DAY, @TeslimTarihi, GETDATE());
    
    IF @GecikmeGunu > 0
        SET @Sonuc = 'BASARILI: Kitap iade edildi. ' + CAST(@GecikmeGunu AS NVARCHAR) + 
                     ' gün gecikme. Ceza: ' + CAST(@GecikmeGunu * 5.00 AS NVARCHAR) + ' TL';
    ELSE
        SET @Sonuc = 'BASARILI: Kitap zamanında iade edildi.';
END
GO

-- SP 6: İstatistikler
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_Istatistikler')
    DROP PROCEDURE sp_Istatistikler;
GO

CREATE PROCEDURE sp_Istatistikler
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        (SELECT COUNT(*) FROM Kitaplar WHERE Durum = 1) AS ToplamKitap,
        (SELECT SUM(MevcutAdet) FROM Kitaplar WHERE Durum = 1) AS MevcutKitap,
        (SELECT COUNT(*) FROM Kullanicilar WHERE Durum = 1) AS ToplamUye,
        (SELECT COUNT(*) FROM OduncIslemleri WHERE Durum = 'odunc') AS AktifOdunc,
        (SELECT COUNT(*) FROM OduncIslemleri WHERE Durum = 'odunc' AND GETDATE() > TeslimTarihi) AS GecikenKitap,
        (SELECT ISNULL(SUM(CezaTutari), 0) FROM Cezalar WHERE OdenmeDurumu = 0) AS ToplamOdenmemisCeza,
        (SELECT COUNT(*) FROM Yazarlar) AS ToplamYazar,
        (SELECT COUNT(*) FROM Kategoriler) AS ToplamKategori;
END
GO


-- Kategoriler
INSERT INTO Kategoriler (KategoriAdi, Aciklama) VALUES 
('Roman', 'Türk ve Dünya Romanları'),
('Bilim Kurgu', 'Bilim Kurgu ve Fantastik Eserler'),
('Tarih', 'Tarih ve Biyografi Kitapları'),
('Felsefe', 'Felsefe ve Düşünce Kitapları'),
('Çocuk', 'Çocuk Kitapları ve Masallar'),
('Bilim', 'Popüler Bilim Kitapları'),
('Şiir', 'Şiir Kitapları'),
('Psikoloji', 'Psikoloji ve Kişisel Gelişim');

-- Yazarlar
INSERT INTO Yazarlar (Ad, Soyad, Ulke, Biyografi) VALUES 
('Orhan', 'Pamuk', 'Türkiye', 'Nobel ödüllü Türk yazar'),
('Sabahattin', 'Ali', 'Türkiye', 'Türk edebiyatının önemli yazarlarından'),
('Fyodor', 'Dostoyevski', 'Rusya', 'Dünya edebiyatının dev isimlerinden'),
('Albert', 'Camus', 'Fransa', 'Varoluşçu edebiyatın öncülerinden'),
('Gabriel', 'Garcia Marquez', 'Kolombiya', 'Büyülü gerçekçilik akımının ustası'),
('Franz', 'Kafka', 'Çekya', 'Modernist edebiyatın öncülerinden'),
('Halide Edib', 'Adıvar', 'Türkiye', 'Türk edebiyatının önemli kadın yazarlarından'),
('Nazım', 'Hikmet', 'Türkiye', 'Dünyaca ünlü Türk şair');

-- Kitaplar
INSERT INTO Kitaplar (ISBN, KitapAdi, YazarID, KategoriID, YayinYili, YayinEvi, SayfaSayisi, ToplamAdet, MevcutAdet, Aciklama) VALUES 
('9789750718533', 'Kar', 1, 1, 2002, 'Yapı Kredi Yayınları', 436, 5, 5, 'Orhan Pamuk''un ödüllü romanı'),
('9789750719387', 'Masumiyet Müzesi', 1, 1, 2008, 'Yapı Kredi Yayınları', 592, 3, 3, 'Aşk ve tutku romanı'),
('9789750505683', 'Kürk Mantolu Madonna', 2, 1, 1943, 'Yapı Kredi Yayınları', 160, 10, 10, 'Türk edebiyatının klasiklerinden'),
('9786053609728', 'Suç ve Ceza', 3, 1, 1866, 'İş Bankası Kültür Yayınları', 687, 4, 4, 'Dostoyevski''nin başyapıtı'),
('9786053607540', 'Yabancı', 4, 4, 1942, 'Can Yayınları', 120, 6, 6, 'Varoluşçu edebiyatın klasiği'),
('9789750738609', 'Yüzyıllık Yalnızlık', 5, 1, 1967, 'Can Yayınları', 448, 5, 5, 'Büyülü gerçekçiliğin başyapıtı'),
('9789750718632', 'Dönüşüm', 6, 2, 1915, 'İş Bankası Kültür Yayınları', 96, 7, 7, 'Kafka''nın ünlü novellası'),
('9789750503528', 'Ateşten Gömlek', 7, 1, 1922, 'Can Yayınları', 224, 4, 4, 'Kurtuluş Savaşı romanı'),
('9789750719691', 'İstanbul', 1, 3, 2003, 'Yapı Kredi Yayınları', 416, 3, 3, 'İstanbul anıları'),
('9789750726415', 'Simyacı', 5, 4, 1988, 'Can Yayınları', 184, 8, 8, 'Yolculuk ve keşif romanı');

PRINT 'Veritabanı başarıyla oluşturuldu ve örnek veriler eklendi.';
GO
