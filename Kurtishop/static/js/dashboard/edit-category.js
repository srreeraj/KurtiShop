let currentEditPk = null;

function openEditModal(pk, name, parentId, description, isActive) {
    currentEditPk = pk;
    
    const modal = document.getElementById('editModal');
    const form = document.getElementById('edit-form');
    
    // Set action URL
    form.action = `/dashboard/categories/${pk}/edit/`;
    
    // Populate fields
    form.querySelector('input[name="name"]').value = name;
    form.querySelector('textarea[name="description"]').value = description || '';
    
    const parentSelect = form.querySelector('select[name="parent"]');
    if (parentSelect) parentSelect.value = parentId;
    
    const toggle = form.querySelector('#is_active_toggle');
    if (toggle) toggle.checked = isActive === 'true';
    
    modal.classList.remove('hidden');
    lucide.createIcons();
    form.querySelector('input[name="name"]').focus();
}

function closeEditModal() {
    const modal = document.getElementById('editModal');
    modal.classList.add('hidden');
}

document.addEventListener('keydown', function(e) {
    if (e.key === "Escape") {
        const editModal = document.getElementById('editModal');
        if (!editModal.classList.contains('hidden')) closeEditModal();
    }
});