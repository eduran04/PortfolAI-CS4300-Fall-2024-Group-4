// Sidebar functionality
const toggleButton = document.getElementById('toggle-btn');
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');

// Initialize sidebar state
let isCollapsed = false;

function toggleSidebar() {
    isCollapsed = !isCollapsed;
    sidebar.classList.toggle('close');
    toggleButton.classList.toggle('rotate');
    
    // Update main content margin
    if (isCollapsed) {
        mainContent.classList.remove('sidebar-open');
        mainContent.classList.add('sidebar-collapsed');
    } else {
        mainContent.classList.remove('sidebar-collapsed');
        mainContent.classList.add('sidebar-open');
    }
    
    closeAllSubMenus();
}

function toggleSubMenu(button) {
    const subMenu = button.nextElementSibling;
    
    if (!subMenu.classList.contains('show')) {
        closeAllSubMenus();
    }
    
    subMenu.classList.toggle('show');
    button.classList.toggle('rotate');
    
    // If sidebar is collapsed, expand it when opening submenu
    if (sidebar.classList.contains('close')) {
        sidebar.classList.toggle('close');
        toggleButton.classList.toggle('rotate');
        isCollapsed = false;
        mainContent.classList.remove('sidebar-collapsed');
        mainContent.classList.add('sidebar-open');
    }
}

function closeAllSubMenus() {
    const openSubMenus = sidebar.getElementsByClassName('show');
    Array.from(openSubMenus).forEach(ul => {
        ul.classList.remove('show');
        ul.previousElementSibling.classList.remove('rotate');
    });
}

// Settings dropdown functionality
function toggleSettings() {
    const settingsMenu = document.getElementById('settings-menu');
    const settingsArrow = document.getElementById('settings-arrow');
    
    if (settingsMenu.classList.contains('tw-hidden')) {
        settingsMenu.classList.remove('tw-hidden');
        settingsArrow.style.transform = 'rotate(180deg)';
    } else {
        settingsMenu.classList.add('tw-hidden');
        settingsArrow.style.transform = 'rotate(0deg)';
    }
}

// Close submenus when clicking outside
document.addEventListener('click', function(event) {
    if (!sidebar.contains(event.target)) {
        closeAllSubMenus();
    }
});

// Handle window resize - Optimized for laptop/desktop
window.addEventListener('resize', function() {
    if (window.innerWidth <= 767) {
        // Mobile view - reset sidebar state
        sidebar.classList.remove('close');
        toggleButton.classList.remove('rotate');
        mainContent.classList.remove('sidebar-open', 'sidebar-collapsed');
        isCollapsed = false;
    } else if (window.innerWidth <= 1023) {
        // Small laptop/tablet landscape - compact but functional
        if (!isCollapsed) {
            mainContent.classList.remove('sidebar-collapsed');
            mainContent.classList.add('sidebar-open');
        }
    } else {
        // Standard laptop and desktop - full experience
        if (!isCollapsed) {
            mainContent.classList.remove('sidebar-collapsed');
            mainContent.classList.add('sidebar-open');
        }
    }
});

// Initialize sidebar on page load - Laptop/desktop optimized
document.addEventListener('DOMContentLoaded', function() {
    // Set initial state based on screen size
    if (window.innerWidth > 767) {
        mainContent.classList.add('sidebar-open');
        isCollapsed = false;
    } else {
        mainContent.classList.remove('sidebar-open', 'sidebar-collapsed');
        isCollapsed = false;
    }
    
    // Add click handlers to all dropdown buttons
    const dropdownButtons = document.querySelectorAll('.dropdown-btn');
    dropdownButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            toggleSubMenu(this);
        });
    });
    
    // Add click handlers to all navigation links
    const navLinks = document.querySelectorAll('#sidebar a:not(.dropdown-btn)');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Remove active class from all links
            navLinks.forEach(l => l.parentElement.classList.remove('active'));
            // Add active class to clicked link
            this.parentElement.classList.add('active');
        });
    });
});

// Export functions for global access
window.toggleSidebar = toggleSidebar;
window.toggleSubMenu = toggleSubMenu;
window.toggleSettings = toggleSettings;
