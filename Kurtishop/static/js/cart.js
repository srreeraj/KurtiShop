// ================= CSRF =================

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// ================= LOAD DRAWER =================

async function loadCartDrawer() {

    try {

        const response = await fetch('/cart/drawer/');

        const html = await response.text();

        document.getElementById('cart-drawer-content').innerHTML = html;

        attachDrawerListeners();

    } catch (err) {

        console.error(err);

    }

}

// ================= LISTENERS =================

function attachDrawerListeners() {

    document.querySelectorAll('[data-action="update-qty"]').forEach(btn => {

        btn.addEventListener('click', function () {

            updateQuantityAjax(
                this.dataset.itemId,
                this.dataset.change
            );

        });

    });

    document.querySelectorAll('.remove-from-drawer').forEach(btn => {

        btn.addEventListener('click', function () {

            if (confirm("Remove this item?")) {

                removeFromDrawerAjax(
                    this.dataset.itemId
                );

            }

        });

    });

}

// ================= UPDATE QUANTITY =================

async function updateQuantityAjax(itemId, change) {

    const formData = new FormData();

    formData.append("quantity", change);

    formData.append("csrfmiddlewaretoken", getCSRFToken());

    const response = await fetch(`/cart/update/${itemId}/`, {

        method: "POST",

        body: formData

    });

    const data = await response.json();

    if (data.status === "success") {

        loadCartDrawer();

    } else {

        alert(data.message);

    }

}

// ================= REMOVE =================

async function removeFromDrawerAjax(itemId) {

    const formData = new FormData();

    formData.append("csrfmiddlewaretoken", getCSRFToken());

    const response = await fetch(`/cart/remove/${itemId}/`, {

        method: "POST",

        body: formData

    });

    const data = await response.json();

    if (data.status === "success") {

        loadCartDrawer();

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