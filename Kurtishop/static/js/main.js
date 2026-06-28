const menuBtn = document.getElementById('menu-btn');
const mobileMenu = document.getElementById('mobile-menu');

if (menuBtn) {
    menuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
    });
}


let selectedVariantId = null;

function changeImage(el) {
    document.querySelectorAll('.thumbnail').forEach(t => t.classList.remove('border-red-600'));
    el.classList.add('border-red-600');
    document.getElementById('main-image').src = el.querySelector('img').src;
}

function selectSize(el, sizeName, variantId) {
    document.querySelectorAll('.size-btn').forEach(btn => btn.classList.remove('border-red-600', 'bg-red-50'));
    el.classList.add('border-red-600', 'bg-red-50');
    selectedVariantId = variantId;
}

function changeQty(amount) {
    const qty = document.getElementById('quantity');
    let value = parseInt(qty.value) || 1;
    value = Math.max(1, value + amount);
    qty.value = value;
}

function addToCartDetail(productId) {
    if (!selectedVariantId) {
        alert("Please select a size first!");
        return;
    }
    const qty = document.getElementById('quantity').value;
    alert(`✅ Added ${qty} item(s) to cart!`);
    // Later connect to real cart logic
}
