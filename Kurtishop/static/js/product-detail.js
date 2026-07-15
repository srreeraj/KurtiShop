// static/js/product-detail.js

let colorData = [];
let currentColorId = null;
let currentVariantId = null;
let currentStock = 0;

document.addEventListener('DOMContentLoaded', function () {
    initProductDetail();
});

function initProductDetail() {
    // Load color data from django json_script
    const jsonElement = document.getElementById('color-data');
    if (jsonElement) {
        try {
            colorData = JSON.parse(jsonElement.textContent);
        } catch (e) {
            console.error("Failed to parse color data", e);
        }
    }

    initColorSelection();
    setupEventListeners();
}

function setupEventListeners() {
    // Quantity buttons are handled inline via onclick for now
    // You can convert them to event listeners later if you want
}

// ===================== URL & State Management =====================
function getUrlParams() {
    return new URLSearchParams(window.location.search);
}

function updateUrl() {
    const params = getUrlParams();
    if (currentColorId) params.set('color', currentColorId);
    if (currentVariantId) params.set('variant', currentVariantId);

    const qty = parseInt(document.getElementById('quantity')?.value) || 1;
    if (qty > 1) params.set('qty', qty);
    else params.delete('qty');

    const newUrl = `${window.location.pathname}?${params.toString()}`;
    history.replaceState(null, '', newUrl);
}

// ===================== COLOR & SIZE SELECTION =====================
function selectColor(btn, colorId) {
    currentColorId = parseInt(colorId);

    // UI Update
    document.querySelectorAll('.color-swatch').forEach(b => {
        b.classList.remove('border-red-600', 'ring-2', 'ring-red-200');
    });
    btn.classList.add('border-red-600', 'ring-2', 'ring-red-200');

    const selected = colorData.find(c => c.color.id === currentColorId);
    if (!selected) return;

    document.getElementById('selected-color-name').textContent = selected.color.name;

    if (selected.images?.length > 0) {
        document.getElementById('main-image').src = selected.images[0].image.url;
    }

    rebuildThumbnails(selected.images);
    updateSizes(selected.variants);

    updateUrl();
}

function rebuildThumbnails(images) {
    const container = document.getElementById('thumbnail-container');
    container.innerHTML = '';

    images.forEach((img, index) => {
        const div = document.createElement('div');
        div.className = `thumbnail cursor-pointer rounded-xl overflow-hidden border-2 border-transparent hover:border-red-400 transition-all ${index === 0 ? 'border-red-600' : ''}`;
        div.innerHTML = `<img src="${img.image.url}" class="w-full aspect-square object-cover">`;
        div.onclick = () => changeMainImage(div);
        container.appendChild(div);
    });
}

function updateSizes(variants) {
    const container = document.getElementById('size-options');
    container.innerHTML = '';

    variants.forEach(variant => {
        const btn = document.createElement('button');
        btn.className = `px-6 py-3 border-2 rounded-2xl font-medium transition-all ${
            variant.stock > 0 ? 'border-gray-300 hover:border-red-600' : 'border-gray-200 text-gray-400 line-through cursor-not-allowed'
        }`;
        btn.textContent = variant.size.name;
        btn.dataset.variantId = variant.id;

        if (variant.stock > 0) {
            btn.onclick = () => selectSize(btn, variant.id, variant.stock);
        }
        container.appendChild(btn);
    });
}

function selectSize(btn, variantId, stock) {
    currentVariantId = variantId;
    currentStock = stock || 0;

    document.querySelectorAll('#size-options button').forEach(b => {
        b.classList.remove('border-red-600', 'bg-red-50');
    });
    btn.classList.add('border-red-600', 'bg-red-50');

    resetQuantity();
    updateUrl();
}

// ===================== IMAGE GALLERY =====================
function changeMainImage(thumb) {
    document.querySelectorAll('.thumbnail').forEach(t => t.classList.remove('border-red-600'));
    thumb.classList.add('border-red-600');
    document.getElementById('main-image').src = thumb.querySelector('img').src;
}

// ===================== QUANTITY =====================
function changeQty(change) {
    const input = document.getElementById('quantity');
    let qty = parseInt(input.value) || 1;
    qty = Math.max(1, Math.min(qty + change, currentStock || 1));
    input.value = qty;

    updateQuantityButtons();
    showStockInfo();
    updateUrl();
}

function updateQuantityButtons() {
    const qty = parseInt(document.getElementById('quantity').value) || 1;
    const minusBtn = document.querySelector('.qty-minus');
    const plusBtn = document.querySelector('.qty-plus');

    if (minusBtn) minusBtn.disabled = qty <= 1;
    if (plusBtn) plusBtn.disabled = qty >= currentStock;
}

function resetQuantity() {
    const input = document.getElementById('quantity');
    input.value = 1;
    updateQuantityButtons();
    showStockInfo();
}

function showStockInfo() {
    const stockEl = document.getElementById('stock-info');
    const qty = parseInt(document.getElementById('quantity').value) || 1;
    const remaining = currentStock - qty;

    if (remaining <= 0) {
        stockEl.textContent = "Out of stock";
        stockEl.className = "text-red-600 font-medium";
    } else if (remaining <= 5) {
        stockEl.textContent = `Only ${remaining} left in stock!`;
        stockEl.className = "text-amber-600 font-medium";
    } else {
        stockEl.textContent = "";
        stockEl.className = "";
    }
}

// ===================== ADD TO CART =====================
function addToCartDetail() {
    if (!currentVariantId) {
        alert("Please select a size first.");
        return;
    }

    const qty = parseInt(document.getElementById('quantity').value) || 1;

    if (qty > currentStock) {
        alert(`Sorry, only ${currentStock} items available.`);
        document.getElementById('quantity').value = currentStock;
        return;
    }

    const addBtn = document.querySelector('button[onclick="addToCartDetail()"]');
    const originalText = addBtn.textContent;

    addBtn.textContent = "ADDING...";
    addBtn.disabled = true;

    fetch(`/cart/add/${currentVariantId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `quantity=${qty}`
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            addBtn.textContent = "✓ ADDED!";
            addBtn.classList.add('bg-green-600');
            showToast(data.message);

            // Update navbar cart count
            document.dispatchEvent(new CustomEvent('cartUpdated', {
                detail: { cart_count: data.cart_count }
            }));

            setTimeout(() => {
                addBtn.textContent = originalText;
                addBtn.classList.remove('bg-green-600');
                addBtn.disabled = false;
            }, 1800);
        } else {
            alert(data.message || "Failed to add to cart");
            addBtn.textContent = originalText;
            addBtn.disabled = false;
        }
    })
    .catch(() => {
        alert("Something went wrong");
        addBtn.textContent = originalText;
        addBtn.disabled = false;
    });
}

// ===================== UTILITIES =====================
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showToast(message) {
    let toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.style.cssText = `
            position:fixed; bottom:20px; left:50%; transform:translateX(-50%);
            background:#166534; color:white; padding:16px 24px; border-radius:12px;
            z-index:10000; box-shadow:0 10px 15px -3px rgb(0 0 0 / 0.1);
        `;
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.style.opacity = '1';
    setTimeout(() => { toast.style.opacity = '0'; }, 2500);
}

// ===================== RESTORE FROM URL =====================
function initColorSelection() {
    const params = getUrlParams();
    let colorParam = params.get('color');
    let variantParam = params.get('variant');
    let qtyParam = parseInt(params.get('qty'));

    let targetBtn = colorParam 
        ? document.querySelector(`.color-swatch[data-color-id="${colorParam}"]`)
        : document.querySelector('.color-swatch');

    if (targetBtn) {
        targetBtn.click();

        setTimeout(() => {
            if (variantParam) {
                const sizeBtn = document.querySelector(`#size-options button[data-variant-id="${variantParam}"]`);
                if (sizeBtn) sizeBtn.click();
            }

            if (qtyParam && qtyParam > 1) {
                const qtyInput = document.getElementById('quantity');
                if (qtyInput) {
                    qtyInput.value = Math.min(qtyParam, currentStock || qtyParam);
                    updateQuantityButtons();
                    showStockInfo();
                }
            }
        }, 120);
    }
}

function toggleAccordion(btn) {
    const content = btn.nextElementSibling;
    const icon = btn.querySelector('span:last-child');

    content.classList.toggle('hidden');
    icon.textContent = content.classList.contains('hidden') ? '+' : '-';
}