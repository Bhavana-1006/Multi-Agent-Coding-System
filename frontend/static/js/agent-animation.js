/**
 * Synthetix - Multi-Agent Coding System
 * Hero Multi-Agent Collaboration Engine
 * 
 * Simulates real multi-agent orchestration:
 * Phase 1: PlannerAgent deconstructs problem into algorithmic invariants
 * Phase 2: CodingAgent synthesizes typed Python implementation with streaming lines
 * Phase 3: ReviewAgent performs static audit, cyclomatic check & quality scoring
 * Phase 4: TestingAgent executes isolated pytest sandbox assertions
 * Phase 5: Verification banner & test results displayed
 * 
 * Loops seamlessly through realistic programming challenges.
 */

(function () {
  'use strict';

  /* ========================================================================= */
  /* 1. AI SPHERE / ORB RENDERER (Continuous volumetric AI activity)          */
  /* ========================================================================= */
  class AIOrbRenderer {
    constructor(canvasId = 'hero-ai-orb-canvas') {
      this.canvas = document.getElementById(canvasId);
      if (!this.canvas) return;
      this.ctx = this.canvas.getContext('2d');
      this.animationFrameId = null;
      this.isRunning = false;
      this.startTime = performance.now();
      this.currentHue = 195; // Iris/Cyan base
      this.targetHue = 195;
      this.dpr = Math.min(window.devicePixelRatio || 1, 2);
      this.reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      this.agentHues = {
        planner: 190,   // Cyan
        coder: 215,     // Electric Blue
        reviewer: 265,  // Iris / Violet
        tester: 38,     // Warm Amber
        debugger: 160,  // Emerald / Teal
        verified: 155   // Mint / Green
      };

      this.init();
    }

    init() {
      this.resize();
      window.addEventListener('resize', () => this.resize(), { passive: true });
      this.start();
    }

    setAgentTheme(agentKey) {
      if (this.agentHues[agentKey] !== undefined) {
        this.targetHue = this.agentHues[agentKey];
      }
    }

    resize() {
      if (!this.canvas) return;
      const rect = this.canvas.getBoundingClientRect();
      const width = rect.width || 640;
      const height = rect.height || 540;
      this.canvas.width = Math.floor(width * this.dpr);
      this.canvas.height = Math.floor(height * this.dpr);
      this.width = width;
      this.height = height;
    }

    start() {
      if (this.isRunning) return;
      this.isRunning = true;
      this.animate();
    }

    stop() {
      this.isRunning = false;
      if (this.animationFrameId) {
        cancelAnimationFrame(this.animationFrameId);
        this.animationFrameId = null;
      }
    }

    animate() {
      if (!this.isRunning) return;
      this.render();
      this.animationFrameId = requestAnimationFrame(() => this.animate());
    }

    render() {
      const ctx = this.ctx;
      if (!ctx || !this.width || !this.height) return;

      this.currentHue += (this.targetHue - this.currentHue) * 0.04;

      ctx.save();
      ctx.scale(this.dpr, this.dpr);
      ctx.clearRect(0, 0, this.width, this.height);

      const now = performance.now();
      const t = (now - this.startTime) * 0.001;
      const cx = this.width * 0.5;
      const cy = this.height * 0.52;

      const baseR = Math.min(this.width, this.height) * 0.30;
      const pulse = Math.sin(t * 1.5) * 10;
      const r = baseR + pulse;

      // Volumetric Atmosphere Glow
      const outerGlow = ctx.createRadialGradient(cx, cy, r * 0.2, cx, cy, r * 1.7);
      outerGlow.addColorStop(0, `hsla(${this.currentHue}, 90%, 65%, 0.22)`);
      outerGlow.addColorStop(0.35, `hsla(${this.currentHue + 20}, 85%, 55%, 0.12)`);
      outerGlow.addColorStop(0.7, `hsla(260, 75%, 45%, 0.05)`);
      outerGlow.addColorStop(1, 'rgba(5, 5, 5, 0)');
      ctx.fillStyle = outerGlow;
      ctx.beginPath();
      ctx.arc(cx, cy, r * 1.7, 0, Math.PI * 2);
      ctx.fill();

      // Luminous Core Radial Glow
      const coreGlow = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
      coreGlow.addColorStop(0, `hsla(${this.currentHue}, 100%, 94%, 0.65)`);
      coreGlow.addColorStop(0.25, `hsla(${this.currentHue}, 90%, 70%, 0.38)`);
      coreGlow.addColorStop(0.6, `hsla(${this.currentHue + 30}, 80%, 55%, 0.16)`);
      coreGlow.addColorStop(0.92, `hsla(250, 70%, 40%, 0.04)`);
      coreGlow.addColorStop(1, 'rgba(5, 5, 5, 0)');
      ctx.fillStyle = coreGlow;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();

      // Orbital 3D Rings & Nodes
      if (!this.reducedMotion) {
        const ringCount = 3;
        for (let i = 0; i < ringCount; i++) {
          ctx.save();
          ctx.translate(cx, cy);

          const angleOffset = (i * Math.PI) / 3;
          const rotY = t * (0.32 + i * 0.1) + angleOffset;
          const rotZ = Math.sin(t * 0.2 + i) * 0.35 + (i - 1) * 0.35;

          ctx.rotate(rotZ);
          ctx.scale(1, Math.cos(rotY) * 0.55 + 0.15);

          ctx.beginPath();
          ctx.arc(0, 0, r * (0.95 + i * 0.18), 0, Math.PI * 2);
          ctx.strokeStyle = `hsla(${this.currentHue + i * 15}, 85%, 72%, ${0.25 - i * 0.05})`;
          ctx.lineWidth = 1.2;
          ctx.setLineDash([8, 12]);
          ctx.stroke();

          const nodeAngle = t * (1.1 + i * 0.25);
          const nx = Math.cos(nodeAngle) * (r * (0.95 + i * 0.18));
          const ny = Math.sin(nodeAngle) * (r * (0.95 + i * 0.18));
          ctx.beginPath();
          ctx.arc(nx, ny, 2.5, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(${this.currentHue}, 100%, 88%, 0.8)`;
          ctx.shadowColor = `hsl(${this.currentHue}, 100%, 75%)`;
          ctx.shadowBlur = 8;
          ctx.fill();

          ctx.restore();
        }
      }

      ctx.restore();
    }
  }

  /* ========================================================================= */
  /* 2. MULTI-AGENT STUDIO COLLABORATION ENGINE                                */
  /* ========================================================================= */
  class MultiAgentStudioAnimation {
    constructor() {
      this.currentScenarioIndex = 0;
      this.timer = null;
      this.codeTypingInterval = null;
      this.isRunning = false;
      this.orbRenderer = null;

      // Realistic problem scenarios demonstrating full 5-agent lifecycle
      this.scenarios = [
        {
          filename: 'lru_cache.py',
          title: 'LRU Cache with O(1) Eviction',
          plannerMsg: 'Decomposing: Doubly-linked node map + O(1) eviction threshold',
          plannerPlan: [
            '<span class="text-slate-500 font-mono text-xs italic"># [Planner Specification]</span>',
            '<span class="text-cyan-400 font-mono text-xs"># 1. Structure: OrderedDict for O(1) get/put lookups</span>',
            '<span class="text-cyan-400 font-mono text-xs"># 2. Invariant: Most recent moved to end; popitem(last=False)</span>',
            '<span class="text-cyan-400 font-mono text-xs"># 3. Guard: Capacity validation during initialization</span>'
          ],
          coderMsg: 'Synthesizing OrderedDict LRUCache implementation...',
          coderLines: [
            '<span class="tok-kw">from</span> collections <span class="tok-kw">import</span> OrderedDict',
            '',
            '<span class="tok-kw">class</span> <span class="tok-cls">LRUCache</span>:',
            '    <span class="tok-kw">def</span> <span class="tok-fn">__init__</span>(self, capacity: <span class="tok-type">int</span>):',
            '        self.cache = OrderedDict()',
            '        self.capacity = capacity',
            '',
            '    <span class="tok-kw">def</span> <span class="tok-fn">get</span>(self, key: <span class="tok-type">int</span>) -> <span class="tok-type">int</span>:',
            '        <span class="tok-kw">if</span> key <span class="tok-kw">not in</span> self.cache: <span class="tok-kw">return</span> -<span class="tok-num">1</span>',
            '        self.cache.move_to_end(key)',
            '        <span class="tok-kw">return</span> self.cache[key]',
            '',
            '    <span class="tok-kw">def</span> <span class="tok-fn">put</span>(self, key: <span class="tok-type">int</span>, val: <span class="tok-type">int</span>) -> <span class="tok-type">None</span>:',
            '        <span class="tok-kw">if</span> key <span class="tok-kw">in</span> self.cache: self.cache.move_to_end(key)',
            '        self.cache[key] = val',
            '        <span class="tok-kw">if</span> len(self.cache) > self.capacity:',
            '            self.cache.popitem(last=<span class="tok-kw">False</span>)'
          ],
          reviewerMsg: 'Quality Score 9.8/10 • Complexity O(1) • Zero memory leak vulnerabilities',
          testerMsg: 'Pytest Sandbox: 4/5 assertions passed, boundary check (capacity <= 0) flagged',
          debuggerMsg: 'Self-Repair: Added capacity validation guard & verified edge case',
          debuggerPatch: [
            '        <span class="text-emerald-400 font-mono text-xs"># [Debugger Patch Applied]</span>',
            '        <span class="tok-kw">if</span> capacity <= <span class="tok-num">0</span>: <span class="tok-kw">raise</span> <span class="tok-cls">ValueError</span>(<span class="tok-str">"Capacity must be positive"</span>)'
          ],
          verifiedMsg: 'Pytest Sandbox: 5/5 test assertions PASSED (0.012s) in isolated sandbox'
        },
        {
          filename: 'rate_limiter.py',
          title: 'Token Bucket Rate Limiter',
          plannerMsg: 'Decomposing: High-throughput token bucket with monotonic refill guard',
          plannerPlan: [
            '<span class="text-slate-500 font-mono text-xs italic"># [Planner Specification]</span>',
            '<span class="text-cyan-400 font-mono text-xs"># 1. State: Tokens counter capped at burst capacity</span>',
            '<span class="text-cyan-400 font-mono text-xs"># 2. Timing: Monotonic delta elapsed calculation</span>',
            '<span class="text-cyan-400 font-mono text-xs"># 3. Thread-safety: Atomic deduction on allow_request</span>'
          ],
          coderMsg: 'Synthesizing thread-safe TokenBucket implementation...',
          coderLines: [
            '<span class="tok-kw">import</span> time',
            '',
            '<span class="tok-kw">class</span> <span class="tok-cls">TokenBucket</span>:',
            '    <span class="tok-kw">def</span> <span class="tok-fn">__init__</span>(self, capacity: <span class="tok-type">int</span>, refill_rate: <span class="tok-type">float</span>):',
            '        self.capacity = capacity',
            '        self.tokens = float(capacity)',
            '        self.refill_rate = refill_rate',
            '        self.last_ts = time.monotonic()',
            '',
            '    <span class="tok-kw">def</span> <span class="tok-fn">allow_request</span>(self, tokens: <span class="tok-type">int</span> = <span class="tok-num">1</span>) -> <span class="tok-type">bool</span>:',
            '        now = time.monotonic()',
            '        delta = now - self.last_ts',
            '        self.tokens = min(self.capacity, self.tokens + delta * self.refill_rate)',
            '        self.last_ts = now',
            '        <span class="tok-kw">if</span> self.tokens >= tokens:',
            '            self.tokens -= tokens',
            '            <span class="tok-kw">return True</span>',
            '        <span class="tok-kw">return False</span>'
          ],
          reviewerMsg: 'Quality Score 9.9/10 • Monotonic clock audited • PEP 8 compliant',
          testerMsg: 'Pytest Sandbox: 3/4 concurrency assertions passed, burst overflow edge-case caught',
          debuggerMsg: 'Self-Repair: Clamped negative delta guard & synchronized token deduction',
          debuggerPatch: [
            '        <span class="text-emerald-400 font-mono text-xs"># [Debugger Patch Applied]</span>',
            '        delta = max(<span class="tok-num">0.0</span>, now - self.last_ts)  <span class="text-slate-500 font-mono text-xs"># Guard system time rollback</span>'
          ],
          verifiedMsg: 'Pytest Sandbox: 4/4 concurrency assertions PASSED (0.009s) in sandbox'
        },
        {
          filename: 'two_sum_hash.py',
          title: 'Optimal Two-Sum Hash Lookup',
          plannerMsg: 'Decomposing: Single-pass complement lookup with invariant hash map',
          plannerPlan: [
            '<span class="text-slate-500 font-mono text-xs italic"># [Planner Specification]</span>',
            '<span class="text-cyan-400 font-mono text-xs"># 1. Complexity: Strict O(n) time, O(n) memory bound</span>',
            '<span class="text-cyan-400 font-mono text-xs"># 2. Logic: Complement calculation (target - val) before insert</span>',
            '<span class="text-cyan-400 font-mono text-xs"># 3. Collision: Guard against duplicate element reuse</span>'
          ],
          coderMsg: 'Synthesizing two_sum with strict O(n) guarantees...',
          coderLines: [
            '<span class="tok-kw">def</span> <span class="tok-fn">two_sum</span>(nums: list[<span class="tok-type">int</span>], target: <span class="tok-type">int</span>) -> list[<span class="tok-type">int</span>]:',
            '    <span class="tok-str">"""Finds indices of pair summing to target in O(n)."""</span>',
            '    seen = {}',
            '    <span class="tok-kw">for</span> i, val <span class="tok-kw">in</span> enumerate(nums):',
            '        complement = target - val',
            '        <span class="tok-kw">if</span> complement <span class="tok-kw">in</span> seen:',
            '            <span class="tok-kw">return</span> [seen[complement], i]',
            '        seen[val] = i',
            '    <span class="tok-kw">return</span> []'
          ],
          reviewerMsg: 'Quality Score 10/10 • Algorithmic bounds verified • Edge cases checked',
          testerMsg: 'Pytest Sandbox: 5/6 assertions passed, empty list input validation flagged',
          debuggerMsg: 'Self-Repair: Added early exit length guard for len(nums) < 2',
          debuggerPatch: [
            '    <span class="text-emerald-400 font-mono text-xs"># [Debugger Patch Applied]</span>',
            '    <span class="tok-kw">if not</span> nums <span class="tok-kw">or</span> len(nums) < <span class="tok-num">2</span>: <span class="tok-kw">return</span> []'
          ],
          verifiedMsg: 'Pytest Sandbox: 6/6 edge cases PASSED (0.004s) in sandbox'
        }
      ];

      this.init();
    }

    init() {
      this.cacheDOMElements();
      this.orbRenderer = new AIOrbRenderer('hero-ai-orb-canvas');
      if (!this.container) return;
      this.start();
    }

    cacheDOMElements() {
      this.container = document.getElementById('hero-agent-stage');
      this.filenameEl = document.getElementById('stage-filename');
      this.codeBodyEl = document.getElementById('stage-code-body');
      this.lineNumsEl = document.getElementById('stage-line-nums');
      this.statusLogEl = document.getElementById('stage-status-log');
      this.statusPillEl = document.getElementById('stage-status-pill');

      // 5 Agent Matrix Nodes
      this.agentNodes = {
        planner: document.getElementById('agent-node-planner'),
        coder: document.getElementById('agent-node-coder'),
        reviewer: document.getElementById('agent-node-reviewer'),
        tester: document.getElementById('agent-node-tester'),
        debugger: document.getElementById('agent-node-debugger')
      };

      // Glowing conduits connecting adjacent agents
      this.conduits = {
        1: document.getElementById('conduit-1'), // Planner -> Coder
        2: document.getElementById('conduit-2'), // Coder -> Reviewer
        3: document.getElementById('conduit-3'), // Reviewer -> Tester
        4: document.getElementById('conduit-4')  // Tester -> Debugger
      };

      // Explanatory Sidebar Steps
      this.stepCards = {
        planner: document.getElementById('step-planner'),
        coder: document.getElementById('step-coder'),
        reviewer: document.getElementById('step-reviewer'),
        tester: document.getElementById('step-tester'),
        debugger: document.getElementById('step-debugger')
      };
    }

    setWorkflowState(activeKey, activeConduit = null) {
      // 1. Update Agent Matrix Nodes
      Object.keys(this.agentNodes).forEach(key => {
        const el = this.agentNodes[key];
        if (!el) return;
        if (key === activeKey) {
          el.classList.add('agent-active');
          el.classList.remove('agent-idle', 'opacity-50');
        } else {
          el.classList.remove('agent-active');
          el.classList.add('agent-idle', 'opacity-50');
        }
      });

      // 2. Update Conduit Glows
      Object.keys(this.conduits).forEach(idx => {
        const c = this.conduits[idx];
        if (!c) return;
        if (activeConduit === 'all' || Number(idx) === activeConduit) {
          c.classList.add('conduit-active');
        } else {
          c.classList.remove('conduit-active');
        }
      });

      // 3. Update Explanatory Sidebar Step Cards
      Object.keys(this.stepCards).forEach(key => {
        const sc = this.stepCards[key];
        if (!sc) return;
        if (key === activeKey) {
          sc.classList.add('workflow-step-active');
        } else {
          sc.classList.remove('workflow-step-active');
        }
      });

      // 4. Update AI Sphere Hue
      if (this.orbRenderer) {
        this.orbRenderer.setAgentTheme(activeKey);
      }
    }

    start() {
      if (this.isRunning) return;
      this.isRunning = true;
      if (this.orbRenderer) this.orbRenderer.start();
      this.runPhasePlan();
    }

    stop() {
      this.isRunning = false;
      if (this.timer) clearTimeout(this.timer);
      if (this.codeTypingInterval) clearInterval(this.codeTypingInterval);
      if (this.orbRenderer) this.orbRenderer.stop();
    }

    // Step 1: Planner Agent Formulates Architecture
    runPhasePlan() {
      if (!this.isRunning) return;
      const scenario = this.scenarios[this.currentScenarioIndex];

      if (this.filenameEl) this.filenameEl.textContent = scenario.filename;
      this.setWorkflowState('planner', null);

      if (this.statusLogEl) {
        this.statusLogEl.innerHTML = `
          <span class="text-cyan-400 font-bold">[Planner]</span>
          <span class="text-slate-300 ml-1.5">${scenario.plannerMsg}</span>
        `;
      }

      if (this.statusPillEl) {
        this.statusPillEl.className = 'agent-pill-badge bg-cyan-500/10 text-cyan-400 border border-cyan-500/30';
        this.statusPillEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span><span>Planning Architecture</span>`;
      }

      // Display Planner Blueprint in Code Editor
      if (this.codeBodyEl) {
        this.codeBodyEl.innerHTML = scenario.plannerPlan.map(p => `<div class="editor-line flex items-center">${p}</div>`).join('');
      }
      if (this.lineNumsEl) {
        this.lineNumsEl.innerHTML = scenario.plannerPlan.map((_, i) => `<div>${i + 1}</div>`).join('');
      }

      this.timer = setTimeout(() => {
        this.runPhaseCode();
      }, 2400);
    }

    // Step 2: Coder Agent Streams Implementation
    runPhaseCode() {
      if (!this.isRunning) return;
      const scenario = this.scenarios[this.currentScenarioIndex];
      this.setWorkflowState('coder', 1);

      if (this.statusLogEl) {
        this.statusLogEl.innerHTML = `
          <span class="text-blue-400 font-bold">[Coder]</span>
          <span class="text-slate-300 ml-1.5">${scenario.coderMsg}</span>
        `;
      }

      if (this.statusPillEl) {
        this.statusPillEl.className = 'agent-pill-badge bg-blue-500/10 text-blue-400 border border-blue-500/30';
        this.statusPillEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span><span>Synthesizing Code</span>`;
      }

      const totalLines = scenario.coderLines.length;
      let currentLine = 0;

      if (this.codeBodyEl) this.codeBodyEl.innerHTML = '';
      if (this.lineNumsEl) this.lineNumsEl.innerHTML = '';

      if (this.codeTypingInterval) clearInterval(this.codeTypingInterval);

      this.codeTypingInterval = setInterval(() => {
        if (!this.isRunning) return;
        currentLine++;

        if (this.lineNumsEl) {
          const numDiv = document.createElement('div');
          numDiv.textContent = currentLine;
          this.lineNumsEl.appendChild(numDiv);
        }

        if (this.codeBodyEl) {
          const lineContent = scenario.coderLines[currentLine - 1] || '&nbsp;';
          const lineDiv = document.createElement('div');
          lineDiv.className = 'editor-line flex items-center';
          lineDiv.innerHTML = lineContent || '&nbsp;';
          this.codeBodyEl.appendChild(lineDiv);

          this.codeBodyEl.scrollTop = this.codeBodyEl.scrollHeight;
        }

        if (currentLine >= totalLines) {
          clearInterval(this.codeTypingInterval);
          this.timer = setTimeout(() => {
            this.runPhaseReview();
          }, 1300);
        }
      }, 105);
    }

    // Step 3: Review Agent Analyzes Quality
    runPhaseReview() {
      if (!this.isRunning) return;
      const scenario = this.scenarios[this.currentScenarioIndex];
      this.setWorkflowState('reviewer', 2);

      if (this.statusLogEl) {
        this.statusLogEl.innerHTML = `
          <span class="text-violet-400 font-bold">[Reviewer]</span>
          <span class="text-slate-300 ml-1.5">${scenario.reviewerMsg}</span>
        `;
      }

      if (this.statusPillEl) {
        this.statusPillEl.className = 'agent-pill-badge bg-violet-500/10 text-violet-400 border border-violet-500/30';
        this.statusPillEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-violet-400 animate-pulse"></span><span>Quality & Audit Review</span>`;
      }

      this.timer = setTimeout(() => {
        this.runPhaseTest();
      }, 2100);
    }

    // Step 4: Testing Agent Runs Sandboxed Assertions
    runPhaseTest() {
      if (!this.isRunning) return;
      const scenario = this.scenarios[this.currentScenarioIndex];
      this.setWorkflowState('tester', 3);

      if (this.statusLogEl) {
        this.statusLogEl.innerHTML = `
          <span class="text-amber-400 font-bold">[Tester]</span>
          <span class="text-slate-300 ml-1.5">${scenario.testerMsg}</span>
        `;
      }

      if (this.statusPillEl) {
        this.statusPillEl.className = 'agent-pill-badge bg-amber-500/10 text-amber-400 border border-amber-500/30';
        this.statusPillEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-400 animate-spin"></span><span>Running Sandbox Pytest</span>`;
      }

      this.timer = setTimeout(() => {
        this.runPhaseDebug();
      }, 2000);
    }

    // Step 5: Debugger Agent Applies Self-Repair Patch
    runPhaseDebug() {
      if (!this.isRunning) return;
      const scenario = this.scenarios[this.currentScenarioIndex];
      this.setWorkflowState('debugger', 4);

      if (this.statusLogEl) {
        this.statusLogEl.innerHTML = `
          <span class="text-emerald-400 font-bold">[Debugger]</span>
          <span class="text-slate-300 ml-1.5">${scenario.debuggerMsg}</span>
        `;
      }

      if (this.statusPillEl) {
        this.statusPillEl.className = 'agent-pill-badge bg-emerald-500/15 text-emerald-400 border border-emerald-500/40';
        this.statusPillEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span><span>Self-Repair Active</span>`;
      }

      // Append self-repair patch to code editor
      if (this.codeBodyEl && scenario.debuggerPatch) {
        scenario.debuggerPatch.forEach(line => {
          const lineDiv = document.createElement('div');
          lineDiv.className = 'editor-line flex items-center bg-emerald-500/10 -mx-4 px-4 py-0.5 border-l-2 border-emerald-400';
          lineDiv.innerHTML = line;
          this.codeBodyEl.appendChild(lineDiv);
        });
        if (this.lineNumsEl) {
          const currentCount = this.lineNumsEl.children.length;
          scenario.debuggerPatch.forEach((_, i) => {
            const numDiv = document.createElement('div');
            numDiv.textContent = currentCount + i + 1;
            this.lineNumsEl.appendChild(numDiv);
          });
        }
        this.codeBodyEl.scrollTop = this.codeBodyEl.scrollHeight;
      }

      this.timer = setTimeout(() => {
        this.runPhaseVerified();
      }, 2200);
    }

    // Step 6: Verified & All Tests Passing in Sandbox
    runPhaseVerified() {
      if (!this.isRunning) return;
      const scenario = this.scenarios[this.currentScenarioIndex];
      this.setWorkflowState('debugger', 'all');

      if (this.statusLogEl) {
        this.statusLogEl.innerHTML = `
          <span class="text-emerald-400 font-bold">[Sandbox Result]</span>
          <span class="text-emerald-300 ml-1.5 font-semibold">${scenario.verifiedMsg}</span>
        `;
      }

      if (this.statusPillEl) {
        this.statusPillEl.className = 'agent-pill-badge bg-emerald-500/15 text-emerald-400 border border-emerald-500/40 shadow-xs shadow-emerald-500/20';
        this.statusPillEl.innerHTML = `
          <svg class="w-3.5 h-3.5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          <span class="font-bold">Verified & Passing</span>
        `;
      }

      // Next scenario loop after 3.8s pause
      this.timer = setTimeout(() => {
        this.currentScenarioIndex = (this.currentScenarioIndex + 1) % this.scenarios.length;
        this.runPhasePlan();
      }, 3800);
    }
  }

  window.MultiAgentStudioAnimation = MultiAgentStudioAnimation;
})();
