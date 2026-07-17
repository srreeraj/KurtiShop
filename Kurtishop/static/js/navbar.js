// static/js/navbar.js

document.addEventListener('DOMContentLoaded', function () {
    initNavbar();
    initCartCount();
});

function initNavbar() {
    const navbar = document.getElementById('main-navbar');
    const hamburgerBtn = document.getElementById('hamburger-btn');
    const drawer = document.getElementById('mobile-drawer');
    const overlay = document.getElementById('drawer-overlay');
    const closeBtn = document.getElementById('drawer-close-btn');
    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.getElementById('search-input');

    // Scroll Effect
    function handleScroll() {
        if (navbar.dataset.forceSolid === 'true') return;
        if (window.scrollY > 60) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }

    window.addEventListener('scroll', handleScroll, { passive: true });

    // Mobile Menu Drawer
    function openDrawer() {
        drawer.classList.add('!translate-x-0');
        overlay.classList.add('opacity-100', 'pointer-events-auto');
        hamburgerBtn.classList.add('open');
    }

    function closeDrawer() {
        drawer.classList.remove('!translate-x-0');
        overlay.classList.remove('opacity-100', 'pointer-events-auto');
        hamburgerBtn.classList.remove('open');
    }

    hamburgerBtn.addEventListener('click', openDrawer);
    closeBtn.addEventListener('click', closeDrawer);
    overlay.addEventListener('click', closeDrawer);

    // Search Toggle
    searchBtn.addEventListener('click', () => {
        searchInput.classList.toggle('open');
        if (searchInput.classList.contains('open')) {
            searchInput.focus();
        }
    });

    // Keyboard Support
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeDrawer();
            searchInput.classList.remove('open');
        }
    });

    // Initial scroll check
    handleScroll();

    // ==================== SEARCH WITH SUGGESTIONS ====================
    function initSearch() {
        const searchInput = document.getElementById('search-input');
        const suggestionsBox = document.getElementById('search-suggestions');
        let timeout = null;

        if (!searchInput) return;

    function hideSuggestions() {
        suggestionsBox.classList.add('hidden');
        suggestionsBox.innerHTML = '';
    }

    async function fetchSuggestions(query) {
        try {
            const res = await fetch(`/search/suggestions/?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            
            suggestionsBox.innerHTML = '';
            
            if (data.results.length === 0) {
                suggestionsBox.innerHTML = `<div class="px-4 py-8 text-center text-gray-500">No matches found</div>`;
                suggestionsBox.classList.remove('hidden');
                return;
            }

            const html = data.results.map(product => `
                <a href="/product/${product.slug}/" 
                   class="flex gap-4 px-4 py-3 hover:bg-gray-50 group">
                    <div class="w-16 h-16 flex-shrink-0 bg-gray-100 rounded-lg overflow-hidden">
                        ${product.image ? 
                            `<img src="${product.image}" alt="${product.name}" class="w-full h-full object-cover">` : 
                            `<div class="w-full h-full flex items-center justify-center text-xs text-gray-400">No img</div>`
                        }
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="font-medium text-sm line-clamp-2 group-hover:text-brand">${product.name}</div>
                        <div class="text-xs text-gray-500">${product.category} ${product.occasion ? '• ' + product.occasion : ''}</div>
                        ${product.price ? `
                            <div class="flex items-baseline gap-2 mt-1">
                                <span class="font-semibold">₹${product.price}</span>
                                ${product.discount > 0 ? 
                                    `<span class="text-xs text-gray-400 line-through">₹${product.original_price}</span>` : ''}
                            </div>
                        ` : ''}
                    </div>
                </a>
            `).join('');

            suggestionsBox.innerHTML = html;
            suggestionsBox.classList.remove('hidden');
        } catch (e) {
            console.error('Search error', e);
        }
    }

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        clearTimeout(timeout);
        
        if (query.length < 2) {
            hideSuggestions();
            return;
        }

        timeout = setTimeout(() => {
            fetchSuggestions(query);
        }, 250); // debounce
    });

    // Hide on click outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            hideSuggestions();
        }
    });

    // Keyboard: Enter → full search (optional)
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `/products/?search=${encodeURIComponent(query)}`; // we'll create this later
            }
        }
    });
}

// Call it
initSearch();
}

// ===================== CART COUNT =====================
function updateCartCount(count) {
    const cartCountEl = document.getElementById('cart-count');
    if (!cartCountEl) return;

    const newCount = parseInt(count) || 0;
    cartCountEl.textContent = newCount;

    // Optional: only animate if count actually changed
    if (newCount > 0) {
        cartCountEl.classList.add('scale-125');
        setTimeout(() => {
            cartCountEl.classList.remove('scale-125');
        }, 300);
    }
}

async function fetchCartCount() {
    try {
        const response = await fetch('/cart/count/');  // Adjust if you use app_name
        if (response.ok) {
            const data = await response.json();
            updateCartCount(data.cart_count);
        }
    } catch (error) {
        console.warn('Could not fetch cart count:', error);
    }
}

function initCartCount() {
    // Fetch initial count when page loads
    fetchCartCount();

    // Listen for updates from add-to-cart, etc.
    document.addEventListener('cartUpdated', (e) => {
        if (e.detail && e.detail.cart_count !== undefined) {
            updateCartCount(e.detail.cart_count);
        }
    });
}

// Make it globally available
window.updateCartCount = updateCartCount;