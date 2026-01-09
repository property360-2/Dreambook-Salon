/**
 * AsyncList - Reusable async search, filter, and pagination module
 *
 * Usage:
 *   new AsyncList({
 *     formSelector: '#filterForm',
 *     resultsSelector: '#resultsContainer',
 *     statusSelector: '#statusText',
 *     debounceDelay: 250
 *   });
 */
class AsyncList {
  constructor(options) {
    this.form = document.querySelector(options.formSelector);
    this.resultsContainer = document.querySelector(options.resultsSelector);
    this.statusText = document.querySelector(options.statusSelector);
    this.debounceDelay = options.debounceDelay || 250;
    this.onSuccess = options.onSuccess || null;
    this.onError = options.onError || null;

    if (!this.form || !this.resultsContainer) {
      console.warn('AsyncList: Required elements not found');
      return;
    }

    this.debounceTimer = null;
    this.init();
  }

  init() {
    // Prevent default form submission
    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      this.performSearch();
    });

    // Debounced input listeners for text inputs
    this.form.querySelectorAll('input[type="text"], input[type="search"]').forEach(input => {
      input.addEventListener('input', () => this.debounceSearch());
    });

    // Immediate search on select/date changes
    this.form.querySelectorAll('select, input[type="date"]').forEach(input => {
      input.addEventListener('change', () => this.performSearch());
    });

    // Delegate pagination clicks
    this.resultsContainer.addEventListener('click', (e) => {
      const link = e.target.closest('a[data-async-pagination="true"]');
      if (link) {
        e.preventDefault();
        this.performSearch(link.href);
      }
    });

    // Handle clear/reset buttons
    this.form.querySelectorAll('[data-async-clear]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.clearFilters();
      });
    });
  }

  setStatus(text) {
    if (this.statusText) {
      this.statusText.textContent = text;
    }
  }

  setLoading(loading) {
    this.form.classList.toggle('opacity-60', loading);
    this.form.classList.toggle('pointer-events-none', loading);

    // Update submit button
    const submitBtn = this.form.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = loading;
      if (loading) {
        submitBtn.dataset.originalText = submitBtn.textContent;
        submitBtn.textContent = 'Loading...';
      } else if (submitBtn.dataset.originalText) {
        submitBtn.textContent = submitBtn.dataset.originalText;
      }
    }
  }

  buildUrl(targetUrl) {
    const url = new URL(targetUrl || this.form.action, window.location.origin);
    const formData = new FormData(this.form);

    // Clear existing search params from form fields
    for (const key of formData.keys()) {
      url.searchParams.delete(key);
    }

    // Add non-empty form values
    for (const [key, value] of formData.entries()) {
      if (value && value.toString().trim()) {
        url.searchParams.set(key, value.toString().trim());
      }
    }

    return url.toString();
  }

  debounceSearch() {
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => this.performSearch(), this.debounceDelay);
  }

  async performSearch(targetUrl) {
    const url = this.buildUrl(targetUrl);
    this.setLoading(true);
    this.setStatus('Loading...');

    try {
      const response = await fetch(url, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      this.resultsContainer.innerHTML = data.html;

      // Update URL without reload
      window.history.replaceState({}, '', url);

      // Update status
      if (data.count !== undefined) {
        this.setStatus(`Found ${data.count} result(s)`);
      }

      // Callback
      if (this.onSuccess) {
        this.onSuccess(data);
      }

    } catch (error) {
      console.error('AsyncList error:', error);
      this.setStatus('Failed to load results. Please try again.');

      if (this.onError) {
        this.onError(error);
      }
    } finally {
      this.setLoading(false);
    }
  }

  clearFilters() {
    // Reset all form inputs
    this.form.querySelectorAll('input[type="text"], input[type="search"], input[type="date"]').forEach(input => {
      input.value = '';
    });
    this.form.querySelectorAll('select').forEach(select => {
      select.selectedIndex = 0;
    });

    // Perform search with cleared filters
    this.performSearch();
  }
}

// Export for module usage or attach to window
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AsyncList;
} else {
  window.AsyncList = AsyncList;
}
