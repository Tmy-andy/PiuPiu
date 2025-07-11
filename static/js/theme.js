// Theme Management System
class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || 'light';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.setupEventListeners();
        this.updateThemePreview();
    }

    getStoredTheme() {
        return localStorage.getItem('theme') || document.documentElement.getAttribute('data-theme');
    }

    setStoredTheme(theme) {
        localStorage.setItem('theme', theme);
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        this.setStoredTheme(theme);
        
        // Trigger custom event for theme change
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: theme } 
        }));
    }

    setupEventListeners() {
        // Theme selection buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.theme-preview')) {
                const themeCard = e.target.closest('.theme-preview');
                const theme = themeCard.getAttribute('data-theme');
                this.changeTheme(theme);
            }
        });

        // Listen for theme changes from server
        window.addEventListener('themeChanged', (e) => {
            this.updateThemePreview();
            this.showThemeChangeNotification(e.detail.theme);
        });
    }

    changeTheme(theme) {
        if (theme === this.currentTheme) return;

        // Apply theme immediately for better UX
        this.applyTheme(theme);
        this.updateThemePreview();

        // Save to server
        this.saveThemeToServer(theme);
    }

    async saveThemeToServer(theme) {
        try {
            const response = await fetch('/change_theme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ theme: theme })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showThemeChangeNotification(theme, 'success');
            } else {
                this.showThemeChangeNotification(theme, 'error');
                // Revert theme if save failed
                this.applyTheme(this.getStoredTheme());
            }
        } catch (error) {
            console.error('Error saving theme:', error);
            this.showThemeChangeNotification(theme, 'error');
            // Revert theme if save failed
            this.applyTheme(this.getStoredTheme());
        }
    }

    updateThemePreview() {
        // Update active state on theme preview cards
        document.querySelectorAll('.theme-preview').forEach(card => {
            card.classList.remove('active');
            if (card.getAttribute('data-theme') === this.currentTheme) {
                card.classList.add('active');
            }
        });

        // Update current theme display
        const currentThemeDisplay = document.getElementById('currentTheme');
        if (currentThemeDisplay) {
            currentThemeDisplay.textContent = this.getThemeDisplayName(this.currentTheme);
        }
    }

    getThemeDisplayName(theme) {
        const themeNames = {
            'light': 'Sáng',
            'dark': 'Tối',
            'blue': 'Xanh Dương',
            'green': 'Xanh Lá',
            'purple': 'Tím',
            'rose': 'Hồng'
        };
        return themeNames[theme] || theme;
    }

    showThemeChangeNotification(theme, status = 'success') {
        const themeName = this.getThemeDisplayName(theme);
        
        // Remove existing notifications
        document.querySelectorAll('.theme-notification').forEach(el => el.remove());

        // Create notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${status === 'success' ? 'success' : 'danger'} alert-dismissible fade show theme-notification`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        `;
        
        notification.innerHTML = `
            <i class="fas fa-${status === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
            ${status === 'success' 
                ? `Đã chuyển sang theme <strong>${themeName}</strong>` 
                : `Lỗi khi lưu theme <strong>${themeName}</strong>`
            }
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    // Get available themes
    getAvailableThemes() {
        return [
            { id: 'light', name: 'Sáng', icon: 'fa-sun' },
            { id: 'dark', name: 'Tối', icon: 'fa-moon' },
            { id: 'blue', name: 'Xanh Dương', icon: 'fa-water' },
            { id: 'green', name: 'Xanh Lá', icon: 'fa-leaf' },
            { id: 'purple', name: 'Tím', icon: 'fa-gem' },
            { id: 'rose', name: 'Hồng', icon: 'fa-heart' }
        ];
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}