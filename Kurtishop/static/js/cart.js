// ==================== CART DRAWER JS ====================

function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Open / Close Drawer
function openCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-overlay');
    
    overlay.classList.remove('hidden');
    setTimeout(() => overlay.classList.add('opacity-100'), 10);
    drawer.classList.remove('translate-x-full');

    loadCartDrawer();
}

function closeCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-overlay');
    
    overlay.classList.remove('opacity-100');
    drawer.classList.add('translate-x-full');
    setTimeout(() => overlay.classList.add('hidden'), 300);
}

// Load Cart Content via AJAX
async function loadCartDrawer() {
    try {
        const res = await fetch('/cart/drawer/');
        const html = await res.text();
        document.getElementById('cart-drawer-content').innerHTML = html;
    } catch (e) {
        console.error("Failed to load cart", e);
    }
}

// Update Quantity in Drawer (Proper POST)
function updateDrawerQty(itemId, change) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/cart/update/${itemId}/`;
    form.style.display = 'none';

    const csrf = document.createElement('input');
    csrf.type = 'hidden';
    csrf.name = 'csrfmiddlewaretoken';
    csrf.value = getCSRFToken();
    form.appendChild(csrf);

    const qtyInput = document.createElement('input');
    qtyInput.type = 'hidden';
    qtyInput.name = 'quantity';
    qtyInput.value = change;        // We'll handle logic in view
    form.appendChild(qtyInput);

    document.body.appendChild(form);
    form.submit();
}

// Remove Item from Drawer
function removeFromDrawer(itemId) {
    if (confirm('Remove this item from cart?')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/cart/remove/${itemId}/`;
        form.style.display = 'none';

        const csrf = document.createElement('input');
        csrf.type = 'hidden';
        csrf.name = 'csrfmiddlewaretoken';
        csrf.value = getCSRFToken();
        form.appendChild(csrf);

        document.body.appendChild(form);
        form.submit();
    }
}

// Cart Icon Click
document.addEventListener('DOMContentLoaded', () => {
    const cartBtn = document.getElementById('cart-btn');
    if (cartBtn) {
        cartBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openCartDrawer();
        });
    }
});

// Close on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeCartDrawer();
});