/**
 * Synthetix - Multi-Agent Coding System
 * Frontend Authentication Manager
 * 
 * Handles client-side validation, mock registration & login,
 * state persistence, and automatic redirection to workspace.
 */

const AuthManager = {
  currentUser: null,

  init() {
    // Check for saved session
    const saved = localStorage.getItem('synthetix_auth_user');
    if (saved) {
      try {
        this.currentUser = JSON.parse(saved);
      } catch (e) {
        this.currentUser = null;
      }
    }
    this.updateUI();
    this.setupListeners();
  },

  setupListeners() {
    // Login form submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
      loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleLogin();
      });
    }

    // Register form submission
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
      registerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleRegister();
      });
    }
  },

  openLoginModal() {
    this.closeModals();
    const modal = document.getElementById('auth-modal-login');
    if (modal) {
      modal.classList.remove('hidden');
      const emailInput = document.getElementById('login-email');
      if (emailInput) emailInput.focus();
    }
  },

  openRegisterModal() {
    this.closeModals();
    const modal = document.getElementById('auth-modal-register');
    if (modal) {
      modal.classList.remove('hidden');
      const nameInput = document.getElementById('reg-name');
      if (nameInput) nameInput.focus();
    }
  },

  closeModals() {
    const loginModal = document.getElementById('auth-modal-login');
    const registerModal = document.getElementById('auth-modal-register');
    if (loginModal) loginModal.classList.add('hidden');
    if (registerModal) registerModal.classList.add('hidden');
  },

  handleLogin() {
    const email = document.getElementById('login-email')?.value.trim();
    const password = document.getElementById('login-password')?.value;
    const rememberMe = document.getElementById('login-remember')?.checked;
    const errorEl = document.getElementById('login-error');

    if (errorEl) errorEl.classList.add('hidden');

    // Validation
    if (!email || !password) {
      this.showError(errorEl, 'Please fill in both email and password.');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      this.showError(errorEl, 'Please enter a valid email address.');
      return;
    }

    if (password.length < 6) {
      this.showError(errorEl, 'Password must be at least 6 characters.');
      return;
    }

    // Simulated successful login
    const user = {
      name: email.split('@')[0],
      email: email,
      token: 'mock-jwt-' + Math.random().toString(36).substring(2)
    };

    this.currentUser = user;
    if (rememberMe) {
      localStorage.setItem('synthetix_auth_user', JSON.stringify(user));
    } else {
      sessionStorage.setItem('synthetix_auth_user', JSON.stringify(user));
    }

    this.updateUI();
    this.closeModals();
    window.showToast?.(`Welcome back, ${user.name}!`, 'success');

    // Redirect to studio workspace
    if (window.navigateTo) {
      window.navigateTo('studio');
    }
  },

  handleRegister() {
    const name = document.getElementById('reg-name')?.value.trim();
    const email = document.getElementById('reg-email')?.value.trim();
    const password = document.getElementById('reg-password')?.value;
    const confirmPassword = document.getElementById('reg-confirm-password')?.value;
    const errorEl = document.getElementById('register-error');

    if (errorEl) errorEl.classList.add('hidden');

    if (!name || !email || !password || !confirmPassword) {
      this.showError(errorEl, 'Please complete all fields.');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      this.showError(errorEl, 'Please enter a valid email address.');
      return;
    }

    if (password.length < 6) {
      this.showError(errorEl, 'Password must be at least 6 characters.');
      return;
    }

    if (password !== confirmPassword) {
      this.showError(errorEl, 'Passwords do not match.');
      return;
    }

    // Simulated successful registration
    const user = {
      name: name,
      email: email,
      token: 'mock-jwt-' + Math.random().toString(36).substring(2)
    };

    this.currentUser = user;
    localStorage.setItem('synthetix_auth_user', JSON.stringify(user));

    this.updateUI();
    this.closeModals();
    window.showToast?.(`Account created successfully! Welcome, ${user.name}.`, 'success');

    // Redirect to studio workspace
    if (window.navigateTo) {
      window.navigateTo('studio');
    }
  },

  logout() {
    this.currentUser = null;
    localStorage.removeItem('synthetix_auth_user');
    sessionStorage.removeItem('synthetix_auth_user');
    this.updateUI();
    window.showToast?.('Logged out successfully.', 'info');
  },

  showError(el, message) {
    if (el) {
      el.textContent = message;
      el.classList.remove('hidden');
    } else {
      window.showToast?.(message, 'error');
    }
  },

  updateUI() {
    const unauthNav = document.getElementById('nav-unauth-actions');
    const authNav = document.getElementById('nav-auth-actions');
    const userNameEl = document.getElementById('nav-user-name');

    if (this.currentUser) {
      if (unauthNav) unauthNav.classList.add('hidden');
      if (authNav) authNav.classList.remove('hidden');
      if (userNameEl) userNameEl.textContent = this.currentUser.name;
    } else {
      if (unauthNav) unauthNav.classList.remove('hidden');
      if (authNav) authNav.classList.add('hidden');
    }
  }
};

window.AuthManager = AuthManager;
