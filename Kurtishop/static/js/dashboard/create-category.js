function openCreateModal() {
    const modal = document.getElementById('createModal');
    if (!modal) {
        console.error('Create modal not found in DOM');
        return;
    }
    
    modal.classList.remove('hidden');
    const form = document.getElementById('create-form');
    if (form) form.reset();
    
    lucide.createIcons();
    
    // Focus first input
    const firstInput = modal.querySelector('input[name="name"]');
    if (firstInput) firstInput.focus();
}

function closeCreateModal() {
    const modal = document.getElementById('createModal');
    if (modal) modal.classList.add('hidden');
}

// Close on outside click and ESC
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('createModal');
    if (!modal) return;

    modal.addEventListener('click', function(e) {
        if (e.target === modal) closeCreateModal();
    });
});

document.addEventListener('keydown', function(e) {
    if (e.key === "Escape") {
        const createModal = document.getElementById('createModal');
        if (createModal && !createModal.classList.contains('hidden')) {
            closeCreateModal();
        }
    }
});