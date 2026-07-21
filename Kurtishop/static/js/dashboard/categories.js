function openCreateModal() {
    const modal = document.getElementById('createModal');
    if (modal) {
        modal.classList.remove('hidden');
        lucide.createIcons(); // refresh icons inside modal
    }
}

function closeCreateModal() {
    const modal = document.getElementById('createModal');
    if (modal) modal.classList.add('hidden');
}

// Close on outside click + ESC key
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('createModal');
    if (!modal) return;

    modal.addEventListener('click', function(e) {
        if (e.target === modal) closeCreateModal();
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === "Escape") closeCreateModal();
    });
});