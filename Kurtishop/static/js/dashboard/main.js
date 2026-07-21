// static/js/dashboard/main.js

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    
    if (sidebar && mainContent) {
        sidebar.classList.toggle('-translate-x-full');
        mainContent.classList.toggle('ml-64'); // adjust based on your sidebar width
    }
}

// Make sure Lucide icons are initialized
document.addEventListener('DOMContentLoaded', function() {
    lucide.createIcons();
});