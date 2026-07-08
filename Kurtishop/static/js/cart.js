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
    csrf.value = 'getCSRFToken()';
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
