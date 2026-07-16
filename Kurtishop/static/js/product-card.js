(function () {
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.body.addEventListener('click', (e) => {
            const btn = e.target.closest('.add-to-cart-btn');
            if (!btn) return;

            btn.classList.add('scale-90');
            setTimeout(() => btn.classList.remove('scale-90'), 150);

            const productId = btn.dataset.productId;
            fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            }).catch(() => {});
        });
    });
})();