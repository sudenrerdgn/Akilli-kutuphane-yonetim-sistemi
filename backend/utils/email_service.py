# ============================================
# AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
# E-posta Servisi
# ============================================

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from datetime import datetime

class EmailService:
    """E-posta Gönderim Servisi"""
    
    @staticmethod
    def send_email(to_email: str, subject: str, body: str, html_body: str = None):
        """E-posta gönderir"""
        try:
            mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            mail_port = current_app.config.get('MAIL_PORT', 587)
            mail_username = current_app.config.get('MAIL_USERNAME')
            mail_password = current_app.config.get('MAIL_PASSWORD')
            
            if not mail_username or not mail_password:
                print("E-posta ayarları yapılandırılmamış.")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = mail_username
            msg['To'] = to_email
            
            # Plain text
            part1 = MIMEText(body, 'plain', 'utf-8')
            msg.attach(part1)
            
            # HTML (opsiyonel)
            if html_body:
                part2 = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(part2)
            
            with smtplib.SMTP(mail_server, mail_port) as server:
                server.starttls()
                server.login(mail_username, mail_password)
                server.sendmail(mail_username, to_email, msg.as_string())
            
            return True
        except Exception as e:
            print(f"E-posta gönderim hatası: {e}")
            return False
    
    @staticmethod
    def send_late_return_notification(user_email: str, user_name: str, 
                                       book_title: str, due_date: datetime, 
                                       days_overdue: int, penalty: float):
        """Geç iade bildirimi gönderir"""
        subject = f"⚠️ Kütüphane - Geciken Kitap Bildirimi: {book_title}"
        
        body = f"""
Sayın {user_name},

Kütüphanemizden ödünç aldığınız "{book_title}" isimli kitabın iade tarihi geçmiştir.

Detaylar:
- Kitap: {book_title}
- Son Teslim Tarihi: {due_date.strftime('%d/%m/%Y')}
- Gecikme Süresi: {days_overdue} gün
- Tahakkuk Eden Ceza: {penalty:.2f} TL

Lütfen en kısa sürede kitabı iade ediniz.

Saygılarımızla,
Kütüphane Yönetimi
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .details {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .details table {{ width: 100%; }}
        .details td {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
        .penalty {{ color: #dc3545; font-weight: bold; font-size: 1.2em; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Kütüphane Bildirimi</h1>
        </div>
        <div class="content">
            <p>Sayın <strong>{user_name}</strong>,</p>
            
            <div class="warning">
                ⚠️ Kütüphanemizden ödünç aldığınız kitabın iade tarihi geçmiştir.
            </div>
            
            <div class="details">
                <table>
                    <tr>
                        <td><strong>📖 Kitap:</strong></td>
                        <td>{book_title}</td>
                    </tr>
                    <tr>
                        <td><strong>📅 Son Teslim Tarihi:</strong></td>
                        <td>{due_date.strftime('%d/%m/%Y')}</td>
                    </tr>
                    <tr>
                        <td><strong>⏰ Gecikme Süresi:</strong></td>
                        <td>{days_overdue} gün</td>
                    </tr>
                    <tr>
                        <td><strong>💰 Tahakkuk Eden Ceza:</strong></td>
                        <td class="penalty">{penalty:.2f} TL</td>
                    </tr>
                </table>
            </div>
            
            <p>Lütfen en kısa sürede kitabı iade ediniz. Her geçen gün için <strong>5.00 TL</strong> ceza uygulanmaktadır.</p>
        </div>
        <div class="footer">
            <p>Saygılarımızla,<br><strong>Kütüphane Yönetimi</strong></p>
            <p>Bu e-posta otomatik olarak gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return EmailService.send_email(user_email, subject, body, html_body)
    
    @staticmethod
    def send_welcome_email(user_email: str, user_name: str):
        """Hoş geldiniz e-postası gönderir"""
        subject = "🎉 Kütüphane Sistemine Hoş Geldiniz!"
        
        body = f"""
Sayın {user_name},

Kütüphane sistemimize başarıyla kayıt oldunuz!

Artık sistemimiz üzerinden:
- Kitap arayabilir
- Kitap ödünç alabilir
- Ödünç geçmişinizi görüntüleyebilirsiniz

İyi okumalar dileriz!

Saygılarımızla,
Kütüphane Yönetimi
        """
        
        return EmailService.send_email(user_email, subject, body)
