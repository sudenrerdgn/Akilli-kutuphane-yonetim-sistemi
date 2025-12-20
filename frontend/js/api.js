// ============================================
// AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
// API Helper
// ============================================

const API_BASE_URL = 'http://localhost:5000/api';

class ApiService {
    constructor() {
        this.token = localStorage.getItem('token');
    }

    // Token işlemleri
    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    }

    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    setUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    }

    isLoggedIn() {
        return !!this.token;
    }

    // HTTP headers
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    // Generic fetch wrapper
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            ...options,
            headers: this.getHeaders(options.auth !== false)
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.mesaj || 'Bir hata oluştu');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // ==================
    // AUTH ENDPOINTS
    // ==================

    async login(email, sifre) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, sifre }),
            auth: false
        });
        
        if (data.data && data.data.tokens) {
            this.setToken(data.data.tokens.access_token);
            this.setUser(data.data.kullanici);
        }
        
        return data;
    }

    async register(userData) {
        return await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
            auth: false
        });
    }

    async logout() {
        this.clearToken();
    }

    async getCurrentUser() {
        return await this.request('/auth/me');
    }

    async changePassword(eskiSifre, yeniSifre) {
        return await this.request('/auth/change-password', {
            method: 'POST',
            body: JSON.stringify({ eski_sifre: eskiSifre, yeni_sifre: yeniSifre })
        });
    }

    // ==================
    // KITAPLAR ENDPOINTS
    // ==================

    async getKitaplar() {
        return await this.request('/kitaplar', { auth: false });
    }

    async getKitap(id) {
        return await this.request(`/kitaplar/${id}`, { auth: false });
    }

    async araKitap(params = {}) {
        const query = new URLSearchParams();
        if (params.q) query.append('q', params.q);
        if (params.kategori_id) query.append('kategori_id', params.kategori_id);
        if (params.yazar_id) query.append('yazar_id', params.yazar_id);
        if (params.sadece_mevcut) query.append('sadece_mevcut', 'true');
        
        return await this.request(`/kitaplar/ara?${query}`, { auth: false });
    }

    async createKitap(kitap) {
        return await this.request('/kitaplar', {
            method: 'POST',
            body: JSON.stringify(kitap)
        });
    }

    async updateKitap(id, kitap) {
        return await this.request(`/kitaplar/${id}`, {
            method: 'PUT',
            body: JSON.stringify(kitap)
        });
    }

    async deleteKitap(id) {
        return await this.request(`/kitaplar/${id}`, {
            method: 'DELETE'
        });
    }

    // ==================
    // KULLANICILAR ENDPOINTS
    // ==================

    async getKullanicilar() {
        return await this.request('/kullanicilar');
    }

    async getKullanici(id) {
        return await this.request(`/kullanicilar/${id}`);
    }

    async updateKullanici(id, kullanici) {
        return await this.request(`/kullanicilar/${id}`, {
            method: 'PUT',
            body: JSON.stringify(kullanici)
        });
    }

    async deleteKullanici(id) {
        return await this.request(`/kullanicilar/${id}`, {
            method: 'DELETE'
        });
    }

    // ==================
    // YAZARLAR ENDPOINTS
    // ==================

    async getYazarlar() {
        return await this.request('/yazarlar', { auth: false });
    }

    async getYazar(id) {
        return await this.request(`/yazarlar/${id}`, { auth: false });
    }

    async createYazar(yazar) {
        return await this.request('/yazarlar', {
            method: 'POST',
            body: JSON.stringify(yazar)
        });
    }

    async updateYazar(id, yazar) {
        return await this.request(`/yazarlar/${id}`, {
            method: 'PUT',
            body: JSON.stringify(yazar)
        });
    }

    async deleteYazar(id) {
        return await this.request(`/yazarlar/${id}`, {
            method: 'DELETE'
        });
    }

    // ==================
    // KATEGORILER ENDPOINTS
    // ==================

    async getKategoriler() {
        return await this.request('/kategoriler', { auth: false });
    }

    async getKategori(id) {
        return await this.request(`/kategoriler/${id}`, { auth: false });
    }

    async createKategori(kategori) {
        return await this.request('/kategoriler', {
            method: 'POST',
            body: JSON.stringify(kategori)
        });
    }

    async updateKategori(id, kategori) {
        return await this.request(`/kategoriler/${id}`, {
            method: 'PUT',
            body: JSON.stringify(kategori)
        });
    }

    async deleteKategori(id) {
        return await this.request(`/kategoriler/${id}`, {
            method: 'DELETE'
        });
    }

    // ==================
    // ODUNC ENDPOINTS
    // ==================

    async getOduncler() {
        return await this.request('/odunc');
    }

    async getOdunc(id) {
        return await this.request(`/odunc/${id}`);
    }

    async getOduncGecmisim() {
        return await this.request('/odunc/gecmisim');
    }

    async getAktifOdunclerim() {
        return await this.request('/odunc/aktif');
    }

    async getGecikenKitaplar() {
        return await this.request('/odunc/geciken');
    }

    async oduncAl(kitapId, gun = 0, saat = 0, dakika = 0) {
        return await this.request('/odunc/al', {
            method: 'POST',
            body: JSON.stringify({ 
                kitap_id: parseInt(kitapId), 
                gun: parseInt(gun) || 0,
                saat: parseInt(saat) || 0,
                dakika: parseInt(dakika) || 0
            })
        });
    }

    async iadeEt(oduncId) {
        return await this.request(`/odunc/iade/${oduncId}`, {
            method: 'POST'
        });
    }

    // ==================
    // CEZALAR ENDPOINTS
    // ==================

    async getCezalar() {
        return await this.request('/cezalar');
    }

    async getCezalarim() {
        return await this.request('/cezalar/benim');
    }

    async getOdenmemisCezalarim() {
        return await this.request('/cezalar/odenmemis');
    }

    async cezaOde(cezaId) {
        return await this.request(`/cezalar/ode/${cezaId}`, {
            method: 'POST'
        });
    }

    // ==================
    // ISTATISTIKLER ENDPOINTS
    // ==================

    async getDashboard() {
        return await this.request('/istatistikler/dashboard');
    }

    async getPopulerKitaplar(limit = 10) {
        return await this.request(`/istatistikler/populer-kitaplar?limit=${limit}`, { auth: false });
    }

    async getAktifUyeler(limit = 10) {
        return await this.request(`/istatistikler/aktif-uyeler?limit=${limit}`);
    }
}

// Singleton instance
const api = new ApiService();
