function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function updateQuantity(itemId, change) {
    const quantityInput = document.querySelector(`input[data-item-id="${itemId}"]`);
    let currentQty = parseInt(quantityInput.value);
    let newQty = currentQty + change;

    if (newQty < 1) {
        if (confirm('Remove this item from cart?')) {
            removeItem(itemId);
        }
        return;
    }

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/cart/update/${itemId}/`;
    form.style.display = 'none';

    // CSRF Token
    const csrf = document.createElement('input');
    csrf.type = 'hidden';
    csrf.name = 'csrfmiddlewaretoken';
    csrf.value = getCSRFToken();
    form.appendChild(csrf);

    // Quantity
    const qtyInput = document.createElement('input');
    qtyInput.type = 'hidden';
    qtyInput.name = 'quantity';
    qtyInput.value = newQty;
    form.appendChild(qtyInput);

    document.body.appendChild(form);
    form.submit()
}

function removeItem(itemId) {
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

async function loadCartDrawer() {
    try {
        const res = await fetch('/cart/drawer/');
        const html = await res.text();
        document.getElementById('cart-drawer-content').innerHTML = html;
    } catch(e) {
        console.error("Failed to load cart", e);
    }
}

// Update quantity in drawer
function updateDrawerQty(itemId, change) {
    // You can make this AJAX later. For now, full reload is fine.
    window.location.href = `/cart/update/${itemId}/?change=${change}`;
}

function removeFromDrawer(itemId) {
    if (confirm('Remove item?')) {
        window.location.href = `/cart/remove/${itemId}/`;
    }
}

// Add event listener in navbar
document.getElementById('cart-btn').addEventListener('click', (e) => {
    e.preventDefault();
    openCartDrawer();
});
