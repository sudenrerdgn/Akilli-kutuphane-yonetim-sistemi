# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# Güvenlik Helper - SQL Injection & XSS Koruması
# Tehlike kontrolü
# if SecurityHelper.check_sql_injection(user_input):
#     return "Tehlikeli içerik!"
#
# # Temizleme
# clean = SecurityHelper.sanitize_string(user_input)

import re
import html
from typing import Any, Optional


class SecurityHelper:
    """Güvenlik yardımcı sınıfı"""
    
    # Tehlikeli SQL kalıpları
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION)\b)",
        r"(--|#|\/\*|\*\/)",
        r"('\s*OR\s*'|'\s*AND\s*')",
        r"(;\s*DROP|;\s*DELETE|;\s*UPDATE)",
        r"(\bWAITFOR\b|\bDELAY\b)",
        r"(xp_cmdshell|sp_executesql)",
    ]
    
    # XSS kalıpları
    XSS_PATTERNS = [
        r"<script[^>]*>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
    ]
    
    @staticmethod
    def sanitize_string(value: Any) -> Optional[str]:
        """String temizle - HTML escape"""
        if value is None:
            return None
        return html.escape(str(value).strip())
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Email format kontrolü"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Telefon format kontrolü"""
        if not phone:
            return True
        clean = re.sub(r'[\s\-\(\)]', '', phone)
        return bool(re.match(r'^(\+90|0)?[0-9]{10}$', clean))
    
    @staticmethod
    def validate_length(value: str, min_len: int = 0, max_len: int = 255) -> bool:
        """Uzunluk kontrolü"""
        if value is None:
            return min_len == 0
        return min_len <= len(str(value)) <= max_len
    
    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """
        SQL Injection kontrolü
        True = TEHLİKELİ, False = Güvenli
        """
        if not value:
            return False
        value_upper = str(value).upper()
        for pattern in SecurityHelper.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def check_xss(value: str) -> bool:
        """
        XSS kontrolü
        True = TEHLİKELİ, False = Güvenli
        """
        if not value:
            return False
        for pattern in SecurityHelper.XSS_PATTERNS:
            if re.search(pattern, str(value), re.IGNORECASE):
                return True
        return False
