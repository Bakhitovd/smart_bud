// Dashboard Module
class Dashboard {
    constructor() {
        this.totalTransactionsEl = document.getElementById('total-transactions');
        this.reviewCountEl = document.getElementById('review-count');
        this.monthSpendingEl = document.getElementById('month-spending');
        this.categoryCountEl = document.getElementById('category-count');
        this.categoriesListEl = document.getElementById('categories-list');
        
        this.init();
    }

    init() {
        this.loadDashboard();
    }

    async loadDashboard() {
        try {
            this.showLoadingStates();
            
            const data = await API.getDashboardData();
            
            this.updateStats(data);
            this.renderCategories(data.categories);
            
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError();
        }
    }

    updateStats(data) {
        const { transactions, reviewQueue } = data;
        
        // Total transactions
        this.totalTransactionsEl.textContent = transactions.length;
        
        // Review count
        this.reviewCountEl.textContent = reviewQueue.length;
        
        // This month spending
        const thisMonthSpending = this.calculateMonthSpending(transactions);
        this.monthSpendingEl.textContent = `$${Math.abs(thisMonthSpending).toFixed(0)}`;
        
        // Category count
        this.categoryCountEl.textContent = data.categories.length;
    }

    calculateMonthSpending(transactions) {
        const now = new Date();
        const currentMonth = now.getMonth();
        const currentYear = now.getFullYear();
        
        return transactions
            .filter(t => {
                const transDate = new Date(t.date);
                return transDate.getMonth() === currentMonth && 
                       transDate.getFullYear() === currentYear &&
                       t.amount < 0; // Only expenses
            })
            .reduce((sum, t) => sum + t.amount, 0);
    }

    renderCategories(categories) {
        if (categories.length === 0) {
            this.categoriesListEl.innerHTML = `
                <div class="empty-state">
                    <p>No categories found.</p>
                </div>
            `;
            return;
        }

        const html = categories.map(category => `
            <div class="category-item">
                <div class="category-color" style="background-color: ${category.color}"></div>
                <div class="category-name">${category.name}</div>
                <div class="category-type">
                    ${category.is_custom ? 'Custom' : 'Default'}
                </div>
            </div>
        `).join('');
        
        this.categoriesListEl.innerHTML = html;
    }

    showLoadingStates() {
        this.totalTransactionsEl.textContent = '...';
        this.reviewCountEl.textContent = '...';
        this.monthSpendingEl.textContent = '...';
        this.categoryCountEl.textContent = '...';
        this.categoriesListEl.innerHTML = '<p class="loading">Loading categories...</p>';
    }

    showError() {
        this.totalTransactionsEl.textContent = '❌';
        this.reviewCountEl.textContent = '❌';
        this.monthSpendingEl.textContent = '❌';
        this.categoryCountEl.textContent = '❌';
        this.categoriesListEl.innerHTML = `
            <div class="empty-state">
                <p style="color: #dc2626;">Failed to load dashboard data</p>
            </div>
        `;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardModule = new Dashboard();
});
