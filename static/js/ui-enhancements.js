/**
 * UI Enhancements for Dreambook Salon
 * Provides loading states, confirmations, toasts, and other UX improvements
 */

// ============================================================================
// LOADING STATES FOR FORMS
// ============================================================================

/**
 * Adds loading state to form submit buttons
 * Usage: Add class 'form-with-loading' to any form
 */
function initFormLoadingStates() {
  document.querySelectorAll('form.form-with-loading').forEach(form => {
    form.addEventListener('submit', function(e) {
      const submitBtn = this.querySelector('button[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        // Store original content
        submitBtn.dataset.originalText = submitBtn.innerHTML;

        // Disable and show loading
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        submitBtn.innerHTML = `
          <svg class="animate-spin inline-block h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Processing...
        `;
      }
    });
  });
}

/**
 * Generic function to add loading state to any button
 */
function setButtonLoading(button, loading = true) {
  if (loading) {
    button.dataset.originalText = button.innerHTML;
    button.disabled = true;
    button.classList.add('opacity-75', 'cursor-not-allowed');
    button.innerHTML = `
      <svg class="animate-spin inline-block h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      ${button.dataset.loadingText || 'Processing...'}
    `;
  } else {
    button.disabled = false;
    button.classList.remove('opacity-75', 'cursor-not-allowed');
    button.innerHTML = button.dataset.originalText || button.innerHTML;
  }
}

// ============================================================================
// CONFIRMATION MODALS
// ============================================================================

/**
 * Creates and shows a confirmation modal
 */
function showConfirmationModal(options = {}) {
  const defaults = {
    title: 'Are you sure?',
    message: 'This action cannot be undone.',
    confirmText: 'Confirm',
    cancelText: 'Cancel',
    confirmClass: 'btn-primary',
    isDanger: false,
    onConfirm: () => {},
    onCancel: () => {}
  };

  const config = { ...defaults, ...options };

  // Create modal HTML
  const modalHTML = `
    <div id="confirmModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 bg-black/70 transition-opacity backdrop-blur-sm" aria-hidden="true"></div>

        <!-- Center modal -->
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <!-- Modal panel -->
        <div class="inline-block align-bottom bg-light-surface rounded-2xl border border-light-border px-6 pt-6 pb-6 text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full animate-slide-up">
          <div class="sm:flex sm:items-start">
            <div class="mx-auto flex-shrink-0 flex items-center justify-center h-14 w-14 rounded-xl ${config.isDanger ? 'bg-red-500/10 border border-red-500/20' : 'bg-primary-500/10 border border-primary-500/20'} sm:mx-0 sm:h-12 sm:w-12">
              ${config.isDanger ?
                '<svg class="h-7 w-7 text-red-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>' :
                '<svg class="h-7 w-7 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'
              }
            </div>
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left flex-1">
              <h3 class="text-xl font-bold text-light-text mb-2" id="modal-title">
                ${config.title}
              </h3>
              <div class="mt-2">
                <p class="text-base text-light-muted">
                  ${config.message}
                </p>
              </div>
            </div>
          </div>
          <div class="mt-6 flex flex-col sm:flex-row-reverse gap-3">
            <button type="button" id="confirmBtn" class="btn ${config.isDanger ? 'bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20' : config.confirmClass} flex-1">
              ${config.confirmText}
            </button>
            <button type="button" id="cancelBtn" class="btn btn-ghost flex-1">
              ${config.cancelText}
            </button>
          </div>
        </div>
      </div>
    </div>
  `;

  // Insert modal into DOM
  const modalContainer = document.createElement('div');
  modalContainer.innerHTML = modalHTML;
  document.body.appendChild(modalContainer);

  // Get modal elements
  const modal = document.getElementById('confirmModal');
  const confirmBtn = document.getElementById('confirmBtn');
  const cancelBtn = document.getElementById('cancelBtn');
  const overlay = modal.querySelector('.fixed.inset-0.bg-black\\/70');

  // Close modal function
  function closeModal() {
    modal.classList.add('opacity-0');
    setTimeout(() => {
      modalContainer.remove();
    }, 200);
  }

  // Event listeners
  confirmBtn.addEventListener('click', () => {
    config.onConfirm();
    closeModal();
  });

  cancelBtn.addEventListener('click', () => {
    config.onCancel();
    closeModal();
  });

  overlay.addEventListener('click', () => {
    config.onCancel();
    closeModal();
  });

  // ESC key to close
  document.addEventListener('keydown', function escHandler(e) {
    if (e.key === 'Escape') {
      config.onCancel();
      closeModal();
      document.removeEventListener('keydown', escHandler);
    }
  });
}

/**
 * Adds confirmation to forms with class 'confirm-action'
 * Usage: Add data attributes to form:
 * - data-confirm-title
 * - data-confirm-message
 * - data-confirm-text
 * - data-danger="true" (optional)
 */
function initConfirmationForms() {
  document.querySelectorAll('form.confirm-action').forEach(form => {
    form.addEventListener('submit', function(e) {
      e.preventDefault();

      const title = this.dataset.confirmTitle || 'Confirm Action';
      const message = this.dataset.confirmMessage || 'Are you sure you want to proceed?';
      const confirmText = this.dataset.confirmText || 'Confirm';
      const isDanger = this.dataset.danger === 'true';

      showConfirmationModal({
        title,
        message,
        confirmText,
        isDanger,
        onConfirm: () => {
          // Remove the confirm-action class temporarily to prevent infinite loop
          this.classList.remove('confirm-action');
          this.submit();
        }
      });
    });
  });
}

// ============================================================================
// TOAST NOTIFICATIONS
// ============================================================================

/**
 * Creates a toast container if it doesn't exist
 */
function ensureToastContainer() {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed top-24 right-4 z-50 space-y-3 max-w-md';
    container.setAttribute('aria-live', 'polite');
    container.setAttribute('aria-atomic', 'true');
    document.body.appendChild(container);
  }
  return container;
}

/**
 * Shows a toast notification
 */
function showToast(message, type = 'info', duration = 5000) {
  const container = ensureToastContainer();

  const icons = {
    success: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
    error: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
    warning: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>',
    info: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
  };

  const colors = {
    success: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
    error: 'bg-red-500/10 border-red-500/20 text-red-400',
    warning: 'bg-amber-500/10 border-amber-500/20 text-amber-400',
    info: 'bg-primary-500/10 border-primary-500/20 text-primary-600'
  };

  const toast = document.createElement('div');
  toast.className = `toast ${colors[type]} animate-slide-up`;
  toast.innerHTML = `
    <div class="flex items-start gap-3">
      <div class="flex-shrink-0 mt-0.5">
        ${icons[type]}
      </div>
      <div class="flex-1">
        <p class="text-sm font-medium text-light-text">${message}</p>
      </div>
      <button type="button" class="flex-shrink-0 hover:opacity-75 transition-opacity" onclick="this.parentElement.parentElement.remove()">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>
  `;

  container.appendChild(toast);

  // Auto remove after duration
  if (duration > 0) {
    setTimeout(() => {
      toast.classList.add('opacity-0', 'transform', 'translate-x-8');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
}

/**
 * Convert existing flash messages to toasts
 */
function convertFlashMessagesToToasts() {
  const flashContainer = document.querySelector('.container-custom.mt-6');
  if (flashContainer) {
    const alerts = flashContainer.querySelectorAll('.alert');
    alerts.forEach(alert => {
      const message = alert.textContent.trim();
      let type = 'info';

      if (alert.classList.contains('alert-success')) type = 'success';
      else if (alert.classList.contains('alert-error')) type = 'error';
      else if (alert.classList.contains('alert-warning')) type = 'warning';

      showToast(message, type);
    });

    // Hide the flash message container
    if (alerts.length > 0) {
      flashContainer.style.display = 'none';
    }
  }
}

// ============================================================================
// REAL-TIME FORM VALIDATION
// ============================================================================

/**
 * Adds real-time validation to forms with class 'validate-realtime'
 */
function initRealtimeValidation() {
  document.querySelectorAll('form.validate-realtime').forEach(form => {
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');

    inputs.forEach(input => {
      // Email validation
      if (input.type === 'email') {
        input.addEventListener('blur', function() {
          const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          validateInput(this, emailPattern.test(this.value), 'Please enter a valid email address');
        });
      }

      // Password validation (minimum 8 characters)
      if (input.type === 'password' && input.name.includes('password1')) {
        input.addEventListener('input', function() {
          const strength = checkPasswordStrength(this.value);
          showPasswordStrength(this, strength);
        });
      }

      // Password confirmation
      if (input.type === 'password' && input.name.includes('password2')) {
        input.addEventListener('input', function() {
          const password1 = form.querySelector('input[name*="password1"]');
          validateInput(this, this.value === password1.value, 'Passwords do not match');
        });
      }

      // Required field validation
      input.addEventListener('blur', function() {
        if (this.hasAttribute('required')) {
          validateInput(this, this.value.trim() !== '', 'This field is required');
        }
      });
    });
  });
}

function validateInput(input, isValid, errorMessage) {
  const existingError = input.parentElement.querySelector('.validation-error');
  const existingSuccess = input.parentElement.querySelector('.validation-success');

  // Remove existing messages
  if (existingError) existingError.remove();
  if (existingSuccess) existingSuccess.remove();

  if (!isValid && input.value.trim() !== '') {
    input.classList.add('input-error');
    input.classList.remove('border-emerald-500/50');

    const errorDiv = document.createElement('p');
    errorDiv.className = 'validation-error mt-1 text-sm text-red-400 flex items-center gap-1';
    errorDiv.innerHTML = `
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>
      ${errorMessage}
    `;
    input.parentElement.appendChild(errorDiv);
  } else if (isValid && input.value.trim() !== '') {
    input.classList.remove('input-error');
    input.classList.add('border-emerald-500/50');

    const successDiv = document.createElement('p');
    successDiv.className = 'validation-success mt-1 text-sm text-emerald-400 flex items-center gap-1';
    successDiv.innerHTML = `
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
      </svg>
      Looks good!
    `;
    input.parentElement.appendChild(successDiv);
  } else {
    input.classList.remove('input-error', 'border-emerald-500/50');
  }
}

function checkPasswordStrength(password) {
  let strength = 0;
  if (password.length >= 8) strength++;
  if (password.length >= 12) strength++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
  if (/\d/.test(password)) strength++;
  if (/[^a-zA-Z\d]/.test(password)) strength++;
  return Math.min(strength, 4);
}

function showPasswordStrength(input, strength) {
  const existingIndicator = input.parentElement.querySelector('.password-strength');
  if (existingIndicator) existingIndicator.remove();

  if (input.value.length === 0) return;

  const labels = ['Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];
  const colors = ['bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-emerald-500', 'bg-green-500'];

  const indicator = document.createElement('div');
  indicator.className = 'password-strength mt-2';
  indicator.innerHTML = `
    <div class="flex gap-1 mb-1">
      ${Array.from({length: 5}, (_, i) =>
        `<div class="h-1 flex-1 rounded-full ${i < strength ? colors[strength] : 'bg-light-border'}"></div>`
      ).join('')}
    </div>
    <p class="text-xs ${strength < 2 ? 'text-red-400' : strength < 4 ? 'text-amber-400' : 'text-emerald-400'}">
      Password strength: ${labels[strength]}
    </p>
  `;

  input.parentElement.appendChild(indicator);
}

// ============================================================================
// SKELETON LOADERS
// ============================================================================

/**
 * Shows skeleton loader for elements with class 'skeleton-target'
 */
function showSkeletonLoader(targetSelector) {
  const target = document.querySelector(targetSelector);
  if (!target) return;

  target.innerHTML = `
    <div class="animate-pulse space-y-4">
      <div class="h-4 bg-light-border rounded w-3/4"></div>
      <div class="h-4 bg-light-border rounded w-full"></div>
      <div class="h-4 bg-light-border rounded w-5/6"></div>
    </div>
  `;
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
  // Initialize all enhancements
  initFormLoadingStates();
  initConfirmationForms();
  convertFlashMessagesToToasts();
  initRealtimeValidation();

  console.log('✨ UI Enhancements loaded successfully');
});

// ============================================================================
// GLOBAL EXPORTS
// ============================================================================

window.showToast = showToast;
window.showConfirmationModal = showConfirmationModal;
window.setButtonLoading = setButtonLoading;
window.showSkeletonLoader = showSkeletonLoader;
