// File Upload Module
class FileUpload {
    constructor() {
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.uploadStatus = document.getElementById('upload-status');
        
        this.init();
    }

    init() {
        // Click to upload
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        // File input change
        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFile(e.target.files[0]);
            }
        });

        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            
            if (e.dataTransfer.files.length > 0) {
                this.handleFile(e.dataTransfer.files[0]);
            }
        });
    }

    async handleFile(file) {
        // Validate file type
        const allowedTypes = ['.csv', '.txt', '.pdf'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExtension)) {
            this.showStatus('error', 'Please upload a CSV, TXT, or PDF file.');
            return;
        }

        // Validate file size (10MB max)
        if (file.size > 10 * 1024 * 1024) {
            this.showStatus('error', 'File size must be less than 10MB.');
            return;
        }

        try {
            this.showStatus('loading', `Uploading and processing ${file.name}...`);
            
            const result = await API.uploadFile(file);
            
            if (result.success) {
                this.showStatus('success', 
                    `✅ Successfully processed ${result.transactions_processed} transactions! ` +
                    `${result.needs_review} need manual review.`
                );
                
                // Show preview of transactions
                if (result.transactions && result.transactions.length > 0) {
                    this.showTransactionPreview(result.transactions);
                }
                
                // Refresh other tabs
                if (window.transactionsModule) {
                    window.transactionsModule.loadTransactions();
                }
                if (window.dashboardModule) {
                    window.dashboardModule.loadDashboard();
                }
            } else {
                this.showStatus('error', result.message || 'Failed to process file.');
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showStatus('error', 'Failed to upload file. Please try again.');
        }
    }

    showStatus(type, message) {
        this.uploadStatus.className = `upload-status ${type}`;
        this.uploadStatus.textContent = message;
        this.uploadStatus.style.display = 'block';
        
        // Auto-hide success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                this.uploadStatus.style.display = 'none';
            }, 5000);
        }
    }

    showTransactionPreview(transactions) {
        const previewHtml = `
            <div class="transaction-preview">
                <h4>Preview of processed transactions:</h4>
                <div class="preview-list">
                    ${transactions.slice(0, 5).map(t => `
                        <div class="preview-item">
                            <span class="preview-description">${t.description}</span>
                            <span class="preview-amount ${t.amount < 0 ? 'negative' : 'positive'}">
                                $${Math.abs(t.amount).toFixed(2)}
                            </span>
                            <span class="preview-category">${t.category}</span>
                            ${t.needs_review ? '<span class="preview-review">⚠️ Needs Review</span>' : ''}
                        </div>
                    `).join('')}
                    ${transactions.length > 5 ? `<div class="preview-more">... and ${transactions.length - 5} more</div>` : ''}
                </div>
            </div>
        `;
        
        this.uploadStatus.innerHTML = this.uploadStatus.innerHTML + previewHtml;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.fileUploadModule = new FileUpload();
});
