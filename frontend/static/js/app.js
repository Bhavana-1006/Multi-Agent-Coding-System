/**
 * Synthetix - Multi-Agent Coding System
 * Application Master Controller
 * 
 * Manages:
 * - View Routing (Landing vs Studio Workspace) & URL hash synchronization
 * - Global Theme state, detection, toggle & persistent storage
 * - Sticky Navbar scroll dynamics
 * - Accessible Toast notifications using theme tokens
 * - Modal events & keyboard bindings (Escape key)
 */

// Global Theme Management
function applyTheme(theme) {
  const icon = document.getElementById('theme-icon');
  const isDark = (theme === 'dark');

  if (isDark) {
    document.documentElement.classList.add('dark');
    document.documentElement.classList.remove('light');
    try { localStorage.setItem('synthetix_theme', 'dark'); } catch (e) {}
    if (icon) icon.setAttribute('data-lucide', 'sun');
  } else {
    document.documentElement.classList.remove('dark');
    document.documentElement.classList.add('light');
    try { localStorage.setItem('synthetix_theme', 'light'); } catch (e) {}
    if (icon) icon.setAttribute('data-lucide', 'moon');
  }
  if (window.lucide) lucide.createIcons();
}
window.applyTheme = applyTheme;

function toggleTheme() {
  const isDark = document.documentElement.classList.contains('dark');
  applyTheme(isDark ? 'light' : 'dark');
}
window.toggleTheme = toggleTheme;

function initTheme() {
  let initialTheme = 'light';
  try {
    const stored = localStorage.getItem('synthetix_theme');
    if (stored === 'dark' || stored === 'light') {
      initialTheme = stored;
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      initialTheme = 'dark';
    }
  } catch (e) {}
  applyTheme(initialTheme);
}

// Global Router function
function navigateTo(view) {
  const landingView = document.getElementById('view-landing');
  const studioView = document.getElementById('view-studio');

  const navLandingBtn = document.getElementById('nav-btn-landing');
  const navStudioBtn = document.getElementById('nav-btn-studio');

  if (view === 'studio') {
    if (landingView) landingView.classList.add('hidden');
    if (studioView) studioView.classList.remove('hidden');

    if (navLandingBtn) {
      navLandingBtn.classList.remove('active', 'bg-brand-purple', 'text-white', 'shadow-sm', 'nav-pill-active');
      navLandingBtn.classList.add('nav-pill-inactive');
    }

    if (navStudioBtn) {
      navStudioBtn.classList.add('active', 'shadow-sm');
      navStudioBtn.classList.remove('text-theme-secondary');
    }

    window.location.hash = 'studio';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    if (studioView) studioView.classList.add('hidden');
    if (landingView) landingView.classList.remove('hidden');

    if (navStudioBtn) {
      navStudioBtn.classList.remove('active', 'shadow-sm');
      navStudioBtn.classList.add('text-theme-secondary');
    }

    if (navLandingBtn) {
      navLandingBtn.classList.add('active', 'nav-pill-active');
      navLandingBtn.classList.remove('text-theme-secondary', 'nav-pill-inactive');
    }

    window.location.hash = 'landing';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  if (window.LandingManager?.onViewChange) {
    window.LandingManager.onViewChange(view);
  }

  if (window.lucide) lucide.createIcons();
}
window.navigateTo = navigateTo;

// Problem modal global helpers for compatibility with tests and UI
function openProblemModal() {
  if (window.WorkspaceManager) {
    window.WorkspaceManager.openProblemModal();
  } else {
    document.getElementById('problem-modal')?.classList.remove('hidden');
  }
}
window.openProblemModal = openProblemModal;

function closeProblemModal() {
  if (window.WorkspaceManager) {
    window.WorkspaceManager.closeProblemModal();
  } else {
    document.getElementById('problem-modal')?.classList.add('hidden');
  }
}
window.closeProblemModal = closeProblemModal;

// Toast Notifications using design tokens
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  const typeStyles = {
    success: 'border-emerald-500/40 bg-theme-surface text-emerald-600 dark:text-emerald-400',
    error: 'border-theme-accent/50 bg-theme-surface text-theme-accent',
    warning: 'border-amber-500/40 bg-theme-surface text-amber-600 dark:text-amber-400',
    info: 'border-brand-purple/40 bg-theme-surface text-brand-purple'
  };

  const icons = {
    success: 'check-circle',
    error: 'alert-triangle',
    warning: 'alert-circle',
    info: 'info'
  };

  toast.className = `p-3.5 rounded-xl border shadow-lg flex items-center gap-3 text-xs font-medium toast-enter ${typeStyles[type] || typeStyles.info}`;
  toast.innerHTML = `
    <i data-lucide="${icons[type] || 'info'}" class="w-4 h-4 shrink-0"></i>
    <span class="flex-1 text-theme-main">${message}</span>
    <button onclick="this.parentElement.remove()" class="text-theme-muted hover:text-theme-main text-sm font-bold ml-1">×</button>
  `;

  container.appendChild(toast);
  if (window.lucide) lucide.createIcons();

  setTimeout(() => {
    toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-10px)';
    setTimeout(() => toast.remove(), 300);
  }, 4500);
}
window.showToast = showToast;

// Scroll watcher for sticky navbar appearance
function setupNavbarScroll() {
  const navbar = document.getElementById('main-navbar');
  if (!navbar) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 15) {
      navbar.classList.add('shadow-sm');
    } else {
      navbar.classList.remove('shadow-sm');
    }
  }, { passive: true });
}

// Load Backend System Configuration
async function loadSystemConfig() {
  try {
    const cfg = await ApiClient.getConfig();
    if (!cfg) return;

    if (cfg.active_provider) {
      const providerEl = document.getElementById('backend-provider-name');
      if (providerEl) providerEl.textContent = cfg.active_provider;
    }

    if (cfg.total_benchmark_problems) {
      const countEl = document.getElementById('nav-lib-count');
      if (countEl) countEl.textContent = `${cfg.total_benchmark_problems}+`;
    }
  } catch (err) {
    console.warn('System config load warning:', err);
  }
}

// Mobile menu toggle
function toggleMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  if (menu) {
    menu.classList.toggle('hidden');
  }
}
window.toggleMobileMenu = toggleMobileMenu;

// Global Escape Key Listener for Modals
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeProblemModal();
    if (window.AuthManager) window.AuthManager.closeModals();
    if (window.WorkspaceManager) {
      window.WorkspaceManager.closeSettings();
      window.WorkspaceManager.closeExplainModal();
    }
  }
});

// App Initialization
document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Theme early
  initTheme();

  // 2. Initialize Lucide Icons & Syntax Highlighting
  if (window.lucide) lucide.createIcons();
  if (window.hljs) hljs.highlightAll();

  // 3. Initialize Subsystems
  setupNavbarScroll();
  loadSystemConfig();
  if (window.AuthManager) window.AuthManager.init();
  if (window.LandingManager) window.LandingManager.init();
  if (window.WorkspaceManager) window.WorkspaceManager.init();

  // 4. Handle initial view routing
  const initialHash = window.location.hash.replace('#', '');
  if (initialHash === 'studio') {
    navigateTo('studio');
  } else if (initialHash === 'benchmarks') {
    navigateTo('landing');
    openProblemModal();
  } else if (initialHash === 'login') {
    navigateTo('landing');
    if (window.AuthManager) window.AuthManager.openLoginModal();
  } else if (initialHash === 'register') {
    navigateTo('landing');
    if (window.AuthManager) window.AuthManager.openRegisterModal();
  } else {
    navigateTo('landing');
  }
});

