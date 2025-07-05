// Main App Controller
class App {
    constructor() {
        this.currentTab = 'upload';
        this.init();
    }

    init() {
        this.setupNavigation();
        this.showTab(this.currentTab);
    }

    setupNavigation() {
        const navTabs = document.querySelectorAll('.nav-tab');
        
        navTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.target.getAttribute('data-tab');
                this.showTab(tabName);
            });
        });
    }

    showTab(tabName) {
        // Update navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.currentTab = tabName;

        // Trigger tab-specific actions
        this.onTabChange(tabName);
    }

    onTabChange(tabName) {
        switch (tabName) {
            case 'transactions':
                if (window.transactionsModule) {
                    window.transactionsModule.loadTransactions();
                }
                break;
            case 'review':
                if (window.transactionsModule) {
                    window.transactionsModule.loadReviewQueue();
                }
                break;
            case 'dashboard':
                if (window.dashboardModule) {
                    window.dashboardModule.loadDashboard();
                }
                break;
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});

// Global error handler
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
});
