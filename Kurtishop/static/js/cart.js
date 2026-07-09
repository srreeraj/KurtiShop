// ================= CSRF =================

function getCSRFToken() {
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : null;
}

// ================= LOAD DRAWER =================

async function loadCartDrawer() {

    try {

        const response = await fetch('/cart/drawer/', {
            credentials: 'same-origin'
        });

        const html = await response.text();

        document.getElementById('cart-drawer-content').innerHTML = html;

        attachDrawerListeners();

    } catch (err) {

        console.error('Failed to load cart drawer:', err);

    }

}

// ================= LISTENERS =================

function attachDrawerListeners() {

    document.querySelectorAll('[data-action="update-qty"]').forEach(btn => {

        btn.addEventListener('click', function (e) {

            e.preventDefault();
            e.stopPropagation();

            if (this.disabled) return;

            updateQuantityAjax(
                this.dataset.itemId,
                this.dataset.change,
                this
            );

        });

    });

    document.querySelectorAll('.remove-from-drawer').forEach(btn => {

        btn.addEventListener('click', function (e) {

            e.preventDefault();
            e.stopPropagation();

            if (this.disabled) return;

            if (confirm("Remove this item?")) {

                removeFromDrawerAjax(
                    this.dataset.itemId,
                    this
                );

            }

        });

    });

}

// ================= UPDATE QUANTITY =================

async function updateQuantityAjax(itemId, change, btn) {

    const csrfToken = getCSRFToken();

    if (!csrfToken) {
        console.error('CSRF token missing from drawer.');
        return;
    }

    const formData = new FormData();

    formData.append("quantity", change);

    formData.append("csrfmiddlewaretoken", csrfToken);

    if (btn) btn.disabled = true;

    try {

        const response = await fetch(`/cart/update/${itemId}/`, {

            method: "POST",

            body: formData,

            credentials: 'same-origin'

        });

        if (!response.ok && response.status !== 400) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();

        if (data.status === "success") {

            loadCartDrawer();

        } else {

            alert(data.message || "Could not update quantity.");
            if (btn) btn.disabled = false;

        }

    } catch (err) {

        console.error('Update quantity failed:', err);
        alert("Something went wrong updating your cart. Please try again.");
        if (btn) btn.disabled = false;

    }

}

// ================= REMOVE =================

async function removeFromDrawerAjax(itemId, btn) {

    const csrfToken = getCSRFToken();

    if (!csrfToken) {
        console.error('CSRF token missing from drawer.');
        return;
    }

    const formData = new FormData();

    formData.append("csrfmiddlewaretoken", csrfToken);

    if (btn) btn.disabled = true;

    try {

        const response = await fetch(`/cart/remove/${itemId}/`, {

            method: "POST",

            body: formData,

            credentials: 'same-origin'

        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();

        if (data.status === "success") {

            loadCartDrawer();

        } else {

            if (btn) btn.disabled = false;

        }

    } catch (err) {

        console.error('Remove item failed:', err);
        alert("Something went wrong removing this item. Please try again.");
        if (btn) btn.disabled = false;

    }

}

// ================= OPEN =================

function openCartDrawer() {

    const overlay = document.getElementById("cart-overlay");

    const drawer = document.getElementById("cart-drawer");

    overlay.classList.remove("hidden");

    setTimeout(() => {

        overlay.classList.add("opacity-100");

    }, 10);

    drawer.classList.remove("translate-x-full");

    loadCartDrawer();

}

// ================= CLOSE =================

function closeCartDrawer() {

    const overlay = document.getElementById("cart-overlay");

    const drawer = document.getElementById("cart-drawer");

    overlay.classList.remove("opacity-100");

    drawer.classList.add("translate-x-full");

    setTimeout(() => {

        overlay.classList.add("hidden");

    }, 300);

}

// ================= INIT =================

document.addEventListener("DOMContentLoaded", () => {

    const cartBtn = document.getElementById("cart-btn");

    if (cartBtn) {

        cartBtn.addEventListener("click", function (e) {

            e.preventDefault();

            openCartDrawer();

        });

    }

    document.addEventListener("keydown", function (e) {

        if (e.key === "Escape") {

            closeCartDrawer();

        }

    });

});