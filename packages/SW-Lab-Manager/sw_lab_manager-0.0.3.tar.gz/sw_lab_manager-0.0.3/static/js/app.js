// SW Labs Management System JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Form validation and submission handling
    const forms = document.querySelectorAll('form');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            // Check if form has validation
            if (form.classList.contains('needs-validation')) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }
            
            // Handle loading state for submit buttons
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && form.checkValidity()) {
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<span class="loading"></span> Loading...';
                submitButton.disabled = true;
                
                // Re-enable button after a timeout in case of errors
                setTimeout(() => {
                    submitButton.innerHTML = originalText;
                    submitButton.disabled = false;
                }, 10000); // 10 second timeout
            }
        }, false);
    });

    // IP address validation
    const ipInputs = document.querySelectorAll('input[pattern]');
    ipInputs.forEach(input => {
        input.addEventListener('input', function() {
            const pattern = this.getAttribute('pattern');
            const value = this.value;
            const regex = new RegExp(pattern);
            
            if (value && !regex.test(value)) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            } else if (value) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-invalid', 'is-valid');
            }
        });
    });

    // Auto-refresh device status
    function refreshDeviceStatus() {
        const statusContainers = document.querySelectorAll('[data-device-status]');
        statusContainers.forEach(container => {
            const deviceId = container.getAttribute('data-device-id');
            if (deviceId) {
                fetch(`/api/device_status/${deviceId}`)
                    .then(response => response.json())
                    .then(data => {
                        updateDeviceStatusDisplay(container, data);
                    })
                    .catch(error => {
                        console.error('Error fetching device status:', error);
                    });
            }
        });
    }

    // Update device status display
    function updateDeviceStatusDisplay(container, data) {
        const statusBadge = container.querySelector('.status-badge');
        const lastPing = container.querySelector('.last-ping');
        
        if (statusBadge) {
            if (data.is_online) {
                statusBadge.className = 'badge bg-success status-badge';
                statusBadge.innerHTML = '<i class="fas fa-circle"></i> Online';
            } else {
                statusBadge.className = 'badge bg-danger status-badge';
                statusBadge.innerHTML = '<i class="fas fa-circle"></i> Offline';
            }
        }
        
        if (lastPing && data.last_ping) {
            lastPing.textContent = new Date(data.last_ping).toLocaleString();
        }
    }

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Station occupation confirmation
    const occupyButtons = document.querySelectorAll('.btn-occupy');
    occupyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to occupy this station? You will be responsible for it until you release it.')) {
                e.preventDefault();
            }
        });
    });

    // Station release confirmation
    const releaseButtons = document.querySelectorAll('.btn-release');
    releaseButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to release this station?')) {
                e.preventDefault();
            }
        });
    });

    // Search functionality for tables
    const searchInputs = document.querySelectorAll('.table-search');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.card').querySelector('table');
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });

    // Sort table columns
    const sortableHeaders = document.querySelectorAll('.sortable');
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const columnIndex = Array.from(this.parentElement.children).indexOf(this);
            const isAscending = this.classList.contains('sort-asc');
            
            // Remove sort classes from all headers
            sortableHeaders.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
            
            // Add sort class to current header
            this.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
            
            // Sort rows
            rows.sort((a, b) => {
                const aValue = a.children[columnIndex].textContent.trim();
                const bValue = b.children[columnIndex].textContent.trim();
                
                if (isAscending) {
                    return bValue.localeCompare(aValue);
                } else {
                    return aValue.localeCompare(bValue);
                }
            });
            
            // Reorder rows
            rows.forEach(row => tbody.appendChild(row));
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Responsive table wrapper
    const tables = document.querySelectorAll('.table-responsive');
    tables.forEach(table => {
        if (table.scrollWidth > table.clientWidth) {
            table.style.overflowX = 'auto';
        }
    });

    // Form field auto-save (for long forms)
    const autoSaveFields = document.querySelectorAll('.auto-save');
    autoSaveFields.forEach(field => {
        let timeout;
        field.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                // Save to localStorage
                localStorage.setItem(`autosave_${this.name}`, this.value);
            }, 1000);
        });
        
        // Restore from localStorage
        const savedValue = localStorage.getItem(`autosave_${field.name}`);
        if (savedValue) {
            field.value = savedValue;
        }
    });

    // Clear auto-save data on form submission
    const formsWithAutoSave = document.querySelectorAll('form');
    formsWithAutoSave.forEach(form => {
        form.addEventListener('submit', function() {
            const autoSaveFields = this.querySelectorAll('.auto-save');
            autoSaveFields.forEach(field => {
                localStorage.removeItem(`autosave_${field.name}`);
            });
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('.table-search');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        }
    });

    // Initialize any additional components
    initializeComponents();
});

// Initialize additional components
function initializeComponents() {
    // Add copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.btn-copy');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            if (textToCopy) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 2000);
                });
            }
        });
    });
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

// Export functions for use in other scripts
window.SWLabsApp = {
    formatDate,
    formatDuration,
    refreshDeviceStatus: function() {
        // This will be called from the main app
        refreshDeviceStatus();
    }
};