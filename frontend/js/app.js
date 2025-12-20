// ============================================
// AKILLI KÜTÜPHANE YÖNETİM SİSTEMİ
// Ana Uygulama
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

// Global state
let kategoriler = [];
let yazarlar = [];
let kitaplar = [];

// ==================
// INITIALIZATION
// ==================

async function initApp() {
    // UI Event Listeners
    setupNavigation();
    setupModals();
    setupForms();
    setupSidebar();
    setupOduncTabs();  // Tab event listener'ları
    
    // Check login status
    updateAuthUI();
    
    // Load initial data
    await loadKategoriler();
    await loadYazarlar();
    await loadDashboard();
}

// Ödünç sayfası tab'ları için event listener
function setupOduncTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Aktif class'ı güncelle
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            // Tab'a göre veri yükle
            const tab = e.target.dataset.tab;
            loadOduncler(tab);
        });
    });
}

// ==================
// NAVIGATION
// ==================

function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            navigateTo(page);
        });
    });
    
    // Global search
    const searchInput = document.getElementById('globalSearch');
    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (e.target.value.length >= 2) {
                searchBooks(e.target.value);
            }
        }, 300);
    });
}

function navigateTo(page) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });
    
    // Update pages
    document.querySelectorAll('.page').forEach(p => {
        p.classList.toggle('active', p.id === `page-${page}`);
    });
    
    // Update title
    const titles = {
        'dashboard': 'Dashboard',
        'kitaplar': 'Kitaplar',
        'yazarlar': 'Yazarlar',
        'kategoriler': 'Kategoriler',
        'odunc': 'Ödünç İşlemleri',
        'kullanicilar': 'Kullanıcılar',
        'cezalar': 'Cezalar'
    };
    document.getElementById('pageTitle').textContent = titles[page] || page;
    
    // Load page data
    loadPageData(page);
}

async function loadPageData(page) {
    switch (page) {
        case 'dashboard':
            await loadDashboard();
            break;
        case 'kitaplar':
            await loadKitaplar();
            break;
        case 'yazarlar':
            await loadYazarlarTable();
            break;
        case 'kategoriler':
            await loadKategorilerGrid();
            break;
        case 'odunc':
            await loadOduncler();
            break;
        case 'kullanicilar':
            await loadKullanicilar();
            break;
        case 'cezalar':
            await loadCezalar();
            break;
    }
}

// ==================
// SIDEBAR
// ==================

function setupSidebar() {
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    
    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });
}

// ==================
// AUTH UI
// ==================

function updateAuthUI() {
    const loginBtn = document.getElementById('loginBtn');
    const userInfo = document.getElementById('userInfo');
    const user = api.getUser();
    
    if (api.isLoggedIn() && user) {
        loginBtn.style.display = 'none';
        userInfo.style.display = 'flex';
        document.getElementById('userName').textContent = `${user.ad} ${user.soyad}`;
        document.getElementById('userRole').textContent = getRoleText(user.rol);
    } else {
        loginBtn.style.display = 'flex';
        userInfo.style.display = 'none';
    }
}

function getRoleText(rol) {
    const roles = {
        'admin': 'Yönetici',
        'personel': 'Personel',
        'uye': 'Üye'
    };
    return roles[rol] || rol;
}

// ==================
// MODALS
// ==================

function setupModals() {
    // Login Modal
    document.getElementById('loginBtn').addEventListener('click', () => {
        openModal('loginModal');
    });
    
    // Logout
    document.getElementById('logoutBtn').addEventListener('click', () => {
        api.logout();
        updateAuthUI();
        showToast('Çıkış yapıldı', 'success');
        navigateTo('dashboard');
    });
    
    // Register/Login switch
    document.getElementById('showRegister').addEventListener('click', (e) => {
        e.preventDefault();
        closeModal('loginModal');
        openModal('registerModal');
    });
    
    document.getElementById('showLogin').addEventListener('click', (e) => {
        e.preventDefault();
        closeModal('registerModal');
        openModal('loginModal');
    });
    
    // Add buttons
    document.getElementById('addBookBtn')?.addEventListener('click', () => {
        if (!api.isLoggedIn()) {
            showToast('Giriş yapmanız gerekiyor', 'warning');
            return;
        }
        resetBookForm();
        document.getElementById('bookModalTitle').innerHTML = '<i class="fas fa-book"></i> Yeni Kitap';
        openModal('bookModal');
    });
    
    document.getElementById('newBorrowBtn')?.addEventListener('click', () => {
        if (!api.isLoggedIn()) {
            showToast('Giriş yapmanız gerekiyor', 'warning');
            return;
        }
        loadBorrowableBooks();
        openModal('borrowModal');
    });
    
    // Close buttons
    document.querySelectorAll('[data-close]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal');
            if (modal) closeModal(modal.id);
        });
    });
    
    // Click outside to close
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    });
}

function openModal(id) {
    document.getElementById(id).classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

// ==================
// FORMS
// ==================

function setupForms() {
    // Login Form
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const sifre = document.getElementById('loginPassword').value;
        
        try {
            await api.login(email, sifre);
            closeModal('loginModal');
            updateAuthUI();
            showToast('Giriş başarılı!', 'success');
            loadDashboard();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    // Register Form
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const userData = {
            ad: document.getElementById('regAd').value,
            soyad: document.getElementById('regSoyad').value,
            email: document.getElementById('regEmail').value,
            telefon: document.getElementById('regTelefon').value,
            sifre: document.getElementById('regPassword').value
        };
        
        try {
            await api.register(userData);
            closeModal('registerModal');
            showToast('Kayıt başarılı! Giriş yapabilirsiniz.', 'success');
            openModal('loginModal');
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    // Book Form
    document.getElementById('bookForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const bookId = document.getElementById('bookId').value;
        const bookData = {
            isbn: document.getElementById('bookIsbn').value,
            kitap_adi: document.getElementById('bookName').value,
            yazar_id: document.getElementById('bookAuthor').value || null,
            kategori_id: document.getElementById('bookCategory').value || null,
            yayin_yili: document.getElementById('bookYear').value || null,
            yayin_evi: document.getElementById('bookPublisher').value || null,
            sayfa_sayisi: document.getElementById('bookPages').value || null,
            dil: document.getElementById('bookLang').value,
            aciklama: document.getElementById('bookDesc').value || null,
            toplam_adet: parseInt(document.getElementById('bookTotal').value) || 1,
            mevcut_adet: parseInt(document.getElementById('bookAvailable').value) || 1
        };
        
        try {
            if (bookId) {
                await api.updateKitap(bookId, bookData);
                showToast('Kitap güncellendi!', 'success');
            } else {
                await api.createKitap(bookData);
                showToast('Kitap eklendi!', 'success');
            }
            closeModal('bookModal');
            loadKitaplar();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    // Borrow Form
    document.getElementById('borrowForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const kitapId = document.getElementById('borrowBook').value;
        const gun = parseInt(document.getElementById('borrowDays').value) || 0;
        const saat = parseInt(document.getElementById('borrowHours').value) || 0;
        const dakika = parseInt(document.getElementById('borrowMinutes').value) || 0;
        
        // En az bir süre girilmiş olmalı
        if (gun === 0 && saat === 0 && dakika === 0) {
            showToast('Lütfen bir süre belirleyin!', 'error');
            return;
        }
        
        try {
            await api.oduncAl(kitapId, gun, saat, dakika);
            closeModal('borrowModal');
            showToast('Kitap ödünç alındı!', 'success');
            loadOduncler();
            loadKitaplar();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    // Author Form
    document.getElementById('authorForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Admin kontrolü
        const user = api.getUser();
        if (!user || user.rol !== 'admin') {
            showToast('Bu işlem için admin yetkisi gerekiyor!', 'error');
            return;
        }
        
        const authorId = document.getElementById('authorId').value;
        const authorData = {
            ad: document.getElementById('authorAd').value,
            soyad: document.getElementById('authorSoyad').value,
            ulke: document.getElementById('authorUlke').value || null,
            biyografi: document.getElementById('authorBiyografi').value || null
        };
        
        try {
            if (authorId) {
                await api.updateYazar(authorId, authorData);
                showToast('Yazar güncellendi!', 'success');
            } else {
                await api.createYazar(authorData);
                showToast('Yazar eklendi!', 'success');
            }
            closeModal('authorModal');
            loadYazarlarTable();
            loadYazarlar(); // Dropdown'ları güncelle
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    // Category Form
    document.getElementById('categoryForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Admin kontrolü
        const user = api.getUser();
        if (!user || user.rol !== 'admin') {
            showToast('Bu işlem için admin yetkisi gerekiyor!', 'error');
            return;
        }
        
        const categoryId = document.getElementById('categoryId').value;
        const categoryData = {
            kategori_adi: document.getElementById('categoryAdi').value,
            aciklama: document.getElementById('categoryAciklama').value || null
        };
        
        try {
            if (categoryId) {
                await api.updateKategori(categoryId, categoryData);
                showToast('Kategori güncellendi!', 'success');
            } else {
                await api.createKategori(categoryData);
                showToast('Kategori eklendi!', 'success');
            }
            closeModal('categoryModal');
            loadKategorilerGrid();
            loadKategoriler(); // Dropdown'ları güncelle
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    // Add Author Button
    document.getElementById('addAuthorBtn')?.addEventListener('click', () => {
        const user = api.getUser();
        if (!user || user.rol !== 'admin') {
            showToast('Bu işlem için admin yetkisi gerekiyor!', 'error');
            return;
        }
        resetAuthorForm();
        document.getElementById('authorModalTitle').innerHTML = '<i class="fas fa-user-edit"></i> Yeni Yazar';
        openModal('authorModal');
    });
    
    // Add Category Button
    document.getElementById('addCategoryBtn')?.addEventListener('click', () => {
        const user = api.getUser();
        if (!user || user.rol !== 'admin') {
            showToast('Bu işlem için admin yetkisi gerekiyor!', 'error');
            return;
        }
        resetCategoryForm();
        document.getElementById('categoryModalTitle').innerHTML = '<i class="fas fa-folder-plus"></i> Yeni Kategori';
        openModal('categoryModal');
    });
    
    // Filters
    document.getElementById('kategoriFilter')?.addEventListener('change', loadKitaplar);
    document.getElementById('yazarFilter')?.addEventListener('change', loadKitaplar);
    document.getElementById('mevcutFilter')?.addEventListener('change', loadKitaplar);
}

// Form reset fonksiyonları
function resetAuthorForm() {
    document.getElementById('authorForm').reset();
    document.getElementById('authorId').value = '';
}

function resetCategoryForm() {
    document.getElementById('categoryForm').reset();
    document.getElementById('categoryId').value = '';
}

function resetBookForm() {
    document.getElementById('bookForm').reset();
    document.getElementById('bookId').value = '';
}

// ==================
// DATA LOADING
// ==================

async function loadDashboard() {
    try {
        // Stats
        if (api.isLoggedIn()) {
            const stats = await api.getDashboard();
            if (stats.data) {
                document.getElementById('statKitap').textContent = stats.data.ToplamKitap || 0;
                document.getElementById('statUye').textContent = stats.data.ToplamUye || 0;
                document.getElementById('statOdunc').textContent = stats.data.AktifOdunc || 0;
                document.getElementById('statGeciken').textContent = stats.data.GecikenKitap || 0;
            }
        }
        
        // Popular books
        const popular = await api.getPopulerKitaplar(5);
        const popularList = document.getElementById('popularBooks');
        
        if (popular.data && popular.data.length > 0) {
            popularList.innerHTML = popular.data.map((book, index) => `
                <li>
                    <span class="rank">${index + 1}</span>
                    <div class="book-info">
                        <div class="book-name">${book.KitapAdi}</div>
                        <div class="book-author">${book.YazarAdi || 'Bilinmiyor'}</div>
                    </div>
                    <span class="borrow-count">${book.OduncSayisi} ödünç</span>
                </li>
            `).join('');
        } else {
            popularList.innerHTML = '<li class="loading-item">Henüz veri yok</li>';
        }
        
    } catch (error) {
        console.error('Dashboard yükleme hatası:', error);
    }
}

async function loadKategoriler() {
    try {
        const result = await api.getKategoriler();
        kategoriler = result.data || [];
        
        // Populate filters
        const filter = document.getElementById('kategoriFilter');
        const bookCategory = document.getElementById('bookCategory');
        
        const options = kategoriler.map(k => 
            `<option value="${k.KategoriID}">${k.KategoriAdi}</option>`
        ).join('');
        
        if (filter) filter.innerHTML = '<option value="">Tüm Kategoriler</option>' + options;
        if (bookCategory) bookCategory.innerHTML = '<option value="">Seçiniz</option>' + options;
        
    } catch (error) {
        console.error('Kategori yükleme hatası:', error);
    }
}

async function loadYazarlar() {
    try {
        const result = await api.getYazarlar();
        yazarlar = result.data || [];
        
        // Populate filters
        const filter = document.getElementById('yazarFilter');
        const bookAuthor = document.getElementById('bookAuthor');
        
        const options = yazarlar.map(y => 
            `<option value="${y.YazarID}">${y.TamAd || y.Ad + ' ' + y.Soyad}</option>`
        ).join('');
        
        if (filter) filter.innerHTML = '<option value="">Tüm Yazarlar</option>' + options;
        if (bookAuthor) bookAuthor.innerHTML = '<option value="">Seçiniz</option>' + options;
        
    } catch (error) {
        console.error('Yazar yükleme hatası:', error);
    }
}

async function loadKitaplar() {
    const grid = document.getElementById('booksGrid');
    grid.innerHTML = '<div class="loading-overlay"><div class="spinner"></div></div>';
    
    try {
        const params = {
            kategori_id: document.getElementById('kategoriFilter')?.value,
            yazar_id: document.getElementById('yazarFilter')?.value,
            sadece_mevcut: document.getElementById('mevcutFilter')?.checked
        };
        
        const result = await api.araKitap(params);
        kitaplar = result.data || [];
        
        if (kitaplar.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-book-open"></i>
                    <h3>Kitap bulunamadı</h3>
                    <p>Filtreleri değiştirerek tekrar deneyin</p>
                </div>
            `;
            return;
        }
        
        grid.innerHTML = kitaplar.map(book => `
            <div class="book-card">
                <div class="book-cover">
                    <i class="fas fa-book"></i>
                </div>
                <div class="book-info">
                    <h3 class="book-title">${book.KitapAdi}</h3>
                    <p class="book-author">${book.YazarAdi || 'Bilinmiyor'}</p>
                    <div class="book-meta">
                        <span class="book-category">${book.KategoriAdi || 'Genel'}</span>
                        <span class="book-stock ${book.MevcutAdet > 0 ? 'available' : 'out'}">
                            ${book.MevcutAdet}/${book.ToplamAdet}
                        </span>
                    </div>
                    <div class="book-actions">
                        ${api.isLoggedIn() ? `
                            <button class="btn btn-sm btn-primary" onclick="editBook(${book.KitapID})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteBook(${book.KitapID})">
                                <i class="fas fa-trash"></i>
                            </button>
                        ` : ''}
                        ${book.MevcutAdet > 0 && api.isLoggedIn() ? `
                            <button class="btn btn-sm btn-success" onclick="quickBorrow(${book.KitapID})">
                                <i class="fas fa-hand-holding"></i> Ödünç Al
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        grid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-circle"></i>
                <h3>Yükleme hatası</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

async function loadYazarlarTable() {
    const tbody = document.getElementById('authorsBody');
    tbody.innerHTML = '<tr><td colspan="5" class="loading-item">Yükleniyor...</td></tr>';
    
    try {
        const result = await api.getYazarlar();
        
        if (!result.data || result.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="loading-item">Yazar bulunamadı</td></tr>';
            return;
        }
        
        const user = api.getUser();
        const isAdmin = user && user.rol === 'admin';
        
        tbody.innerHTML = result.data.map(y => `
            <tr>
                <td>${y.YazarID}</td>
                <td>${y.Ad} ${y.Soyad}</td>
                <td>${y.Ulke || '-'}</td>
                <td>${y.Biyografi ? y.Biyografi.substring(0, 50) + '...' : '-'}</td>
                <td>
                    ${isAdmin ? `
                        <button class="btn btn-sm btn-primary" onclick="editYazar(${y.YazarID})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteYazar(${y.YazarID})">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : '-'}
                </td>
            </tr>
        `).join('');
        
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="5" class="loading-item">${error.message}</td></tr>`;
    }
}

async function loadKategorilerGrid() {
    const grid = document.getElementById('categoriesGrid');
    grid.innerHTML = '<div class="loading-overlay"><div class="spinner"></div></div>';
    
    try {
        const result = await api.getKategoriler();
        
        if (!result.data || result.data.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-folder-open"></i>
                    <h3>Kategori bulunamadı</h3>
                </div>
            `;
            return;
        }
        
        const user = api.getUser();
        const isAdmin = user && user.rol === 'admin';
        
        const icons = ['fa-book', 'fa-rocket', 'fa-landmark', 'fa-brain', 'fa-child', 'fa-flask', 'fa-feather', 'fa-heart'];
        
        grid.innerHTML = result.data.map((k, i) => `
            <div class="category-card">
                <div class="category-icon">
                    <i class="fas ${icons[i % icons.length]}"></i>
                </div>
                <h3 class="category-name">${k.KategoriAdi}</h3>
                <p class="category-count">${k.Aciklama || 'Açıklama yok'}</p>
                ${isAdmin ? `
                    <div class="category-actions">
                        <button class="btn btn-sm btn-primary" onclick="editKategori(${k.KategoriID})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteKategori(${k.KategoriID})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                ` : ''}
            </div>
        `).join('');
        
    } catch (error) {
        grid.innerHTML = `<div class="empty-state"><p>${error.message}</p></div>`;
    }
}

// Aktif tab'ı takip et
let currentOduncTab = 'aktif';

async function loadOduncler(tab = null) {
    if (tab) currentOduncTab = tab;
    
    const tbody = document.getElementById('borrowsBody');
    tbody.innerHTML = '<tr><td colspan="7" class="loading-item">Yükleniyor...</td></tr>';
    
    if (!api.isLoggedIn()) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-item">Giriş yapmanız gerekiyor</td></tr>';
        return;
    }
    
    try {
        const user = api.getUser();
        const isAdmin = user && (user.rol === 'admin' || user.rol === 'personel');
        
        let result;
        
        // Tab'a göre veri çek
        switch (currentOduncTab) {
            case 'aktif':
                // Admin tüm aktif ödünçleri, üye kendi aktiflerini görür
                if (isAdmin) {
                    const allResult = await api.getOduncler();
                    result = {
                        data: allResult.data?.filter(o => o.Durum === 'odunc') || []
                    };
                } else {
                    result = await api.getAktifOdunclerim();
                }
                break;
                
            case 'geciken':
                // Admin tüm gecikenleri görür, üye kendi gecikenlerini
                if (isAdmin) {
                    result = await api.getGecikenKitaplar();
                } else {
                    const aktif = await api.getAktifOdunclerim();
                    result = {
                        data: aktif.data?.filter(o => o.GecikmeGunu > 0) || []
                    };
                }
                break;
                
            case 'gecmis':
                // Admin tüm geçmişi, üye kendi geçmişini görür
                if (isAdmin) {
                    const allResult = await api.getOduncler();
                    result = {
                        data: allResult.data?.filter(o => o.Durum === 'iade') || []
                    };
                } else {
                    const gecmis = await api.getOduncGecmisim();
                    result = {
                        data: gecmis.data?.filter(o => o.Durum === 'iade') || []
                    };
                }
                break;
                
            default:
                result = isAdmin ? await api.getOduncler() : await api.getOduncGecmisim();
        }
        
        if (!result.data || result.data.length === 0) {
            const emptyMessages = {
                'aktif': 'Aktif ödünç bulunmuyor',
                'geciken': 'Geciken kitap bulunmuyor',
                'gecmis': 'Geçmiş ödünç bulunmuyor'
            };
            tbody.innerHTML = `<tr><td colspan="7" class="loading-item">${emptyMessages[currentOduncTab] || 'Ödünç işlemi bulunamadı'}</td></tr>`;
            return;
        }
        
        tbody.innerHTML = result.data.map(o => `
            <tr>
                <td>${o.OduncID}</td>
                <td>${o.KitapAdi || '-'}</td>
                <td>${o.KullaniciAdi || (user?.ad + ' ' + user?.soyad) || '-'}</td>
                <td>${formatDate(o.OduncTarihi)}</td>
                <td>${formatDate(o.TeslimTarihi)}</td>
                <td>
                    <span class="badge ${getStatusBadge(o.Durum, o.GecikmeGunu)}">
                        ${getStatusText(o.Durum, o.GecikmeGunu)}
                    </span>
                </td>
                <td>
                    ${o.Durum === 'odunc' ? `
                        <button class="btn btn-sm btn-success" onclick="iadeEt(${o.OduncID})">
                            <i class="fas fa-undo"></i> İade Et
                        </button>
                    ` : '-'}
                </td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Ödünç yükleme hatası:', error);
        tbody.innerHTML = `<tr><td colspan="7" class="loading-item">${error.message}</td></tr>`;
    }
}

async function loadKullanicilar() {
    const tbody = document.getElementById('usersBody');
    tbody.innerHTML = '<tr><td colspan="7" class="loading-item">Yükleniyor...</td></tr>';
    
    if (!api.isLoggedIn()) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-item">Giriş yapmanız gerekiyor</td></tr>';
        return;
    }
    
    try {
        const result = await api.getKullanicilar();
        
        if (!result.data || result.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading-item">Kullanıcı bulunamadı</td></tr>';
            return;
        }
        
        tbody.innerHTML = result.data.map(u => `
            <tr>
                <td>${u.KullaniciID}</td>
                <td>${u.Ad} ${u.Soyad}</td>
                <td>${u.Email}</td>
                <td>${u.Telefon || '-'}</td>
                <td><span class="badge badge-info">${getRoleText(u.Rol)}</span></td>
                <td><span class="badge ${u.Durum ? 'badge-success' : 'badge-danger'}">
                    ${u.Durum ? 'Aktif' : 'Pasif'}
                </span></td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deleteKullanici(${u.KullaniciID})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="7" class="loading-item">${error.message}</td></tr>`;
    }
}

async function loadCezalar() {
    const tbody = document.getElementById('penaltiesBody');
    tbody.innerHTML = '<tr><td colspan="7" class="loading-item">Yükleniyor...</td></tr>';
    
    if (!api.isLoggedIn()) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-item">Giriş yapmanız gerekiyor</td></tr>';
        return;
    }
    
    try {
        // Kullanıcı rolünü kontrol et
        const user = api.getUser();
        const isAdmin = user && (user.rol === 'admin' || user.rol === 'personel');
        
        // Admin/Personel tüm cezaları, üye kendi cezalarını görür
        const result = isAdmin ? await api.getCezalar() : await api.getCezalarim();
        
        let total = 0;
        if (result.data) {
            result.data.forEach(c => {
                if (!c.OdenmeDurumu) total += (parseFloat(c.CezaTutari) || 0);
            });
        }
        document.getElementById('totalPenalty').textContent = `${(total || 0).toFixed(2)} TL`;
        
        if (!result.data || result.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading-item">Ceza bulunamadı</td></tr>';
            return;
        }
        
        tbody.innerHTML = result.data.map(c => `
            <tr>
                <td>${c.CezaID}</td>
                <td>${c.KullaniciAdi || user?.ad + ' ' + user?.soyad || '-'}</td>
                <td>${c.KitapAdi || '-'}</td>
                <td>${c.GecikmeGunu || 0} dakika</td>
                <td><strong>${(parseFloat(c.CezaTutari) || 0).toFixed(2)} TL</strong></td>
                <td>
                    <span class="badge ${c.OdenmeDurumu ? 'badge-success' : 'badge-danger'}">
                        ${c.OdenmeDurumu ? 'Ödendi' : 'Ödenmedi'}
                    </span>
                </td>
                <td>
                    ${!c.OdenmeDurumu ? `
                        <button class="btn btn-sm btn-success" onclick="cezaOde(${c.CezaID})">
                            <i class="fas fa-credit-card"></i> Öde
                        </button>
                    ` : '-'}
                </td>
            </tr>
        `).join('');
        
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="7" class="loading-item">${error.message}</td></tr>`;
    }
}

async function loadBorrowableBooks() {
    const select = document.getElementById('borrowBook');
    select.innerHTML = '<option value="">Yükleniyor...</option>';
    
    try {
        const result = await api.araKitap({ sadece_mevcut: true });
        
        if (result.data && result.data.length > 0) {
            select.innerHTML = '<option value="">Kitap Seçiniz</option>' + 
                result.data.map(b => 
                    `<option value="${b.KitapID}">${b.KitapAdi} (${b.MevcutAdet} mevcut)</option>`
                ).join('');
        } else {
            select.innerHTML = '<option value="">Mevcut kitap yok</option>';
        }
    } catch (error) {
        select.innerHTML = '<option value="">Hata oluştu</option>';
    }
}

// ==================
// ACTIONS
// ==================

async function searchBooks(query) {
    navigateTo('kitaplar');
    const result = await api.araKitap({ q: query });
    kitaplar = result.data || [];
    
    const grid = document.getElementById('booksGrid');
    if (kitaplar.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <h3>"${query}" için sonuç bulunamadı</h3>
            </div>
        `;
    } else {
        // Re-render with search results
        await loadKitaplar();
    }
}

async function editBook(id) {
    try {
        const result = await api.getKitap(id);
        const book = result.data;
        
        document.getElementById('bookId').value = book.KitapID;
        document.getElementById('bookIsbn').value = book.ISBN;
        document.getElementById('bookName').value = book.KitapAdi;
        document.getElementById('bookAuthor').value = book.YazarID || '';
        document.getElementById('bookCategory').value = book.KategoriID || '';
        document.getElementById('bookYear').value = book.YayinYili || '';
        document.getElementById('bookPublisher').value = book.YayinEvi || '';
        document.getElementById('bookPages').value = book.SayfaSayisi || '';
        document.getElementById('bookLang').value = book.Dil || 'Türkçe';
        document.getElementById('bookDesc').value = book.Aciklama || '';
        document.getElementById('bookTotal').value = book.ToplamAdet || 1;
        document.getElementById('bookAvailable').value = book.MevcutAdet || 1;
        
        document.getElementById('bookModalTitle').innerHTML = '<i class="fas fa-edit"></i> Kitap Düzenle';
        openModal('bookModal');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function deleteBook(id) {
    if (!confirm('Bu kitabı silmek istediğinizden emin misiniz?')) return;
    
    try {
        await api.deleteKitap(id);
        showToast('Kitap silindi!', 'success');
        loadKitaplar();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function quickBorrow(kitapId) {
    // Süre belirleme modalını aç
    document.getElementById('quickBorrowKitapId').value = kitapId;
    document.getElementById('quickBorrowDays').value = 0;
    document.getElementById('quickBorrowHours').value = 0;
    document.getElementById('quickBorrowMinutes').value = 5;
    openModal('quickBorrowModal');
}

async function confirmQuickBorrow() {
    const kitapId = document.getElementById('quickBorrowKitapId').value;
    const gun = parseInt(document.getElementById('quickBorrowDays').value) || 0;
    const saat = parseInt(document.getElementById('quickBorrowHours').value) || 0;
    const dakika = parseInt(document.getElementById('quickBorrowMinutes').value) || 0;
    
    // En az bir süre girilmiş olmalı
    if (gun === 0 && saat === 0 && dakika === 0) {
        showToast('Lütfen bir süre belirleyin!', 'error');
        return;
    }
    
    try {
        await api.oduncAl(kitapId, gun, saat, dakika);
        closeModal('quickBorrowModal');
        showToast('Kitap ödünç alındı!', 'success');
        loadKitaplar();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function iadeEt(oduncId) {
    try {
        const result = await api.iadeEt(oduncId);
        showToast(result.mesaj, 'success');
        loadOduncler();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function editYazar(id) {
    // Admin kontrolü
    const user = api.getUser();
    if (!user || user.rol !== 'admin') {
        showToast('Bu işlem için admin yetkisi gerekiyor!', 'error');
        return;
    }
    
    try {
        const result = await api.getYazar(id);
        if (result.data) {
            document.getElementById('authorId').value = result.data.YazarID;
            document.getElementById('authorAd').value = result.data.Ad || '';
            document.getElementById('authorSoyad').value = result.data.Soyad || '';
            document.getElementById('authorUlke').value = result.data.Ulke || '';
            document.getElementById('authorBiyografi').value = result.data.Biyografi || '';
            document.getElementById('authorModalTitle').innerHTML = '<i class="fas fa-user-edit"></i> Yazar Düzenle';
            openModal('authorModal');
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function deleteYazar(id) {
    // Admin kontrolü
    const user = api.getUser();
    if (!user || user.rol !== 'admin') {
        showToast('Bu işlem için admin yetkisi gerekiyor!', 'error');
        return;
    }
    
    if (!confirm('Bu yazarı silmek istediğinizden emin misiniz?')) return;
    
    try {
        await api.deleteYazar(id);
        showToast('Yazar silindi!', 'success');
        loadYazarlar();
        loadYazarlarTable();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function editKategori(id) {
    // Admin kontrolü
    const user = api.getUser();
    if (!user || user.rol !== 'admin') {
        showToast('Bu işlem için admin yetkisi gerekiyor!', 'error');
        return;
    }
    
    try {
        const result = await api.getKategori(id);
        if (result.data) {
            document.getElementById('categoryId').value = result.data.KategoriID;
            document.getElementById('categoryAdi').value = result.data.KategoriAdi || '';
            document.getElementById('categoryAciklama').value = result.data.Aciklama || '';
            document.getElementById('categoryModalTitle').innerHTML = '<i class="fas fa-folder"></i> Kategori Düzenle';
            openModal('categoryModal');
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function deleteKategori(id) {
    // Admin kontrolü
    const user = api.getUser();
    if (!user || user.rol !== 'admin') {
        showToast('Bu işlem için admin yetkisi gerekiyor!', 'error');
        return;
    }
    
    if (!confirm('Bu kategoriyi silmek istediğinizden emin misiniz?')) return;
    
    try {
        await api.deleteKategori(id);
        showToast('Kategori silindi!', 'success');
        loadKategoriler();
        loadKategorilerGrid();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function deleteKullanici(id) {
    if (!confirm('Bu kullanıcıyı silmek istediğinizden emin misiniz?')) return;
    
    try {
        await api.deleteKullanici(id);
        showToast('Kullanıcı silindi!', 'success');
        loadKullanicilar();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function cezaOde(id) {
    try {
        await api.cezaOde(id);
        showToast('Ceza ödendi!', 'success');
        loadCezalar();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ==================
// HELPERS
// ==================

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('tr-TR');
}

function getStatusBadge(durum, gecikme) {
    if (durum === 'iade') return 'badge-success';
    if (gecikme > 0) return 'badge-danger';
    return 'badge-warning';
}

function getStatusText(durum, gecikme) {
    if (durum === 'iade') return 'İade Edildi';
    if (gecikme > 0) {
        // Dakikayı gün/saat/dakika formatına çevir
        const gun = Math.floor(gecikme / (60 * 24));
        const kalan = gecikme % (60 * 24);
        const saat = Math.floor(kalan / 60);
        const dakika = kalan % 60;
        
        let gecikmeStr = '';
        if (gun > 0) gecikmeStr += `${gun}g `;
        if (saat > 0) gecikmeStr += `${saat}s `;
        if (dakika > 0 || (gun === 0 && saat === 0)) gecikmeStr += `${dakika}dk`;
        
        return `Gecikmiş (${gecikmeStr.trim()})`;
    }
    return 'Ödünç';
}

// ==================
// TOAST NOTIFICATIONS
// ==================

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}
