/**
 * Async Utilities for Dreambook Salon
 * Provides toast notifications, AJAX helpers, and async form handling
 */

// Toast Notification System
const Toast = {
  container: null,

  init() {
    this.container = document.getElementById('toast-container');
  },

  show(message, type = 'info', duration = 5000) {
    if (!this.container) this.init();

    const toast = document.createElement('div');
    toast.className = `toast-notification animate-slide-in-right ${this.getTypeClasses(type)}`;

    const icon = this.getIcon(type);

    toast.innerHTML = `
      <div class="flex items-start gap-3 p-4 rounded-xl shadow-2xl border backdrop-blur-sm min-w-[300px] max-w-md">
        <div class="flex-shrink-0 mt-0.5">
          ${icon}
        </div>
        <div class="flex-1 text-sm font-medium">
          ${message}
        </div>
        <button class="flex-shrink-0 ml-3 text-white/70 hover:text-white transition-colors close-toast">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    `;

    this.container.appendChild(toast);

    // Close button functionality
    const closeBtn = toast.querySelector('.close-toast');
    closeBtn.addEventListener('click', () => this.remove(toast));

    // Auto remove after duration
    if (duration > 0) {
      setTimeout(() => this.remove(toast), duration);
    }

    return toast;
  },

  getTypeClasses(type) {
    const classes = {
      'success': 'bg-emerald-500/20 border-emerald-500/50 text-emerald-100',
      'error': 'bg-red-500/20 border-red-500/50 text-red-100',
      'warning': 'bg-amber-500/20 border-amber-500/50 text-amber-100',
      'info': 'bg-blue-500/20 border-blue-500/50 text-blue-100'
    };
    return classes[type] || classes.info;
  },

  getIcon(type) {
    const icons = {
      'success': '<svg class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
      'error': '<svg class="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
      'warning': '<svg class="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>',
      'info': '<svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
    };
    return icons[type] || icons.info;
  },

  remove(toast) {
    toast.classList.add('animate-slide-out-right');
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  },

  success(message, duration) {
    return this.show(message, 'success', duration);
  },

  error(message, duration) {
    return this.show(message, 'error', duration);
  },

  warning(message, duration) {
    return this.show(message, 'warning', duration);
  },

  info(message, duration) {
    return this.show(message, 'info', duration);
  }
};

// AJAX Helper Functions
const Ajax = {
  /**
   * Get CSRF token from cookies
   */
  getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  },

  /**
   * POST request helper
   */
  async post(url, data, options = {}) {
    const csrfToken = this.getCsrfToken();

    const defaultOptions = {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest'
      },
      credentials: 'same-origin'
    };

    // Handle FormData vs JSON
    if (data instanceof FormData) {
      // Don't set Content-Type, let browser set it with boundary
      options.body = data;
    } else {
      defaultOptions.headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(data);
    }

    const response = await fetch(url, { ...defaultOptions, ...options });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(error || `HTTP ${response.status}: ${response.statusText}`);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }

    return await response.text();
  },

  /**
   * GET request helper
   */
  async get(url, options = {}) {
    const defaultOptions = {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      },
      credentials: 'same-origin'
    };

    const response = await fetch(url, { ...defaultOptions, ...options });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }

    return await response.text();
  }
};

// Async Form Handler
const AsyncForm = {
  /**
   * Setup async form submission
   */
  setup(formSelector, options = {}) {
    const forms = document.querySelectorAll(formSelector);

    forms.forEach(form => {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = form.querySelector('[type="submit"]');
        const originalText = submitBtn ? submitBtn.textContent : '';

        try {
          // Disable submit button
          if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
            if (options.loadingText) {
              submitBtn.textContent = options.loadingText;
            }
          }

          // Get form data
          const formData = new FormData(form);
          const url = form.action || window.location.href;

          // Submit via AJAX
          const response = await Ajax.post(url, formData);

          // Handle success
          if (options.onSuccess) {
            options.onSuccess(response, form);
          } else {
            Toast.success('Operation completed successfully!');
          }

          // Optional: reset form
          if (options.resetOnSuccess) {
            form.reset();
          }

        } catch (error) {
          console.error('Form submission error:', error);

          if (options.onError) {
            options.onError(error, form);
          } else {
            Toast.error(error.message || 'An error occurred. Please try again.');
          }
        } finally {
          // Re-enable submit button
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            submitBtn.textContent = originalText;
          }
        }
      });
    });
  }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
  Toast.init();
});

// Export for global use
window.Toast = Toast;
window.Ajax = Ajax;
window.AsyncForm = AsyncForm;
