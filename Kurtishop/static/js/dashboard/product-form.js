document.addEventListener('DOMContentLoaded', function () {

    // ---------- Custom Attributes ----------
    const attributeRows = document.getElementById('attribute-rows');
    const attrTotalFormsInput = document.querySelector('#id_attributes-TOTAL_FORMS');
    const attrEmptyTemplate = document.getElementById('attribute-empty-form');
    const addAttributeBtn = document.getElementById('add-attribute-btn');

    if (addAttributeBtn && attributeRows && attrTotalFormsInput && attrEmptyTemplate) {
        addAttributeBtn.addEventListener('click', function () {
            const index = parseInt(attrTotalFormsInput.value, 10);
            let html = attrEmptyTemplate.innerHTML.replace(/__prefix__/g, index);

            const wrapper = document.createElement('div');
            wrapper.innerHTML = html.trim();
            const row = wrapper.firstElementChild;

            attributeRows.appendChild(row);
            attrTotalFormsInput.value = index + 1;

            if (window.lucide) lucide.createIcons();
        });

        attributeRows.addEventListener('click', function (e) {
            const btn = e.target.closest('.remove-attribute-row');
            if (!btn) return;

            const row = btn.closest('.attribute-row');
            // Clear fields so Django treats it as empty
            row.querySelectorAll('input, select').forEach(function (field) {
                if (field.type === 'checkbox') field.checked = false;
                else field.value = '';
            });
            row.style.display = 'none';
        });
    } else {
        console.warn('Attribute formset elements not found', {
            addAttributeBtn, attributeRows, attrTotalFormsInput, attrEmptyTemplate
        });
    }

    // ---------- Variant rows ----------
    const variantRows = document.getElementById('variant-rows');
    const totalFormsInput = document.querySelector('#id_variants-TOTAL_FORMS');
    const emptyTemplate = document.getElementById('variant-empty-form');
    const addVariantBtn = document.getElementById('add-variant-btn');

    if (addVariantBtn && variantRows && totalFormsInput && emptyTemplate) {
        addVariantBtn.addEventListener('click', function () {
            const index = parseInt(totalFormsInput.value, 10);
            let html = emptyTemplate.innerHTML.replace(/__prefix__/g, index);

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
            row.querySelectorAll('input, select').forEach(function (field) {
                if (field.type === 'checkbox') field.checked = false;
                else field.value = '';
            });
            row.style.display = 'none';
        });
    }

    // ---------- Image blocks ----------
    const imageBlocks = document.getElementById('image-blocks');
    const imageTemplate = document.getElementById('image-block-template');
    const addImageBlockBtn = document.getElementById('add-image-block-btn');
    let blockIndex = 0;

    if (addImageBlockBtn && imageBlocks && imageTemplate) {
        addImageBlockBtn.addEventListener('click', function () {
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

        // Live thumbnail preview
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
    }
});