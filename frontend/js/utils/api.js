// API utility functions
const API_BASE_URL = 'http://localhost:8000';

class API {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    static async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.status}`);
        }

        return await response.json();
    }

    static async getTransactions(filters = {}) {
        const params = new URLSearchParams();
        
        if (filters.limit) params.append('limit', filters.limit);
        if (filters.needs_review !== undefined) params.append('needs_review', filters.needs_review);
        
        const queryString = params.toString();
        const endpoint = `/api/transactions${queryString ? '?' + queryString : ''}`;
        
        return await this.request(endpoint);
    }

    static async getCategories() {
        return await this.request('/api/categories');
    }

    static async getReviewQueue() {
        return await this.request('/api/review-queue');
    }

    static async getDashboardData() {
        // Get all data needed for dashboard
        const [transactions, categories, reviewQueue] = await Promise.all([
            this.getTransactions({ limit: 1000 }),
            this.getCategories(),
            this.getReviewQueue()
        ]);

        return {
            transactions: transactions.transactions || [],
            categories: categories.categories || [],
            reviewQueue: reviewQueue.transactions || []
        };
    }
}

// Export for use in other modules
window.API = API;
