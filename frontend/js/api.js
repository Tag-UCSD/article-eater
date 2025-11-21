// Article Eater v18.4.1 - API Client
// Handles all communication with backend API

const API_BASE_URL = window.location.origin || 'http://localhost:8000';

class ArticleEaterAPI {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.apiKey = localStorage.getItem('ae_api_key');
  }

  // Generic request handler
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    if (this.apiKey) {
      config.headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    return this.request('/healthz');
  }

  // Jobs
  async submitJob(jobType, params, priority = 100) {
    return this.request('/jobs/', {
      method: 'POST',
      body: JSON.stringify({ job_type: jobType, params, priority })
    });
  }

  async getJobStatus(jobId) {
    return this.request(`/jobs/${jobId}`);
  }

  async listJobs(status = null, limit = 100) {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    params.append('limit', limit);
    return this.request(`/jobs/?${params}`);
  }

  // Library (articles)
  async listArticles(limit = 50, offset = 0) {
    return this.request(`/library/?limit=${limit}&offset=${offset}`);
  }

  async getArticle(articleId) {
    return this.request(`/library/${articleId}`);
  }

  async searchArticles(query) {
    return this.request(`/library/search?q=${encodeURIComponent(query)}`);
  }

  // Findings
  async getFindings(articleId) {
    return this.request(`/findings?article_id=${articleId}`);
  }

  async getAllFindings(limit = 100) {
    return this.request(`/findings?limit=${limit}`);
  }

  // Rules
  async listRules(limit = 50) {
    return this.request(`/rules?limit=${limit}`);
  }

  async getRule(ruleId) {
    return this.request(`/rules/${ruleId}`);
  }

  async getRuleEvidence(ruleId) {
    return this.request(`/rules/${ruleId}/evidence`);
  }

  // Usage & Costs
  async getUsage() {
    return this.request('/usage/me');
  }

  async getUsageAdmin() {
    return this.request('/usage/admin');
  }

  // Profile
  async getProfile() {
    return this.request('/profile');
  }

  async updateProfile(data) {
    return this.request('/profile', {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  }

  // API Keys
  async listAPIKeys() {
    return this.request('/profile/api-keys');
  }

  async addAPIKey(provider, key) {
    return this.request('/profile/api-keys', {
      method: 'POST',
      body: JSON.stringify({ provider, key })
    });
  }

  async deleteAPIKey(provider) {
    return this.request(`/profile/api-keys/${provider}`, {
      method: 'DELETE'
    });
  }
}

// UI Helper Functions
const UI = {
  // Show loading spinner
  showLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
      el.innerHTML = '<div class="spinner"></div> Loading...';
    }
  },

  // Show error message
  showError(elementId, message) {
    const el = document.getElementById(elementId);
    if (el) {
      el.innerHTML = `
        <div class="alert alert-error">
          <strong>Error:</strong> ${message}
        </div>
      `;
    }
  },

  // Show success message
  showSuccess(elementId, message) {
    const el = document.getElementById(elementId);
    if (el) {
      el.innerHTML = `
        <div class="alert alert-success">
          ${message}
        </div>
      `;
    }
  },

  // Format date
  formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  },

  // Format confidence score
  formatConfidence(score) {
    if (score === null || score === undefined) return 'N/A';
    const percentage = Math.round(score * 100);
    let label = 'Low';
    if (percentage >= 80) label = 'High';
    else if (percentage >= 60) label = 'Medium';
    
    return `${percentage}% (${label})`;
  },

  // Get confidence color
  getConfidenceColor(score) {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  },

  // Create badge
  badge(text, type = 'gray') {
    return `<span class="badge badge-${type}">${text}</span>`;
  },

  // Create progress bar
  progressBar(percentage, type = 'primary') {
    return `
      <div class="progress-bar">
        <div class="progress-fill ${type}" style="width: ${percentage}%"></div>
      </div>
    `;
  },

  // Modal functions
  showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
    }
  },

  hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
    }
  },

  // Toast notification
  toast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 10000;
      min-width: 300px;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.transition = 'opacity 0.3s';
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
};

// Data formatting utilities
const DataUtils = {
  // Format large numbers
  formatNumber(num) {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  },

  // Format currency
  formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  },

  // Calculate percentage
  percentage(value, total) {
    if (total === 0) return 0;
    return Math.round((value / total) * 100);
  },

  // Truncate text
  truncate(text, maxLength) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  },

  // Extract DOI from various formats
  extractDOI(text) {
    const doiRegex = /10\.\d{4,9}\/[-._;()\/:A-Z0-9]+/i;
    const match = text.match(doiRegex);
    return match ? match[0] : null;
  },

  // Debounce function for search
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
};

// Chart utilities (simple bar/line charts without dependencies)
const ChartUtils = {
  // Create simple bar chart
  createBarChart(data, containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const maxValue = Math.max(...data.map(d => d.value));
    const chartHTML = data.map(item => {
      const percentage = (item.value / maxValue) * 100;
      return `
        <div style="margin-bottom: 12px;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="font-size: 14px; font-weight: 500;">${item.label}</span>
            <span style="font-size: 14px; color: #6B7280;">${item.value}</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${percentage}%;"></div>
          </div>
        </div>
      `;
    }).join('');

    container.innerHTML = chartHTML;
  },

  // Create simple line chart (sparkline)
  createSparkline(data, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;

    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * 100;
      const y = 100 - ((value - min) / range) * 100;
      return `${x},${y}`;
    }).join(' ');

    container.innerHTML = `
      <svg width="100%" height="60" style="display: block;">
        <polyline
          points="${points}"
          fill="none"
          stroke="#182B49"
          stroke-width="2"
          style="vector-effect: non-scaling-stroke;"
        />
      </svg>
    `;
  }
};

// Export for use in HTML files
window.ArticleEaterAPI = ArticleEaterAPI;
window.UI = UI;
window.DataUtils = DataUtils;
window.ChartUtils = ChartUtils;

// Initialize API client
window.api = new ArticleEaterAPI();

// Global error handler
window.addEventListener('unhandledrejection', event => {
  console.error('Unhandled promise rejection:', event.reason);
  UI.toast('An unexpected error occurred. Please try again.', 'error');
});
