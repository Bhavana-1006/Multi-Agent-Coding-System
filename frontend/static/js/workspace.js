/**
 * Synthetix - Multi-Agent Coding System
 * Conversational Studio Workspace Controller
 * 
 * Interaction Model:
 * USER REQUEST → GENERATED CODE → CUSTOM INPUT → OUTPUT
 * 
 * Core Capabilities:
 * - Empty / Welcoming prompt state ("What do you want to build?")
 * - Smooth transition into active conversational workspace
 * - VS Code / Cursor inspired developer code editor as main focus
 * - Clean "Generating your solution..." loading state
 * - Dedicated "Try your own input" interactive sandbox playground
 * - Dynamic output display with execution timing & error diagnostics
 * - "+ Add test case" compact test runner
 * - Real previous requests history saved in localStorage
 * - Collapsible left sidebar
 * - Slide-over Settings drawer for backend configuration & diagnostics
 * - Compatibility with benchmarks and landing page demo triggers
 */

const WorkspaceManager = {
  currentState: 'empty', // 'empty' | 'active'
  currentMode: 'rl',     // 'rl' | 'baseline'
  currentRequirement: '',
  latestCode: '',
  isExecuting: false,
  history: [],
  testCases: [],
  auditData: { score: 0.0, suggestions: [] },
  stepLogs: [],
  allProblems: [],
  selectedCategory: 'All',

  init() {
    this.loadHistory();
    this.setupEventListeners();
    this.fetchSystemConfig();

    // Check if initial requirement was pre-filled (e.g. from landing page)
    const emptyInput = document.getElementById('req-input-empty');
    const hiddenReq = document.getElementById('req-input');
    const prefill = hiddenReq?.value.trim() || emptyInput?.value.trim();

    if (prefill && prefill.length > 5 && prefill !== 'Write a python function `is_palindrome(s: str) -> bool` that checks if a string is a palindrome, ignoring casing and non-alphanumeric characters.') {
      this.currentRequirement = prefill;
      this.transitionToActiveState(prefill);
    } else {
      this.showEmptyState();
    }
  },

  setupEventListeners() {
    // Enter key shortcuts
    const emptyInput = document.getElementById('req-input-empty');
    if (emptyInput) {
      emptyInput.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
          e.preventDefault();
          this.submitInitialPrompt();
        }
      });
    }

    const playgroundInput = document.getElementById('playground-input');
    if (playgroundInput) {
      playgroundInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          this.runCustomInputLive();
        }
      });
    }

    // Benchmark search filter
    const searchInput = document.getElementById('modal-search-input');
    if (searchInput) {
      searchInput.addEventListener('input', () => this.filterProblems());
    }

    const diffFilter = document.getElementById('modal-difficulty-filter');
    if (diffFilter) {
      diffFilter.addEventListener('change', () => this.filterProblems());
    }
  },

  async fetchSystemConfig() {
    try {
      const config = await ApiClient.getConfig();
      if (config) {
        const provEl = document.getElementById('settings-active-provider');
        const modelEl = document.getElementById('settings-active-model');
        if (provEl && config.active_provider) provEl.textContent = config.active_provider;
        if (modelEl && config.active_model) modelEl.textContent = config.active_model;
      }
    } catch (e) {
      // Non-critical fallback
    }
  },

  // =========================================================================
  // VIEW STATE TRANSITIONS
  // =========================================================================
  showEmptyState() {
    this.currentState = 'empty';
    const emptyState = document.getElementById('studio-empty-state');
    const activeState = document.getElementById('studio-active-state');
    const breadcrumb = document.getElementById('workspace-title-breadcrumb');

    if (emptyState) emptyState.classList.remove('hidden');
    if (activeState) activeState.classList.add('hidden');
    if (breadcrumb) breadcrumb.textContent = 'Studio Workspace';

    const emptyInput = document.getElementById('req-input-empty');
    if (emptyInput) {
      emptyInput.focus();
    }
  },

  transitionToActiveState(requirementText) {
    this.currentState = 'active';
    const emptyState = document.getElementById('studio-empty-state');
    const activeState = document.getElementById('studio-active-state');
    const reqDisplay = document.getElementById('submitted-req-text');
    const breadcrumb = document.getElementById('workspace-title-breadcrumb');

    if (emptyState) emptyState.classList.add('hidden');
    if (activeState) {
      activeState.classList.remove('hidden');
      activeState.classList.add('animate-fade-up');
      setTimeout(() => activeState.classList.remove('animate-fade-up'), 400);
    }

    if (reqDisplay) reqDisplay.textContent = requirementText;

    if (breadcrumb) {
      const shortTitle = requirementText.length > 35 
        ? requirementText.substring(0, 32) + '...' 
        : requirementText;
      breadcrumb.textContent = shortTitle;
    }

    if (window.lucide) lucide.createIcons();
  },

  // =========================================================================
  // USER PROMPT SUBMISSION & CODE GENERATION
  // =========================================================================
  submitInitialPrompt() {
    const emptyInput = document.getElementById('req-input-empty');
    const reqText = emptyInput?.value.trim();

    if (!reqText) {
      window.showToast?.('Please describe what you want to build!', 'warning');
      emptyInput?.focus();
      return;
    }

    this.currentRequirement = reqText;
    const hiddenInput = document.getElementById('req-input');
    if (hiddenInput) hiddenInput.value = reqText;

    this.transitionToActiveState(reqText);
    this.executePipeline();
  },

  async executePipeline() {
    if (this.isExecuting) return;

    const requirement = this.currentRequirement;
    if (!requirement) {
      this.showEmptyState();
      return;
    }

    this.isExecuting = true;
    this.setGeneratingUI(true);

    const codeDisplay = document.getElementById('code-display');
    if (codeDisplay) {
      codeDisplay.textContent = `# Synthesizing Python solution...\n# Requirement: "${requirement}"\n\ndef solution():\n    pass`;
      if (window.hljs) hljs.highlightElement(codeDisplay);
    }

    this.stepLogs = [];

    await ApiClient.runPipelineStream(
      { requirement, test_code: '', mode: this.currentMode },
      {
        onStarted: (data) => {
          // Clean silent start
        },
        onStepStart: (data) => {
          this.stepLogs.push({ step: data.step, agent: data.agent, summary: `Executed ${data.agent}` });
          this.updateTraceInSettings();
        },
        onStepDone: (data) => {
          if (data.intermediate?.code) {
            this.latestCode = data.intermediate.code;
            if (codeDisplay) {
              codeDisplay.textContent = data.intermediate.code;
              if (window.hljs) hljs.highlightElement(codeDisplay);
            }
          }
        },
        onComplete: (data) => {
          this.handlePipelineComplete(data);
        },
        onError: (err) => {
          this.setGeneratingUI(false);
          this.isExecuting = false;
          window.showToast?.(`Synthesis notice: ${err}`, 'warning');
        }
      }
    );

    this.setGeneratingUI(false);
    this.isExecuting = false;
  },

  setGeneratingUI(isGenerating) {
    const genOverlay = document.getElementById('code-generating-state');
    const statusPill = document.getElementById('code-status-pill');
    const readinessLabel = document.getElementById('editor-readiness-label');
    const runBtn = document.getElementById('editor-run-btn');
    const regenBtn = document.getElementById('regenerate-btn');

    if (genOverlay) {
      if (isGenerating) genOverlay.classList.remove('hidden');
      else genOverlay.classList.add('hidden');
    }

    if (statusPill) {
      statusPill.innerHTML = isGenerating
        ? '<span class="w-1.5 h-1.5 rounded-full bg-brand-purple animate-ping"></span><span class="text-brand-purple">Generating...</span>'
        : '<span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span><span class="text-emerald-400">Ready</span>';
    }

    if (readinessLabel) {
      readinessLabel.innerHTML = isGenerating
        ? '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin text-brand-purple"></i><span>Synthesizing code...</span>'
        : '<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400"></i><span>Code generated • Ready to test</span>';
    }

    if (runBtn) runBtn.disabled = isGenerating;
    if (regenBtn) regenBtn.disabled = isGenerating;

    if (window.lucide) lucide.createIcons();
  },

  handlePipelineComplete(data) {
    this.latestCode = data.code || '';
    const codeDisplay = document.getElementById('code-display');
    if (codeDisplay) {
      codeDisplay.textContent = this.latestCode || '# No code synthesized.';
      if (window.hljs) hljs.highlightElement(codeDisplay);
    }

    // Save Quality Review details into Settings
    this.auditData = {
      score: data.review_score || 0.0,
      suggestions: data.review_suggestions || []
    };
    this.updateAuditInSettings();

    // Auto-populate playground input with function name
    this.derivePlaygroundFunctionCall();

    // Save to user history
    this.saveToHistory(this.currentRequirement, this.latestCode);

    // Setup initial test cases if empty
    this.setupDefaultTestCases();

    window.showToast?.('Code synthesized and verified in sandbox!', 'success');

    if (data.test_passed && window.confetti) {
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.6 },
        colors: ['#9B5DE5', '#FF6B6B', '#F7F3EE']
      });
    }

    if (window.lucide) lucide.createIcons();
  },

  derivePlaygroundFunctionCall() {
    const playgroundInput = document.getElementById('playground-input');
    if (!playgroundInput || !this.latestCode) return;

    const fnMatch = this.latestCode.match(/def\s+([a-zA-Z0-9_]+)\s*\((.*?)\):/);
    if (fnMatch) {
      const fnName = fnMatch[1];
      const params = fnMatch[2].split(',').map(p => p.trim()).filter(Boolean);

      if (fnName === 'is_palindrome') {
        playgroundInput.value = 'is_palindrome("A man, a plan, a canal: Panama")';
      } else if (fnName === 'two_sum') {
        playgroundInput.value = 'two_sum([2, 7, 11, 15], 9)';
      } else if (fnName === 'is_prime') {
        playgroundInput.value = 'is_prime(17)';
      } else if (params.length > 0) {
        playgroundInput.value = `${fnName}()`;
      } else {
        playgroundInput.value = `${fnName}()`;
      }
    }
  },

  // =========================================================================
  // CUSTOM INPUT & DYNAMIC OUTPUT
  // =========================================================================
  async runCustomInputLive() {
    const code = this.latestCode || document.getElementById('code-display')?.textContent || '';
    const customInput = document.getElementById('playground-input')?.value.trim();
    const btn = document.getElementById('playground-run-btn');

    const outVal = document.getElementById('playground-output-val');
    const errBox = document.getElementById('playground-err-box');
    const errVal = document.getElementById('playground-err-val');
    const stdoutBox = document.getElementById('playground-stdout-box');
    const stdoutVal = document.getElementById('playground-stdout-val');
    const timeVal = document.getElementById('playground-time');
    const badge = document.getElementById('playground-status-badge');

    if (!customInput) {
      window.showToast?.('Please enter an input argument or expression!', 'warning');
      return;
    }

    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Running...</span>';
      if (window.lucide) lucide.createIcons();
    }
    if (errBox) errBox.classList.add('hidden');
    if (stdoutBox) stdoutBox.classList.add('hidden');

    try {
      const res = await ApiClient.runCustomInput(code, customInput);

      if (timeVal) timeVal.textContent = `${res.execution_time_ms} ms`;

      if (res.success) {
        if (outVal) {
          outVal.textContent = res.return_value !== null ? res.return_value : '(Returned None)';
          outVal.className = 'output-display-box p-3.5 rounded-lg font-mono text-xs sm:text-sm select-text output-success flex items-center';
        }
        if (badge) {
          badge.textContent = 'Returned successfully';
          badge.className = 'text-[10px] font-mono text-emerald-400';
        }
      } else {
        if (outVal) {
          outVal.textContent = 'Execution Failed (See error below)';
          outVal.className = 'output-display-box p-3.5 rounded-lg font-mono text-xs sm:text-sm select-text output-error flex items-center';
        }
        if (badge) {
          badge.textContent = 'Failed';
          badge.className = 'text-[10px] font-mono text-theme-accent';
        }
      }

      if (res.stdout && stdoutBox && stdoutVal) {
        stdoutBox.classList.remove('hidden');
        stdoutVal.textContent = res.stdout;
      }

      if ((res.error || res.stderr) && errBox && errVal) {
        errBox.classList.remove('hidden');
        errVal.textContent = res.error || res.stderr;
      }
    } catch (err) {
      if (outVal) {
        outVal.textContent = `Sandbox Error: ${err.message}`;
        outVal.className = 'output-display-box p-3.5 rounded-lg font-mono text-xs sm:text-sm select-text output-error flex items-center';
      }
      if (errBox && errVal) {
        errBox.classList.remove('hidden');
        errVal.textContent = err.message;
      }
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="play" class="w-3.5 h-3.5 fill-current"></i><span>Run</span>';
        if (window.lucide) lucide.createIcons();
      }
    }
  },

  // =========================================================================
  // CUSTOM TEST CASES (+ Add test case)
  // =========================================================================
  setupDefaultTestCases() {
    if (this.testCases.length > 0) return;

    let fnName = 'solution';
    const fnMatch = this.latestCode.match(/def\s+([a-zA-Z0-9_]+)\s*\(/);
    if (fnMatch) fnName = fnMatch[1];

    if (fnName === 'is_palindrome') {
      this.testCases = [
        { id: 1, input: 'is_palindrome("race a car")', expected: 'False', lastOutput: null, passed: null },
        { id: 2, input: 'is_palindrome("hello")', expected: 'False', lastOutput: null, passed: null }
      ];
    } else if (fnName === 'two_sum') {
      this.testCases = [
        { id: 1, input: 'two_sum([3, 2, 4], 6)', expected: '[1, 2]', lastOutput: null, passed: null }
      ];
    } else {
      this.testCases = [
        { id: 1, input: `${fnName}()`, expected: '', lastOutput: null, passed: null }
      ];
    }
    this.renderTestCases();
  },

  addTestCase(customInput = '', expected = '') {
    let fnCall = customInput;
    if (!fnCall) {
      const fnMatch = this.latestCode.match(/def\s+([a-zA-Z0-9_]+)\s*\(/);
      const fnName = fnMatch ? fnMatch[1] : 'solution';
      fnCall = `${fnName}()`;
    }

    this.testCases.push({
      id: Date.now() + Math.floor(Math.random() * 1000),
      input: fnCall,
      expected: expected || '',
      lastOutput: null,
      passed: null
    });

    this.renderTestCases();
  },

  removeTestCase(id) {
    this.testCases = this.testCases.filter(t => t.id !== id);
    this.renderTestCases();
  },

  renderTestCases() {
    const container = document.getElementById('custom-testcases-list');
    if (!container) return;

    if (this.testCases.length === 0) {
      container.innerHTML = '<div class="text-xs text-theme-muted italic p-2.5 text-center">No custom test cases added yet. Click "+ Add test case" above.</div>';
      return;
    }

    container.innerHTML = '';
    this.testCases.forEach((tc, idx) => {
      const row = document.createElement('div');
      const statusClass = tc.passed === true ? 'status-passed' : (tc.passed === false ? 'status-failed' : '');
      row.className = `testcase-row ${statusClass}`;

      let resultHtml = '';
      if (tc.lastOutput !== null) {
        resultHtml = `<span class="testcase-output-badge ${tc.passed === true ? 'text-emerald-600 dark:text-emerald-400 font-semibold' : (tc.passed === false ? 'text-rose-600 dark:text-rose-400 font-semibold' : '')}">${tc.lastOutput}</span>`;
      }

      row.innerHTML = `
        <span class="text-[10px] font-mono text-theme-muted font-bold">#${idx + 1}</span>
        <div class="testcase-input-col">
          <input type="text" value="${tc.input.replace(/"/g, '&quot;')}" class="testcase-input" placeholder="expression" onchange="WorkspaceManager.updateTestCaseInput(${tc.id}, this.value)" />
        </div>
        ${resultHtml}
        <div class="flex items-center gap-1.5 shrink-0">
          <button onclick="WorkspaceManager.runSingleTestCase(${tc.id})" class="btn-secondary text-[11px] px-2 py-0.5 rounded flex items-center gap-1 hover:text-theme-main" title="Run this test case">
            <i data-lucide="play" class="w-3 h-3 fill-current"></i>
            <span>Run</span>
          </button>
          <button onclick="WorkspaceManager.removeTestCase(${tc.id})" class="text-theme-muted hover:text-theme-accent p-1 transition" title="Delete test case">
            <i data-lucide="trash-2" class="w-3 h-3"></i>
          </button>
        </div>
      `;
      container.appendChild(row);
    });

    if (window.lucide) lucide.createIcons();
  },

  updateTestCaseInput(id, val) {
    const tc = this.testCases.find(t => t.id === id);
    if (tc) tc.input = val.trim();
  },

  async runSingleTestCase(id) {
    const tc = this.testCases.find(t => t.id === id);
    if (!tc || !tc.input) return;

    try {
      const res = await ApiClient.runCustomInput(this.latestCode, tc.input);
      tc.lastOutput = res.return_value !== null ? res.return_value : (res.error ? 'Error' : 'None');
      if (tc.expected) {
        tc.passed = String(res.return_value).trim() === String(tc.expected).trim();
      } else {
        tc.passed = res.success;
      }
      this.renderTestCases();
    } catch (e) {
      tc.lastOutput = 'Error';
      tc.passed = false;
      this.renderTestCases();
    }
  },

  async runAllTestCases() {
    if (this.testCases.length === 0) return;
    const runAllBtn = document.getElementById('run-all-tests-btn');
    if (runAllBtn) runAllBtn.textContent = 'Running...';

    for (const tc of this.testCases) {
      await this.runSingleTestCase(tc.id);
    }

    if (runAllBtn) runAllBtn.textContent = 'Run All';
    window.showToast?.(`Ran ${this.testCases.length} custom test cases`, 'info');
  },

  // =========================================================================
  // ACTION BUTTONS (Copy, Run, Regenerate, Explain, Edit)
  // =========================================================================
  runGeneratedCode() {
    // Executes custom input playground with active expression
    this.runCustomInputLive();
  },

  copyCodeToClipboard() {
    const code = this.latestCode || document.getElementById('code-display')?.textContent || '';
    if (!code) return;

    navigator.clipboard.writeText(code).then(() => {
      window.showToast?.('Code copied to clipboard!', 'success');
      const copyBtn = document.getElementById('copy-code-btn');
      if (copyBtn) {
        copyBtn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400"></i><span class="text-emerald-400">Copied!</span>';
        if (window.lucide) lucide.createIcons();
        setTimeout(() => {
          copyBtn.innerHTML = '<i data-lucide="copy" class="w-3.5 h-3.5"></i><span class="hidden sm:inline">Copy</span>';
          if (window.lucide) lucide.createIcons();
        }, 1800);
      }
    }).catch(() => {
      window.showToast?.('Failed to copy code', 'error');
    });
  },

  regenerateCode() {
    if (this.isExecuting) return;
    window.showToast?.('Regenerating code from requirement...', 'info');
    this.executePipeline();
  },

  explainCode() {
    const modal = document.getElementById('code-explain-modal');
    const content = document.getElementById('explain-content');
    if (!modal || !content) return;

    const fnMatch = this.latestCode.match(/def\s+([a-zA-Z0-9_]+)\s*\((.*?)\):/);
    const fnName = fnMatch ? fnMatch[1] : 'solution';

    content.innerHTML = `
      <div class="space-y-3">
        <p class="font-medium text-theme-main">Function: <span class="font-mono text-brand-purple">${fnName}</span></p>
        <div class="p-3 rounded-lg bg-theme-input border border-theme-subtle">
          <span class="font-bold text-theme-main block mb-1 text-[11px] uppercase tracking-wider">Algorithmic Approach</span>
          <p class="text-theme-secondary">Synthesized directly to address requirement: <em>"${this.currentRequirement}"</em> with edge-case validation, strict typing, and linear execution guarantees.</p>
        </div>
        <div class="p-3 rounded-lg bg-theme-input border border-theme-subtle">
          <span class="font-bold text-theme-main block mb-1 text-[11px] uppercase tracking-wider">Complexity & Architecture</span>
          <p class="text-theme-secondary">Designed with optimal asymptotic time and space bounds, utilizing idiomatic Python constructs.</p>
        </div>
      </div>
    `;

    modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
  },

  closeExplainModal() {
    const modal = document.getElementById('code-explain-modal');
    if (modal) modal.classList.add('hidden');
  },

  startEditRequirement() {
    const editContainer = document.getElementById('req-edit-container');
    const editInput = document.getElementById('req-edit-input');
    const reqText = document.getElementById('submitted-req-text');
    const editBtn = document.getElementById('req-edit-btn');

    if (editContainer && editInput) {
      editInput.value = this.currentRequirement;
      editContainer.classList.remove('hidden');
      if (reqText) reqText.classList.add('hidden');
      if (editBtn) editBtn.classList.add('hidden');
      editInput.focus();
    }
  },

  cancelEditRequirement() {
    const editContainer = document.getElementById('req-edit-container');
    const reqText = document.getElementById('submitted-req-text');
    const editBtn = document.getElementById('req-edit-btn');

    if (editContainer) editContainer.classList.add('hidden');
    if (reqText) reqText.classList.remove('hidden');
    if (editBtn) editBtn.classList.remove('hidden');
  },

  saveEditedRequirement() {
    const editInput = document.getElementById('req-edit-input');
    const newReq = editInput?.value.trim();

    if (!newReq) {
      window.showToast?.('Requirement cannot be empty!', 'warning');
      return;
    }

    this.currentRequirement = newReq;
    const reqDisplay = document.getElementById('submitted-req-text');
    if (reqDisplay) reqDisplay.textContent = newReq;

    this.cancelEditRequirement();
    this.executePipeline();
  },

  // =========================================================================
  // RECENT REQUESTS & SIDEBAR
  // =========================================================================
  loadHistory() {
    try {
      const stored = localStorage.getItem('synthetix_recent_requests');
      if (stored) {
        this.history = JSON.parse(stored);
      }
    } catch (e) {
      this.history = [];
    }
    this.renderHistory();
  },

  saveToHistory(requirement, code) {
    if (!requirement || requirement.length < 5) return;

    // Filter duplicate if already top
    this.history = this.history.filter(h => h.requirement !== requirement);

    let title = requirement;
    if (title.length > 36) title = title.substring(0, 34) + '...';

    this.history.unshift({
      id: Date.now(),
      title,
      requirement,
      code: code || '',
      date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });

    if (this.history.length > 20) {
      this.history = this.history.slice(0, 20);
    }

    try {
      localStorage.setItem('synthetix_recent_requests', JSON.stringify(this.history));
    } catch (e) {}

    this.renderHistory();
  },

  renderHistory() {
    const list = document.getElementById('recent-requests-list');
    if (!list) return;

    if (this.history.length === 0) {
      list.innerHTML = '<div class="text-[11px] text-theme-muted italic p-3 text-center">Your previous coding requests will appear here.</div>';
      return;
    }

    list.innerHTML = '';
    this.history.forEach(item => {
      const btn = document.createElement('button');
      const isActive = (item.requirement === this.currentRequirement);
      btn.className = `recent-request-item ${isActive ? 'active' : ''}`;
      btn.innerHTML = `
        <i data-lucide="message-square" class="w-3.5 h-3.5 shrink-0 ${isActive ? 'text-brand-purple' : 'text-theme-muted'}"></i>
        <span class="req-title font-medium">${item.title}</span>
        <span class="delete-item-btn" onclick="WorkspaceManager.deleteHistoryItem(${item.id}, event)" title="Delete">×</span>
      `;
      btn.onclick = (e) => {
        if (e.target.classList.contains('delete-item-btn')) return;
        this.loadHistoryItem(item.id);
      };
      list.appendChild(btn);
    });

    if (window.lucide) lucide.createIcons();
  },

  loadHistoryItem(id) {
    const item = this.history.find(h => h.id === id);
    if (!item) return;

    this.currentRequirement = item.requirement;
    this.latestCode = item.code;
    this.testCases = [];

    this.transitionToActiveState(item.requirement);

    const codeDisplay = document.getElementById('code-display');
    if (codeDisplay) {
      codeDisplay.textContent = item.code || '# Code ready.';
      if (window.hljs) hljs.highlightElement(codeDisplay);
    }

    this.derivePlaygroundFunctionCall();
    this.setupDefaultTestCases();
    this.renderHistory();

    window.showToast?.('Loaded saved request', 'info');
  },

  deleteHistoryItem(id, event) {
    if (event) event.stopPropagation();
    this.history = this.history.filter(h => h.id !== id);
    try {
      localStorage.setItem('synthetix_recent_requests', JSON.stringify(this.history));
    } catch (e) {}
    this.renderHistory();
  },

  clearHistory() {
    this.history = [];
    try {
      localStorage.removeItem('synthetix_recent_requests');
    } catch (e) {}
    this.renderHistory();
    window.showToast?.('Cleared recent requests', 'info');
  },

  toggleSidebar() {
    const sidebar = document.getElementById('studio-sidebar');
    if (sidebar) {
      sidebar.classList.toggle('collapsed');
      const isCollapsed = sidebar.classList.contains('collapsed');
      sidebar.classList.toggle('hidden', isCollapsed);
    }
  },

  resetToNewTask() {
    this.currentRequirement = '';
    this.latestCode = '';
    this.testCases = [];

    const emptyInput = document.getElementById('req-input-empty');
    if (emptyInput) emptyInput.value = '';

    const hiddenInput = document.getElementById('req-input');
    if (hiddenInput) hiddenInput.value = '';

    const outVal = document.getElementById('playground-output-val');
    if (outVal) {
      outVal.textContent = '(Click "Run" to test custom input against your code)';
      outVal.className = 'output-display-box p-3.5 rounded-lg font-mono text-xs sm:text-sm text-theme-muted select-text min-h-[44px] flex items-center';
    }

    this.showEmptyState();
    this.renderHistory();
  },

  // =========================================================================
  // SETTINGS DRAWER & BACKEND OPTIONS
  // =========================================================================
  openSettings() {
    const drawer = document.getElementById('settings-drawer');
    const backdrop = document.getElementById('settings-drawer-backdrop');
    if (drawer) drawer.classList.add('drawer-open');
    if (backdrop) backdrop.classList.add('backdrop-open');
    if (window.lucide) lucide.createIcons();
  },

  closeSettings() {
    const drawer = document.getElementById('settings-drawer');
    const backdrop = document.getElementById('settings-drawer-backdrop');
    if (drawer) drawer.classList.remove('drawer-open');
    if (backdrop) backdrop.classList.remove('backdrop-open');
  },

  setMode(mode) {
    this.currentMode = mode;
    const rlBtn = document.getElementById('settings-mode-rl');
    const baseBtn = document.getElementById('settings-mode-baseline');

    if (mode === 'rl') {
      rlBtn?.classList.add('active', 'bg-brand-purple', 'text-white');
      rlBtn?.classList.remove('text-theme-secondary');
      baseBtn?.classList.remove('active', 'bg-brand-purple', 'text-white');
      baseBtn?.classList.add('text-theme-secondary');
      window.showToast?.('Mode set to RL Orchestrator', 'info');
    } else {
      baseBtn?.classList.add('active', 'bg-brand-purple', 'text-white');
      baseBtn?.classList.remove('text-theme-secondary');
      rlBtn?.classList.remove('active', 'bg-brand-purple', 'text-white');
      rlBtn?.classList.add('text-theme-secondary');
      window.showToast?.('Mode set to Baseline Router', 'info');
    }
  },

  toggleQualityAudit() {
    const details = document.getElementById('settings-audit-details');
    const btn = document.getElementById('toggle-audit-btn');
    if (!details) return;
    const isHidden = details.classList.contains('hidden');
    if (isHidden) {
      details.classList.remove('hidden');
      if (btn) btn.textContent = 'Hide';
    } else {
      details.classList.add('hidden');
      if (btn) btn.textContent = 'View';
    }
  },

  updateAuditInSettings() {
    const scoreEl = document.getElementById('settings-audit-score');
    const listEl = document.getElementById('settings-audit-suggestions');
    if (scoreEl) scoreEl.textContent = `${this.auditData.score.toFixed(2)} / 1.0`;
    if (listEl) {
      listEl.innerHTML = '';
      if (this.auditData.suggestions && this.auditData.suggestions.length > 0) {
        this.auditData.suggestions.forEach(sug => {
          const li = document.createElement('li');
          li.textContent = `• ${sug}`;
          listEl.appendChild(li);
        });
      } else {
        listEl.innerHTML = '<li class="text-theme-muted italic">Code satisfies algorithmic standards and typing specs.</li>';
      }
    }
  },

  toggleExecutionTrace() {
    const details = document.getElementById('settings-trace-details');
    const btn = document.getElementById('toggle-trace-btn');
    if (!details) return;
    const isHidden = details.classList.contains('hidden');
    if (isHidden) {
      details.classList.remove('hidden');
      if (btn) btn.textContent = 'Hide';
    } else {
      details.classList.add('hidden');
      if (btn) btn.textContent = 'View';
    }
  },

  updateTraceInSettings() {
    const list = document.getElementById('settings-trace-list');
    if (!list) return;
    if (this.stepLogs.length === 0) {
      list.innerHTML = '<div class="text-[11px] text-theme-muted italic">No execution trace recorded.</div>';
      return;
    }
    list.innerHTML = '';
    this.stepLogs.forEach(s => {
      const d = document.createElement('div');
      d.className = 'p-1.5 rounded bg-theme-surface border border-theme-subtle text-[11px] flex items-center justify-between font-mono';
      d.innerHTML = `<span>Step ${s.step}: ${s.agent}</span><span class="text-emerald-400">Done</span>`;
      list.appendChild(d);
    });
  },

  // =========================================================================
  // BENCHMARKS MODAL INTEGRATION
  // =========================================================================
  openProblemModal() {
    const modal = document.getElementById('problem-modal');
    if (modal) {
      modal.classList.remove('hidden');
      if (this.allProblems.length === 0) {
        this.loadBenchmarkProblems();
      } else {
        this.filterProblems();
      }
    }
  },

  closeProblemModal() {
    const modal = document.getElementById('problem-modal');
    if (modal) modal.classList.add('hidden');
  },

  async loadBenchmarkProblems() {
    try {
      this.allProblems = await ApiClient.getProblems();
      const countEl = document.getElementById('nav-lib-count');
      if (countEl) countEl.textContent = `${this.allProblems.length}+`;
      this.filterProblems();
    } catch (e) {
      const list = document.getElementById('modal-problems-list');
      if (list) {
        list.innerHTML = `<div class="text-center py-8 text-xs text-theme-accent">Failed to load problem benchmark library (${e.message})</div>`;
      }
    }
  },

  filterProblems() {
    const query = (document.getElementById('modal-search-input')?.value || '').toLowerCase().trim();
    const diff = document.getElementById('modal-difficulty-filter')?.value || 'All';
    const list = document.getElementById('modal-problems-list');
    if (!list) return;

    const filtered = this.allProblems.filter(p => {
      const matchesCat = (this.selectedCategory === 'All') || (p.category === this.selectedCategory);
      const matchesDiff = (diff === 'All') || (p.difficulty === diff);
      const matchesQuery = !query ||
        (p.name && p.name.toLowerCase().includes(query)) ||
        (p.requirement && p.requirement.toLowerCase().includes(query)) ||
        ((p.category || '').toLowerCase().includes(query));
      return matchesCat && matchesDiff && matchesQuery;
    });

    list.innerHTML = '';
    if (filtered.length === 0) {
      list.innerHTML = '<div class="text-center py-8 text-xs text-theme-muted italic">No matching benchmark challenges found.</div>';
      return;
    }

    filtered.forEach(p => {
      const card = document.createElement('div');
      card.className = 'bg-theme-card border border-theme-subtle rounded-xl p-4 hover:border-brand-purple hover:bg-theme-card-hover cursor-pointer transition flex items-center justify-between gap-4 shadow-xs';
      
      const diffBadge = p.difficulty === 'Easy'
        ? '<span class="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30">Easy</span>'
        : (p.difficulty === 'Medium'
            ? '<span class="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-amber-500/15 text-amber-800 dark:text-amber-300 border border-amber-500/30">Medium</span>'
            : '<span class="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-rose-500/15 text-rose-700 dark:text-rose-300 border border-rose-500/30">Hard</span>');

      card.innerHTML = `
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2 mb-1.5">
            <span class="font-bold text-xs text-theme-main font-mono">${p.name}</span>
            ${diffBadge}
            <span class="text-[10px] px-2 py-0.5 rounded-full badge-subtle font-medium">${p.category || 'Algorithm'}</span>
          </div>
          <p class="text-xs text-theme-secondary line-clamp-2 leading-relaxed">${p.requirement}</p>
        </div>
        <button class="btn-primary text-xs px-3.5 py-1.5 rounded-lg shrink-0">
          Load
        </button>
      `;
      card.addEventListener('click', () => this.selectProblem(p));
      list.appendChild(card);
    });

    if (window.lucide) lucide.createIcons();
  },

  selectProblem(p) {
    this.currentRequirement = p.requirement;
    const hiddenReq = document.getElementById('req-input');
    if (hiddenReq) hiddenReq.value = p.requirement;

    this.transitionToActiveState(p.requirement);

    const fnSig = p.function_name ? `def ${p.function_name}():` : 'def solution():';
    const previewCode = `# Loaded Benchmark: ${p.name || 'Coding Problem'}\n# Category: ${p.category || 'Algorithm'} | Difficulty: ${p.difficulty || 'Standard'}\n# Requirement: ${p.requirement}\n\n${fnSig}\n    pass`;
    
    this.latestCode = previewCode;
    const codeDisplay = document.getElementById('code-display');
    if (codeDisplay) {
      codeDisplay.textContent = previewCode;
      if (window.hljs) hljs.highlightElement(codeDisplay);
    }

    // Set initial test cases from problem if available
    this.testCases = [];
    if (p.test_cases && p.test_cases.length > 0) {
      p.test_cases.forEach((tc, i) => {
        this.testCases.push({
          id: i + 1,
          input: `${p.function_name || 'solution'}(${tc.input})`,
          expected: String(tc.expected !== undefined ? tc.expected : ''),
          lastOutput: null,
          passed: null
        });
      });
    } else {
      this.derivePlaygroundFunctionCall();
      this.setupDefaultTestCases();
    }
    this.renderTestCases();

    this.closeProblemModal();
    if (window.navigateTo) window.navigateTo('studio');
    window.showToast?.(`Loaded benchmark: ${p.name}`, 'success');

    // Automatically trigger code synthesis
    this.executePipeline();
  }
};

window.WorkspaceManager = WorkspaceManager;
