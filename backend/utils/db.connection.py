# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Veritabanı Bağlantı Yönetimi
# ============================================
# DEĞİŞİKLİK: SQL INJECTION KORUMASI
# execute_stored_procedure() fonksiyonuna WHITELIST kontrolü eklendi.
# Sadece izin verilen procedure'ler çalıştırılabilir.


import pyodbc
import re
from flask import current_app
from contextlib import contextmanager


class DatabaseConnection:
    """SQL Server Veritabanı Bağlantı Sınıfı"""
    
    _instance = None
    
    # ==========================================
    # SQL INJECTION KORUMASI - WHITELIST
    ALLOWED_PROCEDURES = [
        'sp_KitapAra',
        'sp_KullaniciOduncGecmisi',
        'sp_GecikenKitaplar',
        'sp_Istatistikler',
        'sp_AylikRapor',
        'sp_KategoriKitapSayisi',
        'sp_YazarKitapListesi'
    ]
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_connection_string(self):
        """Bağlantı string'ini oluşturur"""
        try:
            host = current_app.config.get('SQLSERVER_HOST', '*****\\SQLEXPRESS')
            database = current_app.config.get('SQLSERVER_DATABASE', 'KutuphaneDB')
            username = current_app.config.get('SQLSERVER_USERNAME', 'sa')
            password = current_app.config.get('SQLSERVER_PASSWORD', '******')
            driver = current_app.config.get('SQLSERVER_DRIVER', 'ODBC Driver 17 for SQL Server')
        except RuntimeError:
            host = '****\\SQLEXPRESS'
            database = 'KutuphaneDB'
            username = 'sa'
            password = '*******'
            driver = 'ODBC Driver 17 for SQL Server'
        
        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={host};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )
    
    def get_connection(self):
        """Yeni bir veritabanı bağlantısı oluşturur"""
        try:
            connection_string = self.get_connection_string()
            conn = pyodbc.connect(connection_string)
            return conn
        except pyodbc.Error as e:
            print(f"Veritabanı bağlantı hatası: {e}")
            raise
    
    @contextmanager
    def get_cursor(self):
        """Context manager ile cursor yönetimi"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def execute_query(self, query, params=None):
        """SELECT sorgusu - Parameterized (güvenli)"""
        with self.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            columns = [column[0] for column in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def execute_non_query(self, query, params=None):
        """INSERT/UPDATE/DELETE - Parameterized (güvenli)"""
        with self.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.rowcount
    
    def execute_scalar(self, query, params=None):
        """Tek değer döndüren sorgu - Parameterized (güvenli)"""
        with self.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            row = cursor.fetchone()
            return row[0] if row else None
    
    def execute_insert_get_id(self, query, params=None):
        """INSERT + ID döndür - Parameterized (güvenli)"""
        with self.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            cursor.execute("SELECT SCOPE_IDENTITY()")
            row = cursor.fetchone()
            return int(row[0]) if row and row[0] else None
    
    # ==========================================
    # SQL INJECTION KORUMASI - WHITELIST KONTROL
    # ==========================================
    def _is_safe_procedure(self, proc_name: str) -> bool:
        """
        Stored procedure güvenlik kontrolü
        
        SADECE whitelist'teki procedure'ler çalıştırılabilir!
        """
        if not proc_name:
            return False
        
        # Whitelist kontrolü
        if proc_name not in self.ALLOWED_PROCEDURES:
            print(f"[GÜVENLİK] İzin verilmeyen procedure: {proc_name}")
            return False
        
        # Format kontrolü (sadece harf, rakam, alt çizgi)
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', proc_name):
            print(f"[GÜVENLİK] Geçersiz procedure adı: {proc_name}")
            return False
        
        return True
    
    def execute_stored_procedure(self, proc_name, params=None):
        """
        Stored Procedure çalıştırır
        
        SQL INJECTION KORUMASI:
        - proc_name WHITELIST kontrolünden geçer
        - Parametreler parameterized query ile gönderilir
        """
        # ==========================================
        # GÜVENLİK KONTROLÜ
        # ==========================================
        if not self._is_safe_procedure(proc_name):
            raise ValueError(f"İzin verilmeyen stored procedure: {proc_name}")
        
        with self.get_cursor() as cursor:
            if params:
                param_str = ', '.join(['?' for _ in params])
                cursor.execute(f"EXEC {proc_name} {param_str}", params)
            else:
                cursor.execute(f"EXEC {proc_name}")
            
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            return None
    
    def test_connection(self):
        """Bağlantı testi"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except:
            return False


# Singleton instance
db = DatabaseConnection()
