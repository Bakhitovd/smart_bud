// Transactions Module
class Transactions {
    constructor() {
        this.transactionsList = document.getElementById('transactions-list');
        this.reviewList = document.getElementById('review-list');
        this.refreshBtn = document.getElementById('refresh-transactions');
        this.filterSelect = document.getElementById('filter-review');
        
        this.init();
    }

    init() {
        // Refresh button
        this.refreshBtn.addEventListener('click', () => {
            this.loadTransactions();
        });

        // Filter change
        this.filterSelect.addEventListener('change', () => {
            this.loadTransactions();
        });

        // Load initial data
        this.loadTransactions();
        this.loadReviewQueue();
    }

    async loadTransactions() {
        try {
            this.showLoading(this.transactionsList);
            
            const filters = {};
            const reviewFilter = this.filterSelect.value;
            
            if (reviewFilter !== '') {
                filters.needs_review = reviewFilter === 'true';
            }
            
            const result = await API.getTransactions(filters);
            this.renderTransactions(result.transactions || []);
            
        } catch (error) {
            console.error('Error loading transactions:', error);
            this.showError(this.transactionsList, 'Failed to load transactions');
        }
    }

    async loadReviewQueue() {
        try {
            this.showLoading(this.reviewList);
            
            const result = await API.getReviewQueue();
            this.renderReviewQueue(result.transactions || []);
            
        } catch (error) {
            console.error('Error loading review queue:', error);
            this.showError(this.reviewList, 'Failed to load review queue');
        }
    }

    renderTransactions(transactions) {
        if (transactions.length === 0) {
            this.transactionsList.innerHTML = `
                <div class="empty-state">
                    <p>No transactions found. Upload a bank statement to get started!</p>
                </div>
            `;
            return;
        }

        const html = transactions.map(transaction => this.createTransactionHTML(transaction)).join('');
        this.transactionsList.innerHTML = html;
    }

    renderReviewQueue(transactions) {
        if (transactions.length === 0) {
            this.reviewList.innerHTML = `
                <div class="empty-state">
                    <p>🎉 No transactions need review! All transactions have been categorized.</p>
                </div>
            `;
            return;
        }

        const html = transactions.map(transaction => this.createTransactionHTML(transaction, true)).join('');
        this.reviewList.innerHTML = html;
    }

    createTransactionHTML(transaction, isReview = false) {
        const date = new Date(transaction.date).toLocaleDateString();
        const amount = Math.abs(transaction.amount);
        const isNegative = transaction.amount < 0;
        
        return `
            <div class="transaction-item ${transaction.needs_review ? 'needs-review' : ''}" data-id="${transaction.id}">
                <div class="transaction-info">
                    <div class="transaction-description">${this.escapeHtml(transaction.description)}</div>
                    <div class="transaction-meta">
                        ${date} • ${transaction.file_source || 'Unknown source'}
                        ${transaction.confidence_score ? 
                            `<span class="confidence-score">Confidence: ${(transaction.confidence_score * 100).toFixed(0)}%</span>` 
                            : ''
                        }
                    </div>
                </div>
                <div class="transaction-details">
                    <div class="transaction-amount ${isNegative ? 'negative' : 'positive'}">
                        ${isNegative ? '-' : '+'}$${amount.toFixed(2)}
                    </div>
                    <div class="transaction-category" style="background-color: ${this.getCategoryColor(transaction.category)}">
                        ${transaction.category || 'Uncategorized'}
                    </div>
                    ${transaction.needs_review ? 
                        `<button class="btn btn-primary review-btn" onclick="window.transactionsModule.reviewTransaction(${transaction.id})">
                            Review
                        </button>` 
                        : ''
                    }
                </div>
            </div>
        `;
    }

    getCategoryColor(categoryName) {
        const colors = {
            'Groceries': '#10B981',
            'Dining': '#F59E0B',
            'Transportation': '#3B82F6',
            'Bills': '#EF4444',
            'Entertainment': '#8B5CF6',
            'Shopping': '#EC4899',
            'Healthcare': '#06B6D4',
            'Other': '#6B7280'
        };
        return colors[categoryName] || '#6B7280';
    }

    reviewTransaction(transactionId) {
        // For now, just show an alert. In a full implementation, 
        // this would open a modal to edit the transaction category
        alert(`Review transaction ${transactionId}\n\nIn a full implementation, this would open a modal to edit the category.`);
    }

    showLoading(container) {
        container.innerHTML = '<p class="loading">Loading...</p>';
    }

    showError(container, message) {
        container.innerHTML = `
            <div class="empty-state">
                <p style="color: #dc2626;">❌ ${message}</p>
            </div>
        `;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.transactionsModule = new Transactions();
});
