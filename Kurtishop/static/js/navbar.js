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