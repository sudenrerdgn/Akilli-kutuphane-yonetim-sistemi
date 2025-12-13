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
    
    // Check login status
    updateAuthUI();
    
    // Load initial data
    await loadKategoriler();
    await loadYazarlar();
    await loadDashboard();
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
    
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (e.target.value.length >= 2) {
                    searchBooks(e.target.value);
                }
            }, 300);
        });
    }
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
    
    if (toggle && sidebar) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }
}

// ==================
// AUTH UI
// ==================

function updateAuthUI() {
    const loginBtn = document.getElementById('loginBtn');
    const userInfo = document.getElementById('userInfo');
    const user = api.getUser();
    
    if (api.isLoggedIn() && user) {
        if (loginBtn) loginBtn.style.display = 'none';
        if (userInfo) {
            userInfo.style.display = 'flex';
            document.getElementById('userName').textContent = `${user.ad} ${user.soyad}`;
            document.getElementById('userRole').textContent = getRoleText(user.rol);
        }
    } else {
        if (loginBtn) loginBtn.style.display = 'flex';
        if (userInfo) userInfo.style.display = 'none';
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
    document.getElementById('loginBtn')?.addEventListener('click', () => {
        openModal('loginModal');
    });
    
    // Logout
    document.getElementById('logoutBtn')?.addEventListener('click', () => {
        api.logout();
        updateAuthUI();
        showToast('Çıkış yapıldı', 'success');
        navigateTo('dashboard');
    });
    
    // Register/Login switch
    document.getElementById('showRegister')?.addEventListener('click', (e) => {
        e.preventDefault();
        closeModal('loginModal');
        openModal('registerModal');
    });
    
    document.getElementById('showLogin')?.addEventListener('click', (e) => {
        e.preventDefault();
        closeModal('registerModal');
        openModal('loginModal');
    });
    
    // Add Book button
    document.getElementById('addBookBtn')?.addEventListener('click', () => {
        if (!api.isLoggedIn()) {
            showToast('Giriş yapmanız gerekiyor', 'warning');
            return;
        }
        resetBookForm();
        document.getElementById('bookModalTitle').innerHTML = '<i class="fas fa-book"></i> Yeni Kitap';
        openModal('bookModal');
    });
    
    // Add Author button
    document.getElementById('addAuthorBtn')?.addEventListener('click', () => {
        if (!api.isLoggedIn()) {
            showToast('Giriş yapmanız gerekiyor', 'warning');
            return;
        }
        resetAuthorForm();
        document.getElementById('authorModalTitle').innerHTML = '<i class="fas fa-user"></i> Yeni Yazar';
        openModal('authorModal');
    });
    
    // Add Category button
    document.getElementById('addCategoryBtn')?.addEventListener('click', () => {
        if (!api.isLoggedIn()) {
            showToast('Giriş yapmanız gerekiyor', 'warning');
            return;
        }
        resetCategoryForm();
        document.getElementById('categoryModalTitle').innerHTML = '<i class="fas fa-folder"></i> Yeni Kategori';
        openModal('categoryModal');
    });
    
    // Add User button
    document.getElementById('addUserBtn')?.addEventListener('click', () => {
        if (!api.isLoggedIn()) {
            showToast('Giriş yapmanız gerekiyor', 'warning');
            return;
        }
        resetUserForm();
        document.getElementById('userModalTitle').innerHTML = '<i class="fas fa-user-plus"></i> Yeni Kullanıcı';
        openModal('userModal');
    });
    
    // New Borrow button
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
    const modal = document.getElementById(id);
    if (modal) modal.classList.add('active');
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove('active');
}

// ==================
// FORMS
// ==================

function setupForms() {
    // Login Form
    document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
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
    document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
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
    document.getElementById('bookForm')?.addEventListener('submit', async (e) => {
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
    
    // Author Form
    document.getElementById('authorForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const authorId = document.getElementById('authorId').value;
        const authorData = {
            ad: document.getElementById('authorAd').value,
            soyad: document.getElementById('authorSoyad').value,
            biyografi: document.getElementById('authorBio').value || null,
            ulke: document.getElementById('authorCountry').value || null
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
            await loadYazarlar();
            await loadYazarlarTable();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    // Category Form
    document.getElementById('categoryForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const categoryId = document.getElementById('categoryId').value;
        const categoryData = {
            kategori_adi: document.getElementById('categoryName').value,
            aciklama: document.getElementById('categoryDesc').value || null
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
            await loadKategoriler();
            await loadKategorilerGrid();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    // User Form (Admin adding new user)
    document.getElementById('userForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userData = {
            ad: document.getElementById('userAd').value,
            soyad: document.getElementById('userSoyad').value,
            email: document.getElementById('userEmail').value,
            telefon: document.getElementById('userTelefon').value || null,
            sifre: document.getElementById('userPassword').value
        };
        
        try {
            await api.register(userData);
            closeModal('userModal');
            showToast('Kullanıcı eklendi!', 'success');
            loadKullanicilar();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    // Borrow Form
    document.getElementById('borrowForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const kitapId = parseInt(document.getElementById('borrowBook').value);
        const gun = parseInt(document.getElementById('borrowDays').value) || 14;
        
        if (!kitapId) {
            showToast('Lütfen bir kitap seçin', 'warning');
            return;
        }
        
        try {
            await api.oduncAl(kitapId, gun);
            closeModal('borrowModal');
            showToast('Kitap ödünç alındı!', 'success');
            loadOduncler();
            loadKitaplar();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    // Filters
    document.getElementById('kategoriFilter')?.addEventListener('change', loadKitaplar);
    document.getElementById('yazarFilter')?.addEventListener('change', loadKitaplar);
    document.getElementById('mevcutFilter')?.addEventListener('change', loadKitaplar);
}

function resetBookForm() {
    document.getElementById('bookForm')?.reset();
    const bookId = document.getElementById('bookId');
    if (bookId) bookId.value = '';
}

function resetAuthorForm() {
    document.getElementById('authorForm')?.reset();
    const authorId = document.getElementById('authorId');
    if (authorId) authorId.value = '';
}

function resetCategoryForm() {
    document.getElementById('categoryForm')?.reset();
    const categoryId = document.getElementById('categoryId');
    if (categoryId) categoryId.value = '';
}

function resetUserForm() {
    document.getElementById('userForm')?.reset();
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
        
        if (popularList) {
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
    if (!grid) return;
    
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
    if (!tbody) return;
    
    tbody.innerHTML = '<tr><td colspan="5" class="loading-item">Yükleniyor...</td></tr>';
    
    try {
        const result = await api.getYazarlar();
        
        if (!result.data || result.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="loading-item">Yazar bulunamadı</td></tr>';
            return;
        }
        
        tbody.innerHTML = result.data.map(y => `
            <tr>
                <td>${y.YazarID}</td>
                <td>${y.Ad} ${y.Soyad}</td>
                <td>${y.Ulke || '-'}</td>
                <td>${y.Biyografi ? y.Biyografi.substring(0, 50) + '...' : '-'}</td>
                <td>
                    ${api.isLoggedIn() ? `
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
    if (!grid) return;
    
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
        
        const icons = ['fa-book', 'fa-rocket', 'fa-landmark', 'fa-brain', 'fa-child', 'fa-flask', 'fa-feather', 'fa-heart'];
        
        grid.innerHTML = result.data.map((k, i) => `
            <div class="category-card">
                <div class="category-icon">
                    <i class="fas ${icons[i % icons.length]}"></i>
                </div>
                <h3 class="category-name">${k.KategoriAdi}</h3>
                <p class="category-count">${k.Aciklama || 'Açıklama yok'}</p>
                ${api.isLoggedIn() ? `
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

async function loadOduncler() {
    const tbody = document.getElementById('borrowsBody');
    if (!tbody) return;
    
    tbody.innerHTML = '<tr><td colspan="7" class="loading-item">Yükleniyor...</td></tr>';
    
    if (!api.isLoggedIn()) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-item">Giriş yapmanız gerekiyor</td></tr>';
        return;
    }
    
    try {
        const user = api.getUser();
        let result;
        
        // Rol bazlı endpoint seçimi
        if (user && (user.rol === 'admin' || user.rol === 'personel')) {
            // Admin/Personel tüm ödünçleri görebilir
            result = await api.getOduncler();
        } else {
            // Normal kullanıcı sadece kendi aktif ödünçlerini görebilir
            result = await api.getAktifOdunclerim();
        }
        
        if (!result.data || result.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading-item">Ödünç işlemi bulunamadı</td></tr>';
            return;
        }
        
        // Normal kullanıcı için farklı tablo yapısı (KullaniciAdi yok)
        if (user && user.rol === 'uye') {
            tbody.innerHTML = result.data.map(o => `
                <tr>
                    <td>${o.OduncID}</td>
                    <td>${o.KitapAdi}</td>
                    <td>${user.ad} ${user.soyad}</td>
                    <td>${formatDate(o.OduncTarihi)}</td>
                    <td>${formatDate(o.TeslimTarihi)}</td>
                    <td>
                        <span class="badge ${getStatusBadge('odunc', o.GecikmeGunu || 0)}">
                            ${getStatusText('odunc', o.GecikmeGunu || 0)}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-success" onclick="iadeEt(${o.OduncID})">
                            <i class="fas fa-undo"></i> İade Et
                        </button>
                    </td>
                </tr>
            `).join('');
        } else {
            // Admin/Personel için tam tablo
            tbody.innerHTML = result.data.map(o => `
                <tr>
                    <td>${o.OduncID}</td>
                    <td>${o.KitapAdi}</td>
                    <td>${o.KullaniciAdi}</td>
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
        }
        
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="7" class="loading-item">${error.message}</td></tr>`;
    }
}

async function loadKullanicilar() {
    const tbody = document.getElementById('usersBody');
    if (!tbody) return;
    
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
    if (!tbody) return;
    
    tbody.innerHTML = '<tr><td colspan="7" class="loading-item">Yükleniyor...</td></tr>';
    
    if (!api.isLoggedIn()) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-item">Giriş yapmanız gerekiyor</td></tr>';
        return;
    }
    
    try {
        const user = api.getUser();
        let result;
        
        // Rol bazlı endpoint seçimi
        if (user && (user.rol === 'admin' || user.rol === 'personel')) {
            // Admin/Personel tüm cezaları görebilir
            result = await api.getCezalar();
        } else {
            // Normal kullanıcı sadece kendi cezalarını görebilir
            result = await api.getCezalarim();
        }
        
        let total = 0;
        if (result.data) {
            result.data.forEach(c => {
                if (!c.OdenmeDurumu) total += c.CezaTutari;
            });
        }
        const totalEl = document.getElementById('totalPenalty');
        if (totalEl) totalEl.textContent = `${total.toFixed(2)} TL`;
        
        if (!result.data || result.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading-item">Ceza bulunamadı</td></tr>';
            return;
        }
        
        // Normal kullanıcı için farklı tablo yapısı (KullaniciAdi yok)
        if (user && user.rol === 'uye') {
            tbody.innerHTML = result.data.map(c => `
                <tr>
                    <td>${c.CezaID}</td>
                    <td>${user.ad} ${user.soyad}</td>
                    <td>${c.KitapAdi}</td>
                    <td>${c.GecikmeGunu} gün</td>
                    <td><strong>${c.CezaTutari.toFixed(2)} TL</strong></td>
                    <td>
                        <span class="badge ${c.OdenmeDurumu ? 'badge-success' : 'badge-danger'}">
                            ${c.OdenmeDurumu ? 'Ödendi' : 'Ödenmedi'}
                        </span>
                    </td>
                    <td>
                        ${!c.OdenmeDurumu ? `
                            <button class="btn btn-sm btn-success" onclick="cezaOde(${c.CezaID})">
                                <i class="fas fa-check"></i> Öde
                            </button>
                        ` : '-'}
                    </td>
                </tr>
            `).join('');
        } else {
            // Admin/Personel için tam tablo
            tbody.innerHTML = result.data.map(c => `
                <tr>
                    <td>${c.CezaID}</td>
                    <td>${c.KullaniciAdi}</td>
                    <td>${c.KitapAdi}</td>
                    <td>${c.GecikmeGunu} gün</td>
                    <td><strong>${c.CezaTutari.toFixed(2)} TL</strong></td>
                    <td>
                        <span class="badge ${c.OdenmeDurumu ? 'badge-success' : 'badge-danger'}">
                            ${c.OdenmeDurumu ? 'Ödendi' : 'Ödenmedi'}
                        </span>
                    </td>
                    <td>
                        ${!c.OdenmeDurumu ? `
                            <button class="btn btn-sm btn-success" onclick="cezaOde(${c.CezaID})">
                                <i class="fas fa-check"></i> Öde
                            </button>
                        ` : '-'}
                    </td>
                </tr>
            `).join('');
        }
        
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="7" class="loading-item">${error.message}</td></tr>`;
    }
}

async function loadBorrowableBooks() {
    const select = document.getElementById('borrowBook');
    if (!select) return;
    
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
    try {
        await api.oduncAl(kitapId);
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

// Yazar CRUD
async function editYazar(id) {
    try {
        const result = await api.getYazar(id);
        const yazar = result.data;
        
        document.getElementById('authorId').value = yazar.YazarID;
        document.getElementById('authorAd').value = yazar.Ad;
        document.getElementById('authorSoyad').value = yazar.Soyad;
        document.getElementById('authorBio').value = yazar.Biyografi || '';
        document.getElementById('authorCountry').value = yazar.Ulke || '';
        
        document.getElementById('authorModalTitle').innerHTML = '<i class="fas fa-edit"></i> Yazar Düzenle';
        openModal('authorModal');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function deleteYazar(id) {
    if (!confirm('Bu yazarı silmek istediğinizden emin misiniz?')) return;
    
    try {
        await api.deleteYazar(id);
        showToast('Yazar silindi!', 'success');
        await loadYazarlar();
        await loadYazarlarTable();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Kategori CRUD
async function editKategori(id) {
    try {
        const result = await api.getKategori(id);
        const kategori = result.data;
        
        document.getElementById('categoryId').value = kategori.KategoriID;
        document.getElementById('categoryName').value = kategori.KategoriAdi;
        document.getElementById('categoryDesc').value = kategori.Aciklama || '';
        
        document.getElementById('categoryModalTitle').innerHTML = '<i class="fas fa-edit"></i> Kategori Düzenle';
        openModal('categoryModal');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function deleteKategori(id) {
    if (!confirm('Bu kategoriyi silmek istediğinizden emin misiniz?')) return;
    
    try {
        await api.deleteKategori(id);
        showToast('Kategori silindi!', 'success');
        await loadKategoriler();
        await loadKategorilerGrid();
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
    if (gecikme > 0) return `Gecikmiş (${gecikme} gün)`;
    return 'Ödünç';
}

// ==================
// TOAST NOTIFICATIONS
// ==================

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
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
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}
