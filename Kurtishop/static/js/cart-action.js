// static/js/cart-actions.js

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

function showToast(message, type = 'success') {
    let toast = document.getElementById('global-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'global-toast';
        toast.style.cssText = `
            position:fixed; bottom:20px; left:50%; transform:translateX(-50%);
            padding:16px 24px; border-radius:12px; z-index:10000;
            box-shadow:0 10px 15px -3px rgb(0 0 0 / 0.1);
            font-weight:500;
        `;
        document.body.appendChild(toast);
    }

    if (type === 'success') {
        toast.style.background = '#166534';
        toast.style.color = 'white';
    } else {
        toast.style.background = '#991b1b';
        toast.style.color = 'white';
    }

    toast.textContent = message;
    toast.style.opacity = '1';

    setTimeout(() => {
        toast.style.opacity = '0';
    }, 2500);
}

// ===================== QUICK ADD TO CART =====================
async function addToCart(e, variantId) {
    e.preventDefault();
    e.stopImmediatePropagation();

    const btn = e.currentTarget;
    const originalText = btn.textContent;

    // Loading state
    btn.style.transition = 'all 0.2s';
    btn.textContent = "ADDING...";
    btn.disabled = true;

    try {
        const response = await fetch(`/cart/add/${variantId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'quantity=1'
        });

        const data = await response.json();

        if (data.status === 'success') {
            btn.textContent = "✓ ADDED";
            btn.classList.add('!bg-green-600', '!text-white', '!border-green-600');

            // Update navbar count
            document.dispatchEvent(new CustomEvent('cartUpdated', {
                detail: { cart_count: data.cart_count }
            }));

            showToast(data.message || "Added to cart!");

            // Reset button after 2 seconds
            setTimeout(() => {
                btn.textContent = originalText;
                btn.classList.remove('!bg-green-600', '!text-white', '!border-green-600');
                btn.disabled = false;
            }, 2000);

        } else {
            showToast(data.message || "Failed to add item", 'error');
            btn.textContent = originalText;
            btn.disabled = false;
        }

    } catch (error) {
        console.error(error);
        showToast("Something went wrong. Please try again.", 'error');
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// Make it available globally
window.addToCart = addToCart;