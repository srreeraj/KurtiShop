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
}

// ===================== CART COUNT =====================
function updateCartCount(count) {
    const cartCountEl = document.getElementById('cart-count');
    if (!cartCountEl) return;

    cartCountEl.textContent = count || 0;

    // Nice pop animation
    cartCountEl.classList.add('scale-125');
    setTimeout(() => {
        cartCountEl.classList.remove('scale-125');
    }, 300);
}

function initCartCount() {
    // Listen for cart updates from product pages, etc.
    document.addEventListener('cartUpdated', (e) => {
        if (e.detail && e.detail.cart_count !== undefined) {
            updateCartCount(e.detail.cart_count);
        }
    });

    // Optional: Fetch initial count on page load
    // You can improve this later with a dedicated lightweight endpoint
}

// Make updateCartCount available globally so other scripts can call it
window.updateCartCount = updateCartCount;