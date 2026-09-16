/**
 * Synthetix - Multi-Agent Coding System
 * Landing Page Interactive & Animation Logic
 * 
 * Features:
 * - WebGL Shader background orchestration (Reference Image 2 inspired)
 * - Multi-Agent Collaboration Engine loop (Reference Image 1 & 2 inspired)
 * - Interactive Demo section presets (Requirement <-> Code)
 * - Direct one-click transfer of prompt/code to Studio Workspace
 * - Scroll-triggered entrance reveals
 */

const LandingManager = {
  // Preset demo problems with requirement & generated verified code
  demos: {
    students: {
      name: "Top 3 Students",
      requirement: "Create a Python function that returns the top 3 students based on their marks, breaking ties by name.",
      code: `def top_students(students: list[dict]) -> list[dict]:
    """
    Returns the top 3 student records sorted by marks descending.
    Ties broken alphabetically by student name.
    """
    if not students:
        return []
    
    return sorted(
        students,
        key=lambda s: (-s.get("marks", 0), s.get("name", ""))
    )[:3]`,
      testAssertion: "assert top_students([{'name':'A', 'marks':90}, {'name':'B', 'marks':95}]) == [{'name':'B', 'marks':95}, {'name':'A', 'marks':90}]"
    },
    palindrome: {
      name: "Strict Palindrome",
      requirement: "Write a python function is_palindrome(s: str) -> bool that checks if a string is a palindrome, ignoring casing and non-alphanumeric characters.",
      code: `def is_palindrome(s: str) -> bool:
    """
    Validates if string is a palindrome, ignoring casing and non-alphanumeric characters.
    """
    cleaned = [c.lower() for c in s if c.isalnum()]
    return cleaned == cleaned[::-1]`,
      testAssertion: "assert is_palindrome('A man, a plan, a canal: Panama') == True"
    },
    twosum: {
      name: "Two Sum",
      requirement: "Write a function two_sum(nums: list[int], target: int) -> list[int] that finds indices of two numbers that add up to target in O(n) hash map time.",
      code: `def two_sum(nums: list[int], target: int) -> list[int]:
    """
    Finds pair indices summing to target in O(n) hash map time complexity.
    """
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []`,
      testAssertion: "assert two_sum([2, 7, 11, 15], 9) == [0, 1]"
    },
    ratelimiter: {
      name: "Rate Limiter",
      requirement: "Create a TokenBucket rate limiter class with capacity and refill_rate that allows requests when tokens are available.",
      code: `import time

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def allow_request(self, tokens: int = 1) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False`,
      testAssertion: "tb = TokenBucket(10, 1.0); assert tb.allow_request(5) == True"
    }
  },

  activeDemoKey: 'students',
  shaderInstance: null,
  agentAnimationInstance: null,

  init() {
    this.setupDemoPresets();
    this.setupScrollObserver();
    this.initHeroShader();
    this.initAgentAnimation();
  },

  initHeroShader() {
    if (window.HeroShaderBackground) {
      try {
        this.shaderInstance = new window.HeroShaderBackground('hero-shader-canvas');
      } catch (err) {
        console.warn('Shader background initialization warning:', err);
      }
    }
  },

  initAgentAnimation() {
    if (window.MultiAgentStudioAnimation) {
      try {
        this.agentAnimationInstance = new window.MultiAgentStudioAnimation();
      } catch (err) {
        console.warn('Agent animation initialization warning:', err);
      }
    }
  },

  onViewChange(view) {
    const isStudio = (view === 'studio');
    if (this.shaderInstance) {
      this.shaderInstance.setStudioMode(isStudio);
    }
    if (this.agentAnimationInstance) {
      if (isStudio) {
        this.agentAnimationInstance.stop();
      } else {
        this.agentAnimationInstance.start();
      }
    }
  },

  setupDemoPresets() {
    const buttons = document.querySelectorAll('[data-demo-key]');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const key = btn.getAttribute('data-demo-key');
        this.selectDemo(key);
      });
    });
  },

  selectDemo(key) {
    if (!this.demos[key]) return;
    this.activeDemoKey = key;
    const demo = this.demos[key];

    // Update active button state
    document.querySelectorAll('[data-demo-key]').forEach(btn => {
      if (btn.getAttribute('data-demo-key') === key) {
        btn.className = 'preset-chip text-xs font-bold bg-white text-[#080808] border border-white rounded-full px-4 py-1.5 shadow-md transition transform -translate-y-0.5';
      } else {
        btn.className = 'preset-chip text-xs font-semibold bg-white/5 text-slate-300 hover:text-white border border-white/10 hover:border-white/30 rounded-full px-4 py-1.5 transition';
      }
    });

    // Update left panel requirement with smooth fade
    const reqTextEl = document.getElementById('demo-requirement-text');
    if (reqTextEl) {
      reqTextEl.value = demo.requirement;
      reqTextEl.classList.add('code-fade-in');
      setTimeout(() => reqTextEl.classList.remove('code-fade-in'), 350);
    }

    // Update right panel code block with syntax highlight and fade
    const codeEl = document.getElementById('demo-code-block');
    if (codeEl) {
      codeEl.textContent = demo.code;
      if (window.hljs) hljs.highlightElement(codeEl);
      codeEl.parentElement.classList.add('code-fade-in');
      setTimeout(() => codeEl.parentElement.classList.remove('code-fade-in'), 350);
    }
  },

  launchDemoInStudio() {
    const demo = this.demos[this.activeDemoKey];
    const reqTextEl = document.getElementById('demo-requirement-text');
    const requirement = reqTextEl ? reqTextEl.value.trim() : (demo ? demo.requirement : '');

    const workspaceInput = document.getElementById('req-input');
    if (workspaceInput) {
      workspaceInput.value = requirement;
    }

    const testInput = document.getElementById('custom-tests-input');
    if (testInput && demo?.testAssertion) {
      testInput.value = demo.testAssertion;
    }

    const codeDisplay = document.getElementById('code-display');
    if (codeDisplay && demo) {
      codeDisplay.textContent = demo.code;
      if (window.hljs) hljs.highlightElement(codeDisplay);
    }

    if (window.WorkspaceManager) {
      window.WorkspaceManager.currentRequirement = requirement;
      window.WorkspaceManager.latestCode = demo?.code || '';
      window.WorkspaceManager.transitionToActiveState(requirement);
      window.WorkspaceManager.derivePlaygroundFunctionCall();
      window.WorkspaceManager.setupDefaultTestCases();
      window.WorkspaceManager.saveToHistory(requirement, demo?.code || '');
    }

    if (window.navigateTo) {
      window.navigateTo('studio');
      window.showToast?.(`Loaded ${demo?.name || 'problem'} in Studio Workspace!`, 'info');
    }
  },

  // Scroll Reveal Animations via IntersectionObserver
  setupScrollObserver() {
    const elements = document.querySelectorAll('.reveal-on-scroll');
    if (!elements.length) return;

    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-revealed');
            observer.unobserve(entry.target);
          }
        });
      }, {
        threshold: 0.12,
        rootMargin: '0px 0px -40px 0px'
      });

      elements.forEach(el => observer.observe(el));
    } else {
      elements.forEach(el => el.classList.add('is-revealed'));
    }
  }
};

window.LandingManager = LandingManager;
