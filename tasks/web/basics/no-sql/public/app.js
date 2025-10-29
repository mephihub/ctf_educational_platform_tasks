class UserPortalApp {
    constructor() {
        this.currentUser = null;
        this.token = localStorage.getItem('token');
        this.currentSection = 'overview';
        this.users = [];
        this.currentPage = 1;
        this.usersPerPage = 10;
        
        this.init();
    }

    async init() {
        // Show loading screen
        this.showLoading();
        
        // Check if user is already logged in
        if (this.token) {
            try {
                await this.getCurrentUser();
                this.showDashboard();
            } catch (error) {
                this.logout();
            }
        } else {
            this.showLogin();
        }
        
        this.setupEventListeners();
        this.hideLoading();
    }

    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }

    showLogin() {
        document.getElementById('loginScreen').classList.remove('hidden');
        document.getElementById('dashboard').classList.add('hidden');
    }

    showDashboard() {
        document.getElementById('loginScreen').classList.add('hidden');
        document.getElementById('dashboard').classList.remove('hidden');
        this.loadDashboardData();
    }

    setupEventListeners() {
        // Login form
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.switchSection(section);
            });
        });

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', (e) => {
            e.preventDefault();
            this.logout();
        });

        // User search and filters
        document.getElementById('userSearch').addEventListener('input', 
            this.debounce(() => this.loadUsers(), 300));
        document.getElementById('departmentFilter').addEventListener('change', () => this.loadUsers());
        document.getElementById('roleFilter').addEventListener('change', () => this.loadUsers());

        // Profile form
        document.getElementById('profileForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.updateProfile();
        });

        // Admin tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = btn.dataset.tab;
                this.switchAdminTab(tab);
            });
        });
    }

    async handleLogin() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('loginError');

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.success) {
                this.token = data.token;
                this.currentUser = data.user;
                localStorage.setItem('token', this.token);
                errorDiv.classList.add('hidden');
                this.showDashboard();
            } else {
                errorDiv.textContent = data.error || 'Login failed';
                errorDiv.classList.remove('hidden');
            }
        } catch (error) {
            errorDiv.textContent = 'Network error. Please try again.';
            errorDiv.classList.remove('hidden');
        }
    }

    async getCurrentUser() {
        const response = await fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to get current user');
        }

        const data = await response.json();
        this.currentUser = data.user;
    }

    logout() {
        this.token = null;
        this.currentUser = null;
        localStorage.removeItem('token');
        this.showLogin();
    }

    switchSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${section}Section`).classList.add('active');

        this.currentSection = section;

        // Load section-specific data
        switch (section) {
            case 'overview':
                this.loadOverviewData();
                break;
            case 'users':
                this.loadUsers();
                break;
            case 'profile':
                this.loadProfile();
                break;
            case 'admin':
                if (this.currentUser.role === 'admin') {
                    this.loadAdminData();
                }
                break;
        }
    }

    async loadDashboardData() {
        // Update current user display
        const userDisplay = document.getElementById('currentUser');
        if (this.currentUser) {
            userDisplay.textContent = `${this.currentUser.profile.firstName || this.currentUser.username}`;
        }

        // Hide admin nav if not admin
        const adminNav = document.querySelector('.admin-only');
        if (this.currentUser.role !== 'admin') {
            adminNav.style.display = 'none';
        }

        // Load initial section
        this.switchSection('overview');
    }

    async loadOverviewData() {
        try {
            const response = await fetch('/api/users/stats/overview', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                
                document.getElementById('totalUsers').textContent = data.totalUsers;
                document.getElementById('activeUsers').textContent = data.activeUsers;
                document.getElementById('departments').textContent = data.usersByDepartment.length;
                document.getElementById('recentActivity').textContent = data.activeUsers;

                // Update charts (simplified display)
                this.updateRoleChart(data.usersByRole);
                this.updateDepartmentChart(data.usersByDepartment);
            }
        } catch (error) {
            console.error('Error loading overview data:', error);
        }
    }

    updateRoleChart(roleData) {
        const chartDiv = document.getElementById('roleChart');
        chartDiv.innerHTML = '';
        
        roleData.forEach(role => {
            const bar = document.createElement('div');
            bar.style.cssText = `
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px;
                margin: 5px 0;
                background: #f8f9fa;
                border-radius: 5px;
                border-left: 4px solid #667eea;
            `;
            bar.innerHTML = `
                <span style="font-weight: 500; text-transform: capitalize;">${role._id}</span>
                <span style="font-weight: 600; color: #667eea;">${role.count}</span>
            `;
            chartDiv.appendChild(bar);
        });
    }

    updateDepartmentChart(deptData) {
        const chartDiv = document.getElementById('departmentChart');
        chartDiv.innerHTML = '';
        
        deptData.forEach(dept => {
            if (dept._id) {
                const bar = document.createElement('div');
                bar.style.cssText = `
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px;
                    margin: 5px 0;
                    background: #f8f9fa;
                    border-radius: 5px;
                    border-left: 4px solid #764ba2;
                `;
                bar.innerHTML = `
                    <span style="font-weight: 500;">${dept._id}</span>
                    <span style="font-weight: 600; color: #764ba2;">${dept.count}</span>
                `;
                chartDiv.appendChild(bar);
            }
        });
    }

    async loadUsers() {
        const search = document.getElementById('userSearch').value;
        const department = document.getElementById('departmentFilter').value;
        const role = document.getElementById('roleFilter').value;

        const params = new URLSearchParams({
            page: this.currentPage,
            limit: this.usersPerPage
        });

        if (search) params.append('search', search);
        if (department) params.append('department', department);
        if (role) params.append('role', role);

        try {
            const response = await fetch(`/api/users?${params}`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.users = data.users;
                this.renderUsersTable();
                this.renderPagination(data.pagination);
                this.updateDepartmentFilter(data.users);
            }
        } catch (error) {
            console.error('Error loading users:', error);
        }
    }

    renderUsersTable() {
        const tbody = document.getElementById('usersTableBody');
        tbody.innerHTML = '';

        this.users.forEach(user => {
            const row = document.createElement('tr');
            
            const initials = (user.profile.firstName?.[0] || '') + (user.profile.lastName?.[0] || '');
            const displayName = `${user.profile.firstName || ''} ${user.profile.lastName || ''}`.trim() || user.username;
            const lastLogin = user.lastLogin ? new Date(user.lastLogin).toLocaleDateString() : 'Never';
            
            row.innerHTML = `
                <td>
                    <div class="user-info-cell">
                        <div class="user-avatar">${initials || user.username[0].toUpperCase()}</div>
                        <div class="user-details">
                            <h4>${displayName}</h4>
                            <p>@${user.username}</p>
                        </div>
                    </div>
                </td>
                <td>${user.email}</td>
                <td>${user.profile.department || '-'}</td>
                <td><span class="role-badge role-${user.role}">${user.role}</span></td>
                <td>${lastLogin}</td>
                <td><span class="status-badge status-${user.isActive ? 'active' : 'inactive'}">${user.isActive ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline" onclick="app.viewUser('${user._id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${this.currentUser.permissions.includes('write') ? `
                            <button class="btn btn-sm btn-outline" onclick="app.editUser('${user._id}')">
                                <i class="fas fa-edit"></i>
                            </button>
                        ` : ''}
                    </div>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }

    renderPagination(pagination) {
        const paginationDiv = document.getElementById('usersPagination');
        paginationDiv.innerHTML = '';

        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.textContent = 'Previous';
        prevBtn.disabled = pagination.page === 1;
        prevBtn.addEventListener('click', () => {
            if (pagination.page > 1) {
                this.currentPage = pagination.page - 1;
                this.loadUsers();
            }
        });
        paginationDiv.appendChild(prevBtn);

        // Page numbers
        for (let i = 1; i <= pagination.pages; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.textContent = i;
            pageBtn.classList.toggle('active', i === pagination.page);
            pageBtn.addEventListener('click', () => {
                this.currentPage = i;
                this.loadUsers();
            });
            paginationDiv.appendChild(pageBtn);
        }

        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Next';
        nextBtn.disabled = pagination.page === pagination.pages;
        nextBtn.addEventListener('click', () => {
            if (pagination.page < pagination.pages) {
                this.currentPage = pagination.page + 1;
                this.loadUsers();
            }
        });
        paginationDiv.appendChild(nextBtn);
    }

    updateDepartmentFilter(users) {
        const filter = document.getElementById('departmentFilter');
        const departments = [...new Set(users.map(u => u.profile.department).filter(Boolean))];
        
        // Keep existing options and add new ones
        const existingOptions = Array.from(filter.options).map(opt => opt.value);
        
        departments.forEach(dept => {
            if (!existingOptions.includes(dept)) {
                const option = document.createElement('option');
                option.value = dept;
                option.textContent = dept;
                filter.appendChild(option);
            }
        });
    }

    async loadProfile() {
        if (!this.currentUser) return;

        // Update profile display
        document.getElementById('profileName').textContent = 
            `${this.currentUser.profile.firstName || ''} ${this.currentUser.profile.lastName || ''}`.trim() || this.currentUser.username;
        document.getElementById('profileRole').textContent = this.currentUser.role;
        document.getElementById('profileBadge').textContent = this.currentUser.role.toUpperCase();

        // Fill form
        document.getElementById('profileFirstName').value = this.currentUser.profile.firstName || '';
        document.getElementById('profileLastName').value = this.currentUser.profile.lastName || '';
        document.getElementById('profileEmail').value = this.currentUser.email;
        document.getElementById('profilePhone').value = this.currentUser.profile.phone || '';
        document.getElementById('profileDepartment').value = this.currentUser.profile.department || '';
        document.getElementById('profilePosition').value = this.currentUser.profile.position || '';
    }

    async updateProfile() {
        const formData = new FormData(document.getElementById('profileForm'));
        const profileData = {
            profile: {
                firstName: formData.get('firstName'),
                lastName: formData.get('lastName'),
                phone: formData.get('phone'),
                department: formData.get('department'),
                position: formData.get('position')
            }
        };

        try {
            const response = await fetch(`/api/users/${this.currentUser._id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(profileData)
            });

            if (response.ok) {
                const data = await response.json();
                this.currentUser = data.user;
                this.showNotification('Profile updated successfully!', 'success');
                this.loadProfile();
            } else {
                this.showNotification('Failed to update profile', 'error');
            }
        } catch (error) {
            this.showNotification('Network error', 'error');
        }
    }

    async loadAdminData() {
        this.switchAdminTab('dashboard');
    }

    switchAdminTab(tab) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.admin-tab').forEach(tabContent => {
            tabContent.classList.remove('active');
        });
        document.getElementById(`admin${tab.charAt(0).toUpperCase() + tab.slice(1)}`).classList.add('active');

        // Load tab-specific data
        switch (tab) {
            case 'flags':
                this.loadFlags();
                break;
            case 'logs':
                this.loadLogs();
                break;
            case 'health':
                this.loadHealth();
                break;
        }
    }

    async loadFlags() {
        try {
            const response = await fetch('/api/admin/flags', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const flagsList = document.getElementById('flagsList');

            if (response.ok) {
                const data = await response.json();
                flagsList.innerHTML = '';
                
                data.flags.forEach(flag => {
                    const flagDiv = document.createElement('div');
                    flagDiv.className = 'flag-item';
                    flagDiv.innerHTML = `
                        <h4><i class="fas fa-flag"></i> ${flag.name}</h4>
                        <p>${flag.description}</p>
                        <div class="flag-value">${flag.value}</div>
                        <small>Category: ${flag.category} | Points: ${flag.points}</small>
                    `;
                    flagsList.appendChild(flagDiv);
                });
            } else {
                flagsList.innerHTML = '<div class="loading-message">Access denied or no flags available</div>';
            }
        } catch (error) {
            document.getElementById('flagsList').innerHTML = '<div class="loading-message">Error loading flags</div>';
        }
    }

    async loadLogs() {
        try {
            const response = await fetch('/api/admin/logs', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const logsList = document.getElementById('logsList');

            if (response.ok) {
                const data = await response.json();
                logsList.innerHTML = '';
                
                data.logs.forEach(log => {
                    const logDiv = document.createElement('div');
                    logDiv.className = 'log-item';
                    logDiv.innerHTML = `
                        <div>
                            <span class="log-level ${log.level.toLowerCase()}">${log.level}</span>
                            <span>${log.message}</span>
                            <small> - ${log.user} (${log.ip})</small>
                        </div>
                        <small>${new Date(log.timestamp).toLocaleString()}</small>
                    `;
                    logsList.appendChild(logDiv);
                });
            } else {
                logsList.innerHTML = '<div class="loading-message">Access denied</div>';
            }
        } catch (error) {
            document.getElementById('logsList').innerHTML = '<div class="loading-message">Error loading logs</div>';
        }
    }

    async loadHealth() {
        try {
            const response = await fetch('/api/admin/health', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const healthStatus = document.getElementById('healthStatus');

            if (response.ok) {
                const data = await response.json();
                healthStatus.innerHTML = `
                    <div class="health-metric">
                        <span>System Status</span>
                        <span class="status-indicator online">
                            <i class="fas fa-circle"></i> ${data.status}
                        </span>
                    </div>
                    <div class="health-metric">
                        <span>Database</span>
                        <span class="status-indicator online">
                            <i class="fas fa-database"></i> ${data.database}
                        </span>
                    </div>
                    <div class="health-metric">
                        <span>Uptime</span>
                        <span>${Math.floor(data.uptime / 60)} minutes</span>
                    </div>
                    <div class="health-metric">
                        <span>Memory Usage</span>
                        <span>${data.memory.used}MB / ${data.memory.total}MB</span>
                    </div>
                `;
            } else {
                healthStatus.innerHTML = '<div class="loading-message">Access denied</div>';
            }
        } catch (error) {
            document.getElementById('healthStatus').innerHTML = '<div class="loading-message">Error loading health data</div>';
        }
    }

    viewUser(userId) {
        // Simple alert for demo - in real app would open modal
        const user = this.users.find(u => u._id === userId);
        if (user) {
            alert(`User Details:\nName: ${user.profile.firstName} ${user.profile.lastName}\nEmail: ${user.email}\nRole: ${user.role}\nDepartment: ${user.profile.department || 'N/A'}`);
        }
    }

    editUser(userId) {
        // Simple prompt for demo - in real app would open edit modal
        const user = this.users.find(u => u._id === userId);
        if (user) {
            const newDepartment = prompt(`Edit department for ${user.username}:`, user.profile.department || '');
            if (newDepartment !== null) {
                // In real app, would make API call to update user
                alert('User update feature would be implemented here');
            }
        }
    }

    showNotification(message, type = 'info') {
        // Simple notification system
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 10px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#667eea'};
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new UserPortalApp();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
