// ==================== CART DRAWER JS ====================

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

// Load Cart
async function loadCartDrawer() {
    try {
        const res = await fetch('/cart/drawer/');
        const html = await res.text();
        const content = document.getElementById('cart-drawer-content');
        content.innerHTML = html;
        
        setTimeout(attachDrawerListeners, 50); // Small delay to ensure DOM is ready
    } catch(e) {
        console.error("Failed to load cart", e);
    }
}

// Attach listeners to dynamic content
function attachDrawerListeners() {
    // Quantity buttons
    document.querySelectorAll('[data-action="update-qty"]').forEach(btn => {
        btn.addEventListener('click', async function() {
            const itemId = this.dataset.itemId;
            const change = parseInt(this.dataset.change);

            await updateQuantityAjax(itemId, change);
        });
    });

    // Remove buttons
    document.querySelectorAll('.remove-from-drawer').forEach(btn => {  // We'll add this class
        btn.addEventListener('click', async function() {
            if (confirm('Remove this item from cart?')) {
                await removeFromDrawerAjax(this.dataset.itemId);
            }
        });
    });
}

// AJAX Update Quantity
async function updateQuantityAjax(itemId, change) {
    const formData = new FormData();
    formData.append('quantity', change);
    formData.append('csrfmiddlewaretoken', getCSRFToken());

    try {
        const res = await fetch(`/cart/update/${itemId}/`, {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            loadCartDrawer(); // Refresh drawer
        } else {
            alert('Failed to update quantity');
        }
    } catch(e) {
        console.error(e);
    }
}

// AJAX Remove
async function removeFromDrawerAjax(itemId) {
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCSRFToken());

    try {
        const res = await fetch(`/cart/remove/${itemId}/`, {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            loadCartDrawer();
        }
    } catch(e) {
        console.error(e);
    }
}

// Open Drawer
function openCartDrawer() {
    const overlay = document.getElementById('cart-overlay');
    const drawer = document.getElementById('cart-drawer');
    
    overlay.classList.remove('hidden');
    setTimeout(() => overlay.classList.add('opacity-100'), 10);
    drawer.classList.remove('translate-x-full');

    loadCartDrawer();
}

function closeCartDrawer() {
    const overlay = document.getElementById('cart-overlay');
    const drawer = document.getElementById('cart-drawer');
    
    overlay.classList.remove('opacity-100');
    drawer.classList.add('translate-x-full');
    setTimeout(() => overlay.classList.add('hidden'), 300);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const cartBtn = document.getElementById('cart-btn');
    if (cartBtn) {
        cartBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openCartDrawer();
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeCartDrawer();
    });
});