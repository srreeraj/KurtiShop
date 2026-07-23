function openCreateModal() {
    const modal = document.getElementById('createModal');
    modal.classList.remove('hidden');
    document.getElementById('create-form').reset();
    lucide.createIcons();
    document.querySelector('#create-form input[name="name"]').focus();
}

function closeCreateModal() {
    const modal = document.getElementById('createModal');
    modal.classList.add('hidden');
}

document.addEventListener('keydown', function(e) {
    if (e.key === "Escape") {
        const createModal = document.getElementById('createModal');
        if (!createModal.classList.contains('hidden')) closeCreateModal();
    }
});