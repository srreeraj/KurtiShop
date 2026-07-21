function openCreateModal() {
    document.getElementById('createModal').classList.remove('hidden');
    lucide.createIcons();
}

function closeCreateModal() {
    document.getElementById('createModal').classList.add('hidden');
}

// Close when clicking outside
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('createModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) closeCreateModal();
        });
    }
});