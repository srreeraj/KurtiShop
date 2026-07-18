// static/js/navbar.js

document.addEventListener('DOMContentLoaded', function () {
    // Global safety net (belongs ideally on <body> in base.html, added here as fallback)
    document.documentElement.classList.add('overflow-x-hidden');
    document.body.classList.add('overflow-x-hidden', 'max-w-full');

    initNavbar();
    initCartCount();
});

// ---- class sets swapped on scroll (transparent <-> solid) ----
const NAVBAR_TRANSPARENT = ['bg-transparent'];
const NAVBAR_SOLID = ['bg-white', 'shadow-[0_1px_0_rgba(0,0,0,0.08)]'];

const LIGHT_TEXT = ['text-white'];
const DARK_TEXT = ['text-[#C1121F]'];

const LINK_LIGHT = ['text-white/90'];
const LINK_DARK = ['text-gray-700'];

function swap(el, addList, removeList) {
    if (!el) return;
    el.classList.remove(...removeList);
    el.classList.add(...addList);
}

function initNavbar() {
    const navbar = document.getElementById('main-navbar');
    const hamburgerBtn = document.getElementById('hamburger-btn');
    const logo = document.getElementById('nav-logo');
    const searchBtn = document.getElementById('search-btn');
    const cartBtn = document.getElementById('cart-btn');
    const navLinks = document.querySelectorAll('[data-nav-link]');
    const drawer = document.getElementById('mobile-drawer');
    const overlay = document.getElementById('drawer-overlay');
    const closeBtn = document.getElementById('drawer-close-btn');
    const searchInput = document.getElementById('search-input');

    function setSolid(isSolid) {
        swap(navbar, isSolid ? NAVBAR_SOLID : NAVBAR_TRANSPARENT, isSolid ? NAVBAR_TRANSPARENT : NAVBAR_SOLID);
        swap(logo, isSolid ? DARK_TEXT : LIGHT_TEXT, isSolid ? LIGHT_TEXT : DARK_TEXT);
        swap(hamburgerBtn, isSolid ? DARK_TEXT : LIGHT_TEXT, isSolid ? LIGHT_TEXT : DARK_TEXT);
        swap(searchBtn, isSolid ? DARK_TEXT : LIGHT_TEXT, isSolid ? LIGHT_TEXT : DARK_TEXT);
        swap(cartBtn, isSolid ? DARK_TEXT : LIGHT_TEXT, isSolid ? LIGHT_TEXT : DARK_TEXT);
        navLinks.forEach(link => swap(link, isSolid ? LINK_DARK : LINK_LIGHT, isSolid ? LINK_LIGHT : LINK_DARK));
    }

    function handleScroll() {
        if (navbar.dataset.forceSolid === 'true') return; // already solid, never goes transparent
        setSolid(window.scrollY > 60);
    }
    window.addEventListener('scroll', handleScroll, { passive: true });

    // Mobile Menu Drawer
    function openDrawer() {
        drawer.classList.add('!translate-x-0');
        overlay.classList.add('opacity-100', 'pointer-events-auto');
    }
    function closeDrawer() {
        drawer.classList.remove('!translate-x-0');
        overlay.classList.remove('opacity-100', 'pointer-events-auto');
    }

    hamburgerBtn.addEventListener('click', openDrawer);
    closeBtn.addEventListener('click', closeDrawer);
    overlay.addEventListener('click', closeDrawer);

    // Search Toggle (expand input)
    const INPUT_OPEN = ['w-[min(160px,30vw)]', 'opacity-100', 'border-b', 'border-gray-300', 'py-1'];
    const INPUT_CLOSED = ['w-0', 'opacity-0'];

    searchBtn.addEventListener('click', () => {
        const isOpen = searchInput.classList.contains('opacity-100');
        if (isOpen) {
            searchInput.classList.remove(...INPUT_OPEN);
            searchInput.classList.add(...INPUT_CLOSED);
        } else {
            searchInput.classList.remove(...INPUT_CLOSED);
            searchInput.classList.add(...INPUT_OPEN);
            searchInput.focus();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeDrawer();
            searchInput.classList.remove(...INPUT_OPEN);
            searchInput.classList.add(...INPUT_CLOSED);
            hideSuggestions();
        }
    });

    handleScroll();
    initSearch();
}

function initSearch() {
    const searchInput = document.getElementById('search-input');
    const suggestionsBox = document.getElementById('search-suggestions');
    let timeout = null;

    if (!searchInput || !suggestionsBox) return;

    function hideSuggestions() {
        suggestionsBox.classList.add('hidden');
        suggestionsBox.innerHTML = '';
    }

    async function fetchSuggestions(query) {
        try {
            const res = await fetch(`/products/search/suggestions/?q=${encodeURIComponent(query)}`);
            if (!res.ok) throw new Error('Failed');

            const data = await res.json();
            suggestionsBox.innerHTML = '';

            if (data.results.length === 0) {
                suggestionsBox.innerHTML = `<div class="px-4 py-8 text-center text-gray-500">No matches found for "${query}"</div>`;
                suggestionsBox.classList.remove('hidden');
                return;
            }

            const html = data.results.map(product => `
                <a href="/product/${product.slug}/"
                   class="flex gap-4 px-4 py-3 hover:bg-gray-50 group border-b border-gray-100 last:border-none">
                    <div class="w-16 h-16 flex-shrink-0 bg-gray-100 rounded-lg overflow-hidden">
                        ${product.image ?
                            `<img src="${product.image}" alt="${product.name}" class="w-full h-full object-cover">` :
                            `<div class="w-full h-full flex items-center justify-center text-xs text-gray-400">No img</div>`
                        }
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="font-medium text-sm line-clamp-2 group-hover:text-[#C1121F]">${product.name}</div>
                        <div class="text-xs text-gray-500">${product.category} ${product.occasion ? '• ' + product.occasion : ''}</div>
                        ${product.price ? `
                            <div class="flex items-baseline gap-2 mt-1">
                                <span class="font-semibold">₹${product.price}</span>
                                ${product.discount > 0 ? `<span class="text-xs text-gray-400 line-through">₹${product.original_price}</span>` : ''}
                            </div>
                        ` : ''}
                    </div>
                </a>
            `).join('');

            suggestionsBox.innerHTML = html;
            suggestionsBox.classList.remove('hidden');
        } catch (e) {
            console.error('Search suggestions error:', e);
        }
    }

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        clearTimeout(timeout);
        if (query.length < 2) {
            hideSuggestions();
            return;
        }
        timeout = setTimeout(() => fetchSuggestions(query), 300);
    });

    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            hideSuggestions();
        }
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === "Enter") {
            const query = searchInput.value.trim();
            if (query.length >= 2) {
                window.location.href = `/products/?search=${encodeURIComponent(query)}`;
            }
        }
    });
}

// ===================== CART COUNT =====================
function updateCartCount(count) {
    const cartCountEl = document.getElementById('cart-count');
    if (!cartCountEl) return;

    const newCount = parseInt(count) || 0;
    cartCountEl.textContent = newCount;

    if (newCount > 0) {
        cartCountEl.classList.add('scale-125');
        setTimeout(() => {
            cartCountEl.classList.remove('scale-125');
        }, 300);
    }
}

async function fetchCartCount() {
    try {
        const response = await fetch('/cart/count/');
        if (response.ok) {
            const data = await response.json();
            updateCartCount(data.cart_count);
        }
    } catch (error) {
        console.warn('Could not fetch cart count:', error);
    }
}

function initCartCount() {
    fetchCartCount();
    document.addEventListener('cartUpdated', (e) => {
        if (e.detail && e.detail.cart_count !== undefined) {
            updateCartCount(e.detail.cart_count);
        }
    });
}

window.updateCartCount = updateCartCount;