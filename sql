--Tablo oluşturduk

CREATE TABLE Kullanicilar (
    kullaniciID INT IDENTITY(1,1) PRIMARY KEY,
    ad NVARCHAR(50) NOT NULL,
    soyad NVARCHAR(50) NOT NULL,
    eposta NVARCHAR(100) NOT NULL UNIQUE,
    sifre NVARCHAR(200) NOT NULL,
    rol NVARCHAR(20) NOT NULL
);
CREATE TABLE Yazarlar (
    yazarID INT IDENTITY(1,1) PRIMARY KEY,
    ad NVARCHAR(50) NOT NULL,
    soyad NVARCHAR(50) NOT NULL
);
CREATE TABLE Kategoriler (
    kategoriID INT IDENTITY(1,1) PRIMARY KEY,
    kategori_adi NVARCHAR(100) NOT NULL
);
CREATE TABLE Kitaplar (
    kitapID INT IDENTITY(1,1) PRIMARY KEY,
    baslik NVARCHAR(200) NOT NULL,
    isbn NVARCHAR(30) NOT NULL UNIQUE,
    yayin_yili INT,
    yazarID INT NOT NULL,
    kategoriID INT NOT NULL,

    FOREIGN KEY (yazarID) REFERENCES Yazarlar(yazarID),
    FOREIGN KEY (kategoriID) REFERENCES Kategoriler(kategoriID)
);
CREATE TABLE Kitap_Kopya (
    kopyaID INT IDENTITY(1,1) PRIMARY KEY,
    kitapID INT NOT NULL,
    durum NVARCHAR(20) NOT NULL DEFAULT 'Mevcut',

    FOREIGN KEY (kitapID) REFERENCES Kitaplar(kitapID)
);
CREATE TABLE Odunc (
    oduncID INT IDENTITY(1,1) PRIMARY KEY,
    kopyaID INT NOT NULL,
    kullaniciID INT NOT NULL,
    odunc_tarihi DATE NOT NULL,
    iade_tarihi DATE NOT NULL,
    gercek_iade_tarihi DATE,
    durum NVARCHAR(20),

    FOREIGN KEY (kopyaID) REFERENCES Kitap_Kopya(kopyaID),
    FOREIGN KEY (kullaniciID) REFERENCES Kullanicilar(kullaniciID)
);
CREATE TABLE Ceza (
    cezaID INT IDENTITY(1,1) PRIMARY KEY,
    oduncID INT NOT NULL UNIQUE,
    gun_sayisi INT NOT NULL,
    ceza_tutari DECIMAL(10,2) NOT NULL,
    odendi_mi BIT NOT NULL DEFAULT 0,

    FOREIGN KEY (oduncID) REFERENCES Odunc(oduncID)
);

-- tablolara ekleme yaptık

INSERT INTO Kullanicilar (ad, soyad, eposta, sifre, rol)
VALUES 
('Ahmet', 'Yılmaz', 'ahmet@example.com', 'sifre123', 'uye'),
('Ayşe', 'Kara', 'ayse@example.com', 'sifre456', 'uye'),
('Admin', 'Root', 'admin@example.com', 'admin123', 'admin');

INSERT INTO Yazarlar (ad, soyad)
VALUES 
('Orhan', 'Pamuk'),
('Yaşar', 'Kemal');

INSERT INTO Kategoriler (kategori_adi)
VALUES 
('Roman'),
('Tarih');

INSERT INTO Kitaplar (baslik, isbn, yayin_yili, yazarID, kategoriID)
VALUES 
('Benim Adım Kırmızı', '9789750705482', 1998, 1, 1),
('İnce Memed', '9789750700739', 1955, 2, 1);

INSERT INTO Kitap_Kopya (kitapID)
VALUES 
(1),
(1),
(2);

INSERT INTO Odunc (kopyaID, kullaniciID, odunc_tarihi, iade_tarihi, durum)
VALUES 
(1, 1, '2025-11-01', '2025-11-10', 'Alındı'),
(3, 2, '2025-11-05', '2025-11-12', 'Alındı');

-- SP oluşturma (iade al (iade edildi)/ver (mevcut))

USE [kütüphane_yonetim_sistemi];
GO

-- Eğer prosedür varsa sil
IF OBJECT_ID('sp_OduncIslem', 'P') IS NOT NULL
    DROP PROCEDURE sp_OduncIslem;
GO

CREATE PROCEDURE sp_OduncIslem
    @islem NVARCHAR(10), -- 'Al' veya 'Iade'
    @kopyaID INT = NULL,
    @kullaniciID INT = NULL,
    @oduncID INT = NULL,
    @odunc_tarihi DATE = NULL,
    @iade_tarihi DATE = NULL,
    @gercek_iade_tarihi DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF @islem = 'Al'
    BEGIN
        -- Ödünç alma
        INSERT INTO Odunc (kopyaID, kullaniciID, odunc_tarihi, iade_tarihi, durum)
        VALUES (@kopyaID, @kullaniciID, @odunc_tarihi, @iade_tarihi, 'Alındı');

        -- Kitap kopya durumunu güncelle
        UPDATE Kitap_Kopya
        SET durum = 'Alındı'
        WHERE kopyaID = @kopyaID;
    END
    ELSE IF @islem = 'Iade'
    BEGIN
        -- İade işlemi
        UPDATE Odunc
        SET gercek_iade_tarihi = @gercek_iade_tarihi,
            durum = 'İade Edildi'
        WHERE oduncID = @oduncID;

        -- Kitap kopya durumunu güncelle
        UPDATE Kitap_Kopya
        SET durum = 'Mevcut'
        WHERE kopyaID = (SELECT kopyaID FROM Odunc WHERE oduncID = @oduncID);
    END
END;
GO

-- Trigger oluşturma (geç iadede ceza oluşması)

USE [kütüphane_yonetim_sistemi];
GO

-- Eğer trigger varsa önce sil
IF OBJECT_ID('trg_GecIadeCeza', 'TR') IS NOT NULL
    DROP TRIGGER trg_GecIadeCeza;
GO

CREATE TRIGGER trg_GecIadeCeza
ON Odunc
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Gecikme varsa ve ceza eklenmemişse Ceza tablosuna ekle
    INSERT INTO Ceza (oduncID, gun_sayisi, ceza_tutari, odendi_mi)
    SELECT 
        i.oduncID,
        DATEDIFF(DAY, i.iade_tarihi, i.gercek_iade_tarihi) AS gun_sayisi,
        DATEDIFF(DAY, i.iade_tarihi, i.gercek_iade_tarihi) * 5.0 AS ceza_tutari,
        0 AS odendi_mi
    FROM inserted i
    LEFT JOIN Ceza c ON i.oduncID = c.oduncID
    WHERE i.gercek_iade_tarihi > i.iade_tarihi
      AND c.oduncID IS NULL;
END;
GO

-- Vıew oluşturma (aktif odunc durumu)

USE [kütüphane_yonetim_sistemi];
GO

-- Eğer view varsa sil
IF OBJECT_ID('vw_AktifOdunc', 'V') IS NOT NULL
    DROP VIEW vw_AktifOdunc;
GO

CREATE VIEW vw_AktifOdunc
AS
SELECT 
    o.oduncID,
    k.kopyaID,
    kt.baslik AS kitap_basligi,
    y.ad + ' ' + y.soyad AS yazar,
    u.ad + ' ' + u.soyad AS kullanici,
    o.odunc_tarihi,
    o.iade_tarihi,
    o.durum
FROM Odunc o
INNER JOIN Kitap_Kopya k ON o.kopyaID = k.kopyaID
INNER JOIN Kitaplar kt ON k.kitapID = kt.kitapID
INNER JOIN Yazarlar y ON kt.yazarID = y.yazarID
INNER JOIN Kullanicilar u ON o.kullaniciID = u.kullaniciID
WHERE o.gercek_iade_tarihi IS NULL;
GO

