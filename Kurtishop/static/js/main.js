// ===================== NAVBAR =====================
const menuBtn = document.getElementById('menu-btn');
const mobileMenu = document.getElementById('mobile-menu');

if (menuBtn) {
    menuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
    });
}

// ===================== PRODUCT DETAIL PAGE =====================

// Change Main Image from Thumbnail
function changeMainImage(el) {
    document.querySelectorAll('.thumbnail').forEach(t => t.classList.remove('border-red-600'));
    el.classList.add('border-red-600');
    document.getElementById('main-image').src = el.querySelector('img').src;
}

// Size Selection
let selectedVariantId = null;

function selectSize(el, variantId) {
    document.querySelectorAll('.size-btn').forEach(btn => {
        btn.classList.remove('border-red-600', 'bg-red-600', 'text-white');
    });
    el.classList.add('border-red-600', 'bg-red-600', 'text-white');
    selectedVariantId = variantId;
}

// Quantity
function changeQty(amount) {
    const qtyInput = document.getElementById('quantity');
    if (!qtyInput) return;
    
    let qty = parseInt(qtyInput.value) || 1;
    qty = Math.max(1, qty + amount);
    qtyInput.value = qty;
}

// Add to Cart
function addToCartDetail() {
    if (!selectedVariantId) {
        alert("Please select a size first!");
        return;
    }
    const qty = document.getElementById('quantity').value || 1;
    alert(`✅ Added ${qty} item(s) to cart!`);
    // TODO: Later integrate with real cart system
}

// Accordion Toggle
function toggleAccordion(el) {
    const content = el.querySelector('.accordion-content');
    if (content) {
        content.classList.toggle('hidden');
    }
}

// Make functions globally available
window.changeMainImage = changeMainImage;
window.selectSize = selectSize;
window.changeQty = changeQty;
window.addToCartDetail = addToCartDetail;
window.toggleAccordion = toggleAccordion;