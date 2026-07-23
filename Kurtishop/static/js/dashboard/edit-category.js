// static/js/dashboard/edit-category.js

function openEditModal(pk, name, parentId, description, isActive) {
    const modal = document.getElementById('editModal');
    if (!modal) {
        console.error('Edit modal not found');
        return;
    }

    const form = document.getElementById('edit-form');
    if (!form) return;

    // Set correct update URL
    form.action = `/dashboard/categories/${pk}/edit/`;

    // Populate form
    form.querySelector('input[name="name"]').value = name || '';
    form.querySelector('textarea[name="description"]').value = description || '';

    const parentSelect = form.querySelector('select[name="parent"]');
    if (parentSelect) parentSelect.value = parentId || '';

    const toggle = form.querySelector('input[name="is_active"]');
    if (toggle) toggle.checked = (isActive === 'true');

    modal.classList.remove('hidden');
    lucide.createIcons();

    // Focus name field
    const nameField = form.querySelector('input[name="name"]');
    if (nameField) nameField.focus();
}

function closeEditModal() {
    const modal = document.getElementById('editModal');
    if (modal) modal.classList.add('hidden');
}

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('editModal');
    if (!modal) return;

    modal.addEventListener('click', function(e) {
        if (e.target === modal) closeEditModal();
    });
});

document.addEventListener('keydown', function(e) {
    if (e.key === "Escape") {
        const editModal = document.getElementById('editModal');
        if (editModal && !editModal.classList.contains('hidden')) {
            closeEditModal();
        }
    }
});