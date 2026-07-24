document.addEventListener('DOMContentLoaded', function () {
    // ---------- Variant rows ----------
    const variantRows = document.getElementById('variant-rows');
    const totalFormsInput = document.querySelector('#id_variants-TOTAL_FORMS');
    const emptyTemplate = document.getElementById('variant-empty-form');

    document.getElementById('add-variant-btn').addEventListener('click', function () {
        const index = parseInt(totalFormsInput.value, 10);
        const html = emptyTemplate.innerHTML.replace(/__prefix__/g, index);
        const wrapper = document.createElement('div');
        wrapper.innerHTML = html.trim();
        const row = wrapper.firstElementChild;
        variantRows.appendChild(row);
        totalFormsInput.value = index + 1;
        if (window.lucide) lucide.createIcons();
    });

    variantRows.addEventListener('click', function (e) {
        const btn = e.target.closest('.remove-variant-row');
        if (!btn) return;
        const row = btn.closest('.variant-row');
        // New (unsaved) row: clear all inputs so Django's empty-form skip logic ignores it, then hide it
        row.querySelectorAll('input, select').forEach(function (field) {
            if (field.type === 'checkbox') field.checked = false;
            else field.value = '';
        });
        row.style.display = 'none';
    });

    // ---------- Image blocks ----------
    const imageBlocks = document.getElementById('image-blocks');
    const imageTemplate = document.getElementById('image-block-template');
    let blockIndex = 0;

    document.getElementById('add-image-block-btn').addEventListener('click', function () {
        const html = imageTemplate.innerHTML.replace(/__INDEX__/g, blockIndex);
        const wrapper = document.createElement('div');
        wrapper.innerHTML = html.trim();
        const block = wrapper.firstElementChild;
        imageBlocks.appendChild(block);
        blockIndex += 1;
        if (window.lucide) lucide.createIcons();
    });

    imageBlocks.addEventListener('click', function (e) {
        const btn = e.target.closest('.remove-image-block');
        if (btn) {
            btn.closest('.image-block').remove();
        }
    });

    // Live thumbnail preview for a multi-file input
    imageBlocks.addEventListener('change', function (e) {
        if (e.target.type !== 'file') return;
        const preview = e.target.closest('.image-block').querySelector('.image-preview');
        preview.innerHTML = '';
        Array.from(e.target.files).forEach(function (file) {
            const reader = new FileReader();
            reader.onload = function (ev) {
                const img = document.createElement('img');
                img.src = ev.target.result;
                img.className = 'w-16 h-16 object-cover rounded-lg border border-gray-200';
                preview.appendChild(img);
            };
            reader.readAsDataURL(file);
        });
    });
});