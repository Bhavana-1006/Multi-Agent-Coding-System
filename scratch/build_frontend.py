import os

html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light dark">
  <title>Multi-Agent Coding System with RL Orchestrator</title>
  
  <!-- Early Theme Initialization to prevent Flash of Unstyled Content -->
  <script>
    (function() {
      const savedTheme = localStorage.getItem('theme');
      if (savedTheme === 'dark' || (!savedTheme && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    })();
  </script>

  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,400&family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  
  <!-- Lucide Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>
  
  <!-- Highlight.js for Syntax Highlighting -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/base16/gruvbox-dark-medium.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
  
  <!-- Canvas Confetti -->
  <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>

  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            serif: ['"Cormorant Garamond"', 'Georgia', 'serif'],
            sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'Consolas', 'monospace']
          },
          colors: {
            sageBg: '#F4F6F1',
            sageCard: '#FFFFFF',
            sageSurface: '#E8EFE5',
            sageBorder: '#C9D6C4',
            sageBorderDark: '#A3B49E',
            sageLight: '#9CB096',
            olive: '#4A5D44',
            oliveDark: '#354331',
            oliveDeep: '#232D20',
            mossText: '#2C3828',
            sandAccent: '#D8C7B5',
            clayAccent: '#B28266',
            darkBg: '#080C14',
            darkCard: '#101622',
            darkSurface: '#182133',
            darkBorder: '#26334D',
            darkBorderGlow: '#10B981'
          }
        }
      }
    };
  </script>

  <style>
    :root {
      --bg-gradient: radial-gradient(circle at top, #F7F9F5 0%, #EBF0E7 60%, #DFE7DB 100%);
      --panel-bg: rgba(255, 255, 255, 0.94);
      --panel-border: #C9D6C4;
      --panel-shadow: 0 4px 20px -2px rgba(44, 56, 40, 0.06);
      --text-main: #2C3828;
      --text-sub: #4A5D44;
      --surface: #E8EFE5;
      --accent: #4A5D44;
      --accent-hover: #354331;
    }

    html.dark {
      --bg-gradient: radial-gradient(circle at 20% 10%, rgba(16, 185, 129, 0.08) 0%, transparent 40%), radial-gradient(circle at 80% 20%, rgba(6, 182, 212, 0.08) 0%, transparent 40%), radial-gradient(circle at 50% 100%, #030712 0%, #080C14 60%, #05080E 100%);
      --panel-bg: rgba(16, 22, 34, 0.82);
      --panel-border: rgba(55, 65, 81, 0.6);
      --panel-shadow: 0 10px 35px 0 rgba(0, 0, 0, 0.55);
      --text-main: #F3F4F6;
      --text-sub: #9CA3AF;
      --surface: rgba(24, 33, 51, 0.85);
      --accent: #10B981;
      --accent-hover: #059669;
    }

    body {
      background: var(--bg-gradient);
      color: var(--text-main);
      min-height: 100vh;
      transition: background 0.3s ease, color 0.3s ease;
    }

    .editorial-panel {
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      box-shadow: var(--panel-shadow);
      transition: all 0.25s ease;
    }

    .editorial-panel-sage {
      background: var(--surface);
      border: 1px solid var(--panel-border);
    }

    .agent-node {
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .agent-running {
      box-shadow: 0 0 25px rgba(16, 185, 129, 0.5) !important;
      border-color: #10B981 !important;
      transform: scale(1.03);
      animation: pulse-glow 1.5s infinite alternate;
    }

    .agent-done {
      border-color: #10B981 !important;
      background: rgba(16, 185, 129, 0.09) !important;
    }

    @keyframes pulse-glow {
      0% { box-shadow: 0 0 12px rgba(16, 185, 129, 0.3); }
      100% { box-shadow: 0 0 30px rgba(16, 185, 129, 0.8); }
    }

    .custom-scrollbar::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
      background: transparent;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
      background: #9CB096;
      border-radius: 4px;
    }
    html.dark .custom-scrollbar::-webkit-scrollbar-thumb {
      background: #4B5563;
    }

    .btn-action {
      background: var(--accent);
      color: #FFFFFF;
      transition: all 0.2s ease;
    }
    .btn-action:hover {
      background: var(--accent-hover);
    }

    /* Ambient Lighting effect */
    .ambient-glow {
      position: absolute;
      top: -120px;
      left: 50%;
      transform: translateX(-50%);
      width: 650px;
      height: 380px;
      background: radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, rgba(6, 182, 212, 0.08) 40%, transparent 70%);
      filter: blur(50px);
      pointer-events: none;
      z-index: 0;
    }

    /* View transition styles */
    ::view-transition-old(root),
    ::view-transition-new(root) {
      animation-duration: 0.25s;
      animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    }

    @media (prefers-reduced-motion: reduce) {
      ::view-transition-group(*),
      ::view-transition-old(*),
      ::view-transition-new(*) {
        animation: none !important;
      }
    }
  </style>
</head>
<body class="font-sans antialiased custom-scrollbar selection:bg-emerald-600 selection:text-white relative overflow-x-hidden">

  <!-- Ambient Glow effect in background -->
  <div class="ambient-glow"></div>

  <!-- Top Announcement Bar -->
  <div class="bg-oliveDark dark:bg-black/90 text-sageBg dark:text-emerald-400 text-[11px] uppercase tracking-[0.2em] font-medium py-1.5 text-center border-b border-olive/30 dark:border-emerald-500/20 flex items-center justify-center gap-2 relative z-10">
    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
    <span>Autonomous Multi-Agent Development • PPO Reinforcement Learning Orchestration</span>
  </div>

  <!-- Global Header Navigation -->
  <header class="border-b border-sageBorder dark:border-gray-800/80 editorial-panel sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-6 py-3.5 flex items-center justify-between">
      
      <!-- Brand Logo / Title -->
      <div class="flex items-center gap-3 cursor-pointer" onclick="navigateTo('landing')">
        <div class="h-10 w-10 rounded-xl bg-olive dark:bg-emerald-600 flex items-center justify-center shadow-md text-white transition transform hover:scale-105">
          <i data-lucide="compass" class="w-5 h-5"></i>
        </div>
        <div>
          <h1 class="font-serif text-2xl font-bold text-oliveDark dark:text-white tracking-wide leading-none">
            Multi-Agent System
          </h1>
          <p class="text-[10px] uppercase tracking-[0.2em] text-olive/80 dark:text-emerald-400 font-semibold mt-1">Adaptive RL Code Synthesizer</p>
        </div>
      </div>

      <!-- Navigation Links -->
      <nav class="hidden md:flex items-center gap-1.5 text-xs font-semibold">
        <button onclick="navigateTo('landing')" id="nav-btn-landing" class="px-3.5 py-1.5 rounded-full transition text-oliveDark dark:text-white bg-sageSurface dark:bg-gray-800 shadow-sm border border-sageBorder dark:border-gray-700">
          Overview
        </button>
        <button onclick="navigateTo('studio')" id="nav-btn-studio" class="px-3.5 py-1.5 rounded-full transition text-olive/70 dark:text-gray-400 hover:text-oliveDark dark:hover:text-white">
          Studio Workspace
        </button>
        <button onclick="openProblemModal()" class="px-3.5 py-1.5 rounded-full transition text-olive/70 dark:text-gray-400 hover:text-oliveDark dark:hover:text-white flex items-center gap-1.5">
          <span>Benchmark Library</span>
          <span id="nav-lib-count" class="text-[10px] px-1.5 py-0.2 rounded-full bg-olive/10 dark:bg-emerald-500/20 text-olive dark:text-emerald-400 font-mono">40+</span>
        </button>
        <button onclick="scrollToArchitecture()" class="px-3.5 py-1.5 rounded-full transition text-olive/70 dark:text-gray-400 hover:text-oliveDark dark:hover:text-white">
          Architecture
        </button>
      </nav>

      <!-- Right Actions (Badges, Theme, CTA) -->
      <div class="flex items-center gap-2.5">
        <!-- LLM Backend Badge -->
        <span id="backend-provider-badge" class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-sageSurface dark:bg-gray-800 text-oliveDark dark:text-gray-200 border border-sageBorder dark:border-gray-700 shadow-sm">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span id="backend-provider-name">Groq Cloud</span>
        </span>

        <!-- Theme Toggle -->
        <button id="theme-toggle-btn" onclick="toggleTheme()" class="p-2 rounded-xl bg-white dark:bg-gray-800 border border-sageBorder dark:border-gray-700 text-oliveDark dark:text-gray-200 hover:bg-sageSurface dark:hover:bg-gray-700 transition shadow-sm" title="Toggle Theme">
          <i id="theme-icon" data-lucide="moon" class="w-4 h-4"></i>
        </button>

        <!-- Header Launch CTA -->
        <button onclick="navigateTo('studio')" id="header-cta-btn" class="btn-action px-3.5 py-1.5 rounded-xl text-xs font-bold uppercase tracking-wider shadow-sm flex items-center gap-1.5 active:scale-95">
          <span>Studio</span>
          <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
        </button>
      </div>

    </div>
  </header>

  <!-- ========================================================================= -->
  <!-- VIEW 1: LANDING PAGE -->
  <!-- ========================================================================= -->
  <div id="view-landing" class="transition-opacity duration-300 relative z-10">
    
    <!-- Hero Section -->
    <section class="max-w-6xl mx-auto px-6 pt-16 pb-20 text-center space-y-6">
      
      <!-- Eyebrow Pill -->
      <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold bg-sageSurface dark:bg-emerald-950/40 text-oliveDark dark:text-emerald-400 border border-sageBorder dark:border-emerald-800/60 shadow-sm animate-in fade-in slide-in-from-top duration-500">
        <i data-lucide="sparkles" class="w-3.5 h-3.5 text-emerald-500"></i>
        <span>PPO Reinforcement Learning • Autonomous Multi-Agent Coordination</span>
      </div>

      <!-- Headline -->
      <h2 class="font-serif text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-oliveDark dark:text-white max-w-4xl mx-auto leading-[1.1]">
        Smarter Than Fixed Pipelines.<br>
        <span class="text-olive dark:text-emerald-400 italic">Engineered With RL.</span>
      </h2>

      <!-- Subtitle -->
      <p class="text-sm sm:text-lg text-mossText/80 dark:text-gray-300 max-w-2xl mx-auto font-sans font-normal leading-relaxed">
        An autonomous multi-agent coding engine that dynamically navigates software synthesis tasks using Actor-Critic PPO decision policies, isolated sandbox verification, and autonomous self-repair.
      </p>

      <!-- CTA Buttons -->
      <div class="flex flex-wrap items-center justify-center gap-3.5 pt-4">
        <button onclick="navigateTo('studio')" class="btn-action text-xs sm:text-sm font-bold uppercase tracking-wider px-6 py-3.5 rounded-xl shadow-xl flex items-center gap-2 transform transition hover:-translate-y-0.5 active:scale-95">
          <i data-lucide="play" class="w-4 h-4 fill-current"></i>
          <span>Launch Orchestrator Studio</span>
        </button>

        <button onclick="openProblemModal()" class="px-5 py-3.5 rounded-xl text-xs sm:text-sm font-semibold bg-white dark:bg-gray-800 hover:bg-sageSurface dark:hover:bg-gray-700 text-oliveDark dark:text-white border border-sageBorder dark:border-gray-700 shadow-md transition flex items-center gap-2 transform hover:-translate-y-0.5">
          <i data-lucide="library" class="w-4 h-4 text-olive dark:text-emerald-400"></i>
          <span>Browse 40+ Benchmarks</span>
        </button>

        <button onclick="scrollToArchitecture()" class="px-5 py-3.5 rounded-xl text-xs sm:text-sm font-semibold text-olive/80 dark:text-gray-300 hover:text-oliveDark dark:hover:text-white transition flex items-center gap-1.5">
          <span>Explore Architecture</span>
          <i data-lucide="arrow-down" class="w-4 h-4"></i>
        </button>
      </div>

      <!-- Live Metrics Ribbon -->
      <div class="pt-10 max-w-4xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="editorial-panel rounded-2xl p-4 text-center">
          <div class="text-2xl font-serif font-bold text-olive dark:text-emerald-400">8 Agents</div>
          <div class="text-[11px] text-olive/70 dark:text-gray-400 uppercase tracking-wider font-semibold mt-1">Specialized Pool</div>
        </div>
        <div class="editorial-panel rounded-2xl p-4 text-center">
          <div class="text-2xl font-serif font-bold text-olive dark:text-emerald-400">12-Dim</div>
          <div class="text-[11px] text-olive/70 dark:text-gray-400 uppercase tracking-wider font-semibold mt-1">State Vector Space</div>
        </div>
        <div class="editorial-panel rounded-2xl p-4 text-center">
          <div class="text-2xl font-serif font-bold text-olive dark:text-emerald-400">Subprocess</div>
          <div class="text-[11px] text-olive/70 dark:text-gray-400 uppercase tracking-wider font-semibold mt-1">Sandbox Security</div>
        </div>
        <div class="editorial-panel rounded-2xl p-4 text-center">
          <div class="text-2xl font-serif font-bold text-olive dark:text-emerald-400">14,400</div>
          <div class="text-[11px] text-olive/70 dark:text-gray-400 uppercase tracking-wider font-semibold mt-1">Daily Free Requests</div>
        </div>
      </div>

    </section>

    <!-- Interactive Quick-Launch Challenges -->
    <section class="max-w-6xl mx-auto px-6 py-12 border-t border-sageBorder/50 dark:border-gray-800/80">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h3 class="font-serif text-2xl sm:text-3xl font-bold text-oliveDark dark:text-white">
            Curated Benchmark Challenges
          </h3>
          <p class="text-xs sm:text-sm text-olive/80 dark:text-gray-400 mt-1">Click any challenge to load it into the Studio and initiate agent orchestration.</p>
        </div>
        <button onclick="openProblemModal()" class="btn-action text-xs font-semibold px-4 py-2 rounded-xl flex items-center gap-1.5 shadow-sm">
          <span>View All 40+</span>
          <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        
        <!-- Challenge 1 -->
        <div onclick="launchQuickProblem('is_palindrome')" class="editorial-panel rounded-2xl p-5 hover:border-olive dark:hover:border-emerald-500 cursor-pointer transition transform hover:-translate-y-1 shadow-sm group">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-mono font-bold text-oliveDark dark:text-white group-hover:text-olive dark:group-hover:text-emerald-400 transition">is_palindrome(s)</span>
            <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400">Easy</span>
          </div>
          <p class="text-xs text-mossText/80 dark:text-gray-400 line-clamp-2 leading-relaxed mb-4">
            Verify if a string is a palindrome, ignoring non-alphanumeric characters and casing.
          </p>
          <div class="flex items-center justify-between pt-2 border-t border-sageBorder/40 dark:border-gray-800 text-[11px] text-olive dark:text-emerald-400 font-semibold">
            <span>String Manipulation</span>
            <span class="flex items-center gap-1 group-hover:translate-x-1 transition-transform">
              <span>Launch</span>
              <i data-lucide="arrow-right" class="w-3 h-3"></i>
            </span>
          </div>
        </div>

        <!-- Challenge 2 -->
        <div onclick="launchQuickProblem('two_sum')" class="editorial-panel rounded-2xl p-5 hover:border-olive dark:hover:border-emerald-500 cursor-pointer transition transform hover:-translate-y-1 shadow-sm group">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-mono font-bold text-oliveDark dark:text-white group-hover:text-olive dark:group-hover:text-emerald-400 transition">two_sum(nums, target)</span>
            <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400">Easy</span>
          </div>
          <p class="text-xs text-mossText/80 dark:text-gray-400 line-clamp-2 leading-relaxed mb-4">
            Return indices of the two numbers that add up to target in O(n) hash map time.
          </p>
          <div class="flex items-center justify-between pt-2 border-t border-sageBorder/40 dark:border-gray-800 text-[11px] text-olive dark:text-emerald-400 font-semibold">
            <span>Hash Table & Array</span>
            <span class="flex items-center gap-1 group-hover:translate-x-1 transition-transform">
              <span>Launch</span>
              <i data-lucide="arrow-right" class="w-3 h-3"></i>
            </span>
          </div>
        </div>

        <!-- Challenge 3 -->
        <div onclick="launchQuickProblem('longest_consecutive')" class="editorial-panel rounded-2xl p-5 hover:border-olive dark:hover:border-emerald-500 cursor-pointer transition transform hover:-translate-y-1 shadow-sm group">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-mono font-bold text-oliveDark dark:text-white group-hover:text-olive dark:group-hover:text-emerald-400 transition">longest_consecutive(nums)</span>
            <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-400">Medium</span>
          </div>
          <p class="text-xs text-mossText/80 dark:text-gray-400 line-clamp-2 leading-relaxed mb-4">
            Find the length of the longest consecutive elements sequence in strict O(n) time.
          </p>
          <div class="flex items-center justify-between pt-2 border-t border-sageBorder/40 dark:border-gray-800 text-[11px] text-olive dark:text-emerald-400 font-semibold">
            <span>Set Algorithm</span>
            <span class="flex items-center gap-1 group-hover:translate-x-1 transition-transform">
              <span>Launch</span>
              <i data-lucide="arrow-right" class="w-3 h-3"></i>
            </span>
          </div>
        </div>

      </div>
    </section>

    <!-- Agent Pool Architecture Section -->
    <section id="architecture-section" class="max-w-6xl mx-auto px-6 py-16 border-t border-sageBorder/50 dark:border-gray-800/80">
      <div class="text-center max-w-3xl mx-auto mb-12">
        <h3 class="font-serif text-3xl sm:text-4xl font-bold text-oliveDark dark:text-white">
          The 8 Specialized Coding Agents
        </h3>
        <p class="text-xs sm:text-sm text-mossText/80 dark:text-gray-300 mt-2 leading-relaxed">
          The RL policy observes continuous state dimensions and dynamically selects only the necessary agents, skipping redundant work and automatically triggering self-repair upon sandbox test failures.
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <!-- Agent 1 -->
        <div class="editorial-panel rounded-2xl p-5 space-y-2.5 hover:border-olive dark:hover:border-emerald-500 transition">
          <div class="w-9 h-9 rounded-xl bg-olive dark:bg-emerald-600/30 text-white dark:text-emerald-400 flex items-center justify-center shadow-sm">
            <i data-lucide="feather" class="w-4 h-4"></i>
          </div>
          <h4 class="text-xs font-bold text-oliveDark dark:text-white uppercase tracking-wider">Requirement Analyzer</h4>
          <p class="text-[11px] text-mossText/80 dark:text-gray-400 leading-relaxed">Deconstructs raw user prompts into inputs, outputs, constraints, and boundary edge cases.</p>
        </div>

        <!-- Agent 2 -->
        <div class="editorial-panel rounded-2xl p-5 space-y-2.5 hover:border-olive dark:hover:border-emerald-500 transition">
          <div class="w-9 h-9 rounded-xl bg-amber-600 dark:bg-amber-600/30 text-white dark:text-amber-400 flex items-center justify-center shadow-sm">
            <i data-lucide="layers" class="w-4 h-4"></i>
          </div>
          <h4 class="text-xs font-bold text-oliveDark dark:text-white uppercase tracking-wider">Planning Agent</h4>
          <p class="text-[11px] text-mossText/80 dark:text-gray-400 leading-relaxed">Synthesizes modular architectural roadmaps and logical algorithmic decomposition steps.</p>
        </div>

        <!-- Agent 3 -->
        <div class="editorial-panel rounded-2xl p-5 space-y-2.5 hover:border-olive dark:hover:border-emerald-500 transition">
          <div class="w-9 h-9 rounded-xl bg-blue-600 dark:bg-cyan-600/30 text-white dark:text-cyan-400 flex items-center justify-center shadow-sm">
            <i data-lucide="database" class="w-4 h-4"></i>
          </div>
          <h4 class="text-xs font-bold text-oliveDark dark:text-white uppercase tracking-wider">Retrieval Agent</h4>
          <p class="text-[11px] text-mossText/80 dark:text-gray-400 leading-relaxed">Vector RAG store queries for relevant algorithmic patterns, formulas, and library references.</p>
        </div>

        <!-- Agent 4 -->
        <div class="editorial-panel rounded-2xl p-5 space-y-2.5 hover:border-olive dark:hover:border-emerald-500 transition">
          <div class="w-9 h-9 rounded-xl bg-emerald-600 dark:bg-emerald-600/30 text-white dark:text-emerald-400 flex items-center justify-center shadow-sm">
            <i data-lucide="code" class="w-4 h-4"></i>
          </div>
          <h4 class="text-xs font-bold text-oliveDark dark:text-white uppercase tracking-wider">Coding Agent</h4>
          <p class="text-[11px] text-mossText/80 dark:text-gray-400 leading-relaxed">Synthesizes high-performance, robust Python source code strictly matching typing constraints.</p>
        </div>

        <!-- Agent 5 -->
        <div class="editorial-panel rounded-2xl p-5 space-y-2.5 hover:border-olive dark:hover:border-emerald-500 transition">
          <div class="w-9 h-9 rounded-xl bg-indigo-600 dark:bg-indigo-600/30 text-white dark:text-indigo-400 flex items-center justify-center shadow-sm">
            <i data-lucide="check-circle" class="w-4 h-4"></i>
          </div>
          <h4 class="text-xs font-bold text-oliveDark dark:text-white uppercase tracking-wider">Testing Agent</h4>
          <p class="text-[11px] text-mossText/80 dark:text-gray-400 leading-relaxed">Executes dynamically generated assertions inside an isolated subprocess Python sandbox.</p>
        </div>

        <!-- Agent 6 -->
        <div class="editorial-panel rounded-2xl p-5 space-y-2.5 hover:border-olive dark:hover:border-emerald-500 transition">
          <div class="w-9 h-9 rounded-xl bg-purple-600 dark:bg-purple-600/30 text-white dark:text-purple-400 flex items-center justify-center shadow-sm">
            <i data-lucide="shield-check" class="w-4 h-4"></i>
          </div>
          <h4 class="text-xs font-bold text-oliveDark dark:text-white uppercase tracking-wider">Review Agent</h4>
          <p class="text-[11px] text-mossText/80 dark:text-gray-400 leading-relaxed">Performs code quality auditing, time complexity estimation, and stylistic checks.</p>
        </div>

        <!-- Agent 7 -->
        <div class="editorial-panel rounded-2xl p-5 space-y-2.5 hover:border-olive dark:hover:border-emerald-500 transition">
          <div class="w-9 h-9 rounded-xl bg-rose-600 dark:bg-rose-600/30 text-white dark:text-rose-400 flex items-center justify-center shadow-sm">
            <i data-lucide="alert-octagon" class="w-4 h-4"></i>
          </div>
          <h4 class="text-xs font-bold text-oliveDark dark:text-white uppercase tracking-wider">Error Analysis</h4>
          <p class="text-[11px] text-mossText/80 dark:text-gray-400 leading-relaxed">Diagnoses tracebacks, syntax errors, and failed assertions to locate precise failure root causes.</p>
        </div>

        <!-- Agent 8 -->
        <div class="editorial-panel rounded-2xl p-5 space-y-2.5 hover:border-olive dark:hover:border-emerald-500 transition">
          <div class="w-9 h-9 rounded-xl bg-teal-600 dark:bg-teal-600/30 text-white dark:text-teal-400 flex items-center justify-center shadow-sm">
            <i data-lucide="wrench" class="w-4 h-4"></i>
          </div>
          <h4 class="text-xs font-bold text-oliveDark dark:text-white uppercase tracking-wider">Self-Repair Agent</h4>
          <p class="text-[11px] text-mossText/80 dark:text-gray-400 leading-relaxed">Applies surgical patches and repairs defective functions without manual developer intervention.</p>
        </div>

      </div>
    </section>

    <!-- RL vs Fixed Baseline Comparison -->
    <section class="max-w-6xl mx-auto px-6 py-14 border-t border-sageBorder/50 dark:border-gray-800/80">
      <div class="editorial-panel rounded-3xl p-8 sm:p-12">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div>
            <span class="text-xs font-mono uppercase tracking-widest text-olive dark:text-emerald-400 font-bold">Policy Evaluation</span>
            <h3 class="font-serif text-3xl sm:text-4xl font-bold text-oliveDark dark:text-white mt-2 mb-4">
              Why Reinforcement Learning Outperforms Static Chains
            </h3>
            <p class="text-xs sm:text-sm text-mossText/80 dark:text-gray-300 leading-relaxed mb-4">
              Traditional multi-agent systems rely on static DAGs or sequential chains that execute every agent regardless of necessity, inflating latency and cost.
            </p>
            <p class="text-xs sm:text-sm text-mossText/80 dark:text-gray-300 leading-relaxed">
              Our PPO policy observes the state, leverages strict action masking to eliminate loops, and terminates execution as soon as assertions pass with verified quality.
            </p>
            <div class="mt-6 flex gap-3">
              <button onclick="navigateTo('studio')" class="btn-action text-xs font-bold uppercase tracking-wider px-5 py-2.5 rounded-xl shadow-md flex items-center gap-2">
                <span>Test in Studio</span>
                <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
              </button>
            </div>
          </div>

          <div class="space-y-4">
            <div class="p-4 rounded-2xl bg-sageSurface/60 dark:bg-gray-800/80 border border-sageBorder dark:border-gray-700">
              <div class="flex items-center justify-between font-bold text-xs text-oliveDark dark:text-white mb-1">
                <span>Deterministic Baseline Pipeline</span>
                <span class="text-rose-600 font-mono">Fixed Sequence</span>
              </div>
              <p class="text-[11px] text-mossText/70 dark:text-gray-400">Always runs all 6-8 agents in lockstep. High token consumption on simple tasks.</p>
            </div>

            <div class="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 shadow-md">
              <div class="flex items-center justify-between font-bold text-xs text-emerald-800 dark:text-emerald-300 mb-1">
                <span>PPO RL Orchestration Policy</span>
                <span class="text-emerald-600 dark:text-emerald-400 font-mono">Learned Dispatch</span>
              </div>
              <p class="text-[11px] text-emerald-900/80 dark:text-emerald-200/80">Dynamically skips unneeded steps, avoids redundant re-testing, and optimizes cumulative reward.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Bottom Launch Banner -->
    <section class="max-w-4xl mx-auto px-6 py-16 text-center space-y-4">
      <h3 class="font-serif text-3xl sm:text-4xl font-bold text-oliveDark dark:text-white">
        Ready to Experience Autonomous Code Synthesis?
      </h3>
      <p class="text-xs sm:text-sm text-mossText/80 dark:text-gray-300 max-w-xl mx-auto">
        Step into the Studio Workspace to watch the multi-agent system synthesize, test, review, and patch code in real time.
      </p>
      <div class="pt-2">
        <button onclick="navigateTo('studio')" class="btn-action text-xs sm:text-sm font-bold uppercase tracking-wider px-7 py-3.5 rounded-xl shadow-xl inline-flex items-center gap-2 transform transition hover:scale-105 active:scale-95">
          <i data-lucide="play" class="w-4 h-4 fill-current"></i>
          <span>Open Orchestrator Studio</span>
        </button>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-sageBorder/60 dark:border-gray-800/80 py-8 text-center text-xs text-olive/60 dark:text-gray-500">
      Multi-Agent Coding System with RL Orchestration • Built with FastAPI, PPO & Tailwind CSS
    </footer>

  </div>

  <!-- ========================================================================= -->
  <!-- VIEW 2: STUDIO / ORCHESTRATOR WORKSPACE -->
  <!-- ========================================================================= -->
  <div id="view-studio" class="hidden transition-opacity duration-300 relative z-10 pb-12">
    
    <!-- Studio Top Action Bar -->
    <div class="max-w-7xl mx-auto px-6 pt-6 pb-2 flex items-center justify-between">
      <button onclick="navigateTo('landing')" class="text-xs font-semibold text-olive dark:text-emerald-400 hover:underline flex items-center gap-1.5 p-2 rounded-xl bg-white dark:bg-gray-800 border border-sageBorder dark:border-gray-700 shadow-sm transition">
        <i data-lucide="arrow-left" class="w-4 h-4"></i>
        <span>Back to Overview</span>
      </button>

      <div class="flex items-center gap-2">
        <span class="text-xs text-olive/70 dark:text-gray-400 font-medium">Orchestration Studio Active</span>
      </div>
    </div>

    <!-- Main Workspace Grid -->
    <main class="max-w-7xl mx-auto px-6 py-4 grid grid-cols-1 lg:grid-cols-12 gap-7">

      <!-- Left Column: Input Controls & Agent Architecture (5 Cols) -->
      <div class="lg:col-span-5 space-y-6">
        
        <!-- Input Card -->
        <div class="editorial-panel rounded-2xl p-6 shadow-sm">
          <div class="flex items-center justify-between mb-3.5 border-b border-sageBorder/60 dark:border-gray-800 pb-3">
            <label class="font-serif text-lg font-bold text-oliveDark dark:text-white flex items-center gap-2">
              <i data-lucide="feather" class="w-4 h-4 text-olive dark:text-emerald-400"></i>
              Software Requirement
            </label>
            
            <!-- Mode Selector Toggle -->
            <div class="inline-flex bg-sageSurface dark:bg-gray-800 p-0.5 rounded-full border border-sageBorder dark:border-gray-700 text-xs">
              <button id="mode-rl" onclick="setMode('rl')" class="px-3 py-1 rounded-full font-semibold transition bg-olive dark:bg-emerald-600 text-white shadow-sm">
                RL Orchestrator
              </button>
              <button id="mode-baseline" onclick="setMode('baseline')" class="px-3 py-1 rounded-full font-medium transition text-mossText dark:text-gray-400 hover:text-oliveDark dark:hover:text-white">
                Baseline
              </button>
            </div>
          </div>

          <textarea id="req-input" rows="3" 
            class="w-full bg-[#FAFCF9] dark:bg-gray-900 border border-sageBorder dark:border-gray-700 rounded-xl p-3.5 text-xs text-mossText dark:text-gray-100 placeholder-olive/50 dark:placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 transition custom-scrollbar font-sans leading-relaxed"
            placeholder="Describe your coding task (e.g. Write a python function is_palindrome(s: str) -> bool)...">Write a python function `is_palindrome(s: str) -> bool` that checks if a string is a palindrome, ignoring casing and non-alphanumeric characters.</textarea>

          <!-- Curated Benchmarks Shortcuts -->
          <div class="mt-3.5">
            <div class="flex items-center justify-between mb-2">
              <span class="text-[11px] uppercase tracking-wider text-olive/80 dark:text-gray-400 font-semibold">Curated Benchmarks:</span>
              <button onclick="openProblemModal()" class="text-[11px] text-olive dark:text-emerald-400 hover:underline flex items-center gap-1 font-medium">
                <span>Browse All 40+</span>
                <i data-lucide="arrow-right" class="w-3 h-3"></i>
              </button>
            </div>
            <div class="flex flex-wrap gap-1.5" id="template-chips">
              <button onclick="setTemplate('is_palindrome')" class="px-2.5 py-1 rounded-lg bg-sageSurface dark:bg-gray-800 hover:bg-sageBorder dark:hover:bg-gray-700 text-xs text-oliveDark dark:text-gray-200 border border-sageBorder dark:border-gray-700 transition font-medium">Palindrome</button>
              <button onclick="setTemplate('two_sum')" class="px-2.5 py-1 rounded-lg bg-sageSurface dark:bg-gray-800 hover:bg-sageBorder dark:hover:bg-gray-700 text-xs text-oliveDark dark:text-gray-200 border border-sageBorder dark:border-gray-700 transition font-medium">Two Sum</button>
              <button onclick="setTemplate('is_prime')" class="px-2.5 py-1 rounded-lg bg-sageSurface dark:bg-gray-800 hover:bg-sageBorder dark:hover:bg-gray-700 text-xs text-oliveDark dark:text-gray-200 border border-sageBorder dark:border-gray-700 transition font-medium">Prime Check</button>
              <button onclick="setTemplate('longest_consecutive')" class="px-2.5 py-1 rounded-lg bg-sageSurface dark:bg-gray-800 hover:bg-sageBorder dark:hover:bg-gray-700 text-xs text-oliveDark dark:text-gray-200 border border-sageBorder dark:border-gray-700 transition font-medium">Longest Consecutive</button>
              <button onclick="setTemplate('sum_of_digits')" class="px-2.5 py-1 rounded-lg bg-sageSurface dark:bg-gray-800 hover:bg-sageBorder dark:hover:bg-gray-700 text-xs text-oliveDark dark:text-gray-200 border border-sageBorder dark:border-gray-700 transition font-medium">Sum of Digits</button>
            </div>
          </div>

          <!-- Custom Test Cases Editor -->
          <div class="mt-4 pt-3.5 border-t border-sageBorder/60 dark:border-gray-800">
            <div class="flex items-center justify-between mb-2">
              <label class="text-xs font-semibold text-oliveDark dark:text-gray-200 flex items-center gap-1.5">
                <i data-lucide="flask-conical" class="w-3.5 h-3.5 text-olive dark:text-emerald-400"></i>
                Custom Test Assertions
              </label>
              <span class="text-[10px] text-olive/70 dark:text-gray-400 italic">(Auto-generated if empty)</span>
            </div>

            <textarea id="custom-tests-input" rows="3" 
              class="w-full bg-[#FAFCF9] dark:bg-gray-900 border border-sageBorder dark:border-gray-700 rounded-xl p-2.5 text-xs font-mono text-mossText dark:text-gray-200 placeholder-olive/40 dark:placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 custom-scrollbar"
              placeholder="assert is_palindrome('racecar') == True&#10;assert is_palindrome('hello') == False">assert is_palindrome('A man, a plan, a canal: Panama') == True
assert is_palindrome('race a car') == False
assert is_palindrome('') == True
assert is_palindrome('0P') == False</textarea>
          </div>

          <!-- Submit Button -->
          <button id="run-btn" onclick="executePipelineStream()" 
            class="mt-5 w-full btn-action font-semibold py-3 px-4 rounded-xl shadow-md flex items-center justify-center gap-2 transition active:scale-[0.98] tracking-wider text-xs uppercase">
            <i data-lucide="play" class="w-3.5 h-3.5 fill-current"></i>
            <span>Execute Multi-Agent System</span>
          </button>
        </div>

        <!-- Agent Pool Architecture Visualizer -->
        <div class="editorial-panel rounded-2xl p-6 shadow-sm">
          <div class="flex items-center justify-between mb-3.5 border-b border-sageBorder/60 dark:border-gray-800 pb-2.5">
            <h3 class="font-serif text-lg font-bold text-oliveDark dark:text-white flex items-center gap-2">
              <i data-lucide="workflow" class="w-4 h-4 text-olive dark:text-emerald-400"></i>
              Agent Pool Architecture
            </h3>
            <span id="live-agent-status" class="text-[10px] uppercase font-bold tracking-widest px-2.5 py-0.5 rounded-full bg-sageSurface dark:bg-gray-800 text-olive dark:text-emerald-400 border border-sageBorder dark:border-gray-700">
              Pool Idle
            </span>
          </div>
          
          <div class="grid grid-cols-2 gap-2.5 text-xs" id="agent-nodes">
            <div id="node-RequirementAnalyzer" class="agent-node p-3 rounded-xl bg-sageSurface/70 dark:bg-gray-800/80 border border-sageBorder dark:border-gray-700 flex items-center justify-between">
              <div class="flex items-center gap-2.5 min-w-0">
                <div class="w-2.5 h-2.5 rounded-full bg-olive dark:bg-emerald-500 shrink-0"></div>
                <div class="truncate">
                  <div class="font-semibold text-oliveDark dark:text-white truncate">Req Analyzer</div>
                  <div class="text-[10px] text-olive/80 dark:text-gray-400">Spec Extraction</div>
                </div>
              </div>
              <span class="status-badge text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-white/70 dark:bg-gray-700 text-oliveDark dark:text-gray-300">IDLE</span>
            </div>

            <div id="node-PlanningAgent" class="agent-node p-3 rounded-xl bg-sageSurface/70 dark:bg-gray-800/80 border border-sageBorder dark:border-gray-700 flex items-center justify-between">
              <div class="flex items-center gap-2.5 min-w-0">
                <div class="w-2.5 h-2.5 rounded-full bg-amber-600 dark:bg-amber-400 shrink-0"></div>
                <div class="truncate">
                  <div class="font-semibold text-oliveDark dark:text-white truncate">Planning Agent</div>
                  <div class="text-[10px] text-olive/80 dark:text-gray-400">Decomposition</div>
                </div>
              </div>
              <span class="status-badge text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-white/70 dark:bg-gray-700 text-oliveDark dark:text-gray-300">IDLE</span>
            </div>

            <div id="node-RetrievalAgent" class="agent-node p-3 rounded-xl bg-sageSurface/70 dark:bg-gray-800/80 border border-sageBorder dark:border-gray-700 flex items-center justify-between">
              <div class="flex items-center gap-2.5 min-w-0">
                <div class="w-2.5 h-2.5 rounded-full bg-blue-600 dark:bg-cyan-400 shrink-0"></div>
                <div class="truncate">
                  <div class="font-semibold text-oliveDark dark:text-white truncate">Retrieval Agent</div>
                  <div class="text-[10px] text-olive/80 dark:text-gray-400">RAG Vector Store</div>
                </div>
              </div>
              <span class="status-badge text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-white/70 dark:bg-gray-700 text-oliveDark dark:text-gray-300">IDLE</span>
            </div>

            <div id="node-CodingAgent" class="agent-node p-3 rounded-xl bg-sageSurface/70 dark:bg-gray-800/80 border border-sageBorder dark:border-gray-700 flex items-center justify-between">
              <div class="flex items-center gap-2.5 min-w-0">
                <div class="w-2.5 h-2.5 rounded-full bg-emerald-600 dark:bg-emerald-400 shrink-0"></div>
                <div class="truncate">
                  <div class="font-semibold text-oliveDark dark:text-white truncate">Coding Agent</div>
                  <div class="text-[10px] text-olive/80 dark:text-gray-400">Synthesizer</div>
                </div>
              </div>
              <span class="status-badge text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-white/70 dark:bg-gray-700 text-oliveDark dark:text-gray-300">IDLE</span>
            </div>

            <div id="node-TestingAgent" class="agent-node p-3 rounded-xl bg-sageSurface/70 dark:bg-gray-800/80 border border-sageBorder dark:border-gray-700 flex items-center justify-between">
              <div class="flex items-center gap-2.5 min-w-0">
                <div class="w-2.5 h-2.5 rounded-full bg-indigo-600 dark:bg-indigo-400 shrink-0"></div>
                <div class="truncate">
                  <div class="font-semibold text-oliveDark dark:text-white truncate">Testing Agent</div>
                  <div class="text-[10px] text-olive/80 dark:text-gray-400">Sandbox Runner</div>
                </div>
              </div>
              <span class="status-badge text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-white/70 dark:bg-gray-700 text-oliveDark dark:text-gray-300">IDLE</span>
            </div>

            <div id="node-ReviewAgent" class="agent-node p-3 rounded-xl bg-sageSurface/70 dark:bg-gray-800/80 border border-sageBorder dark:border-gray-700 flex items-center justify-between">
              <div class="flex items-center gap-2.5 min-w-0">
                <div class="w-2.5 h-2.5 rounded-full bg-purple-600 dark:bg-purple-400 shrink-0"></div>
                <div class="truncate">
                  <div class="font-semibold text-oliveDark dark:text-white truncate">Review Agent</div>
                  <div class="text-[10px] text-olive/80 dark:text-gray-400">Quality Checker</div>
                </div>
              </div>
              <span class="status-badge text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-white/70 dark:bg-gray-700 text-oliveDark dark:text-gray-300">IDLE</span>
            </div>

            <div id="node-ErrorAnalysisAgent" class="agent-node p-3 rounded-xl bg-sageSurface/70 dark:bg-gray-800/80 border border-sageBorder dark:border-gray-700 flex items-center justify-between">
              <div class="flex items-center gap-2.5 min-w-0">
                <div class="w-2.5 h-2.5 rounded-full bg-rose-600 dark:bg-rose-400 shrink-0"></div>
                <div class="truncate">
                  <div class="font-semibold text-oliveDark dark:text-white truncate">Error Analysis</div>
                  <div class="text-[10px] text-olive/80 dark:text-gray-400">Diagnostic Trace</div>
                </div>
              </div>
              <span class="status-badge text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-white/70 dark:bg-gray-700 text-oliveDark dark:text-gray-300">IDLE</span>
            </div>

            <div id="node-SelfRepairAgent" class="agent-node p-3 rounded-xl bg-sageSurface/70 dark:bg-gray-800/80 border border-sageBorder dark:border-gray-700 flex items-center justify-between">
              <div class="flex items-center gap-2.5 min-w-0">
                <div class="w-2.5 h-2.5 rounded-full bg-teal-600 dark:bg-teal-400 shrink-0"></div>
                <div class="truncate">
                  <div class="font-semibold text-oliveDark dark:text-white truncate">Self Repair</div>
                  <div class="text-[10px] text-olive/80 dark:text-gray-400">Auto Patcher</div>
                </div>
              </div>
              <span class="status-badge text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-white/70 dark:bg-gray-700 text-oliveDark dark:text-gray-300">IDLE</span>
            </div>
          </div>
        </div>

      </div>

      <!-- Right Column: Results, Playground, Tabs (7 Cols) -->
      <div class="lg:col-span-7 space-y-6">

        <!-- Status Header Metrics -->
        <div class="grid grid-cols-4 gap-3">
          <div class="editorial-panel rounded-xl p-3.5 text-center">
            <div class="text-[10px] uppercase font-semibold text-olive/70 dark:text-gray-400 tracking-widest">Test Suite</div>
            <div id="metric-status" class="text-xs font-bold text-mossText dark:text-gray-100 mt-1">Ready</div>
          </div>
          <div class="editorial-panel rounded-xl p-3.5 text-center">
            <div class="text-[10px] uppercase font-semibold text-olive/70 dark:text-gray-400 tracking-widest">Tests Passed</div>
            <div id="metric-tests-ratio" class="text-xs font-bold text-olive dark:text-emerald-400 mt-1">-- / --</div>
          </div>
          <div class="editorial-panel rounded-xl p-3.5 text-center">
            <div class="text-[10px] uppercase font-semibold text-olive/70 dark:text-gray-400 tracking-widest">Quality Score</div>
            <div id="metric-score" class="text-xs font-bold text-olive dark:text-emerald-400 mt-1">-- / 1.0</div>
          </div>
          <div class="editorial-panel rounded-xl p-3.5 text-center">
            <div class="text-[10px] uppercase font-semibold text-olive/70 dark:text-gray-400 tracking-widest">RL Reward</div>
            <div id="metric-reward" class="text-xs font-bold text-mossText dark:text-gray-100 mt-1">--</div>
          </div>
        </div>

        <!-- Main Tabbed Viewer -->
        <div class="editorial-panel rounded-2xl shadow-sm overflow-hidden flex flex-col min-h-[540px]">
          
          <!-- Tab Navigation -->
          <div class="flex items-center justify-between border-b border-sageBorder dark:border-gray-800 bg-sageSurface/50 dark:bg-gray-900/50 px-4 pt-2">
            <div class="flex items-center gap-1.5 flex-wrap">
              <button onclick="switchTab('code')" id="tab-btn-code" class="px-3 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-olive dark:border-emerald-400 text-oliveDark dark:text-white flex items-center gap-1.5 transition">
                <i data-lucide="code" class="w-3.5 h-3.5 text-olive dark:text-emerald-400"></i>
                <span>Generated Code</span>
              </button>
              <button onclick="switchTab('playground')" id="tab-btn-playground" class="px-3 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-olive/70 dark:text-gray-400 hover:text-oliveDark dark:hover:text-white flex items-center gap-1.5 transition">
                <i data-lucide="play-circle" class="w-3.5 h-3.5 text-olive dark:text-emerald-400"></i>
                <span>Playground</span>
              </button>
              <button onclick="switchTab('tests')" id="tab-btn-tests" class="px-3 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-olive/70 dark:text-gray-400 hover:text-oliveDark dark:hover:text-white flex items-center gap-1.5 transition">
                <i data-lucide="check-circle" class="w-3.5 h-3.5 text-olive dark:text-emerald-400"></i>
                <span>Sandbox Tests</span>
              </button>
              <button onclick="switchTab('plan')" id="tab-btn-plan" class="px-3 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-olive/70 dark:text-gray-400 hover:text-oliveDark dark:hover:text-white flex items-center gap-1.5 transition">
                <i data-lucide="list-tree" class="w-3.5 h-3.5 text-olive dark:text-emerald-400"></i>
                <span>Spec & Plan</span>
              </button>
              <button onclick="switchTab('review')" id="tab-btn-review" class="px-3 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-olive/70 dark:text-gray-400 hover:text-oliveDark dark:hover:text-white flex items-center gap-1.5 transition">
                <i data-lucide="shield-check" class="w-3.5 h-3.5 text-olive dark:text-emerald-400"></i>
                <span>Review</span>
              </button>
              <button onclick="switchTab('trace')" id="tab-btn-trace" class="px-3 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-olive/70 dark:text-gray-400 hover:text-oliveDark dark:hover:text-white flex items-center gap-1.5 transition">
                <i data-lucide="activity" class="w-3.5 h-3.5 text-olive dark:text-emerald-400"></i>
                <span>RL Trace & State</span>
              </button>
            </div>

            <div class="flex items-center gap-1.5">
              <button onclick="copyCode()" id="copy-btn" class="text-xs text-oliveDark dark:text-gray-200 hover:text-olive dark:hover:text-emerald-400 flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white dark:bg-gray-800 border border-sageBorder dark:border-gray-700 transition shadow-sm font-medium">
                <i data-lucide="copy" class="w-3 h-3 text-olive dark:text-emerald-400"></i>
                <span>Copy</span>
              </button>
            </div>
          </div>

          <!-- Tab 1: Generated Code -->
          <div id="tab-content-code" class="p-5 flex-1 flex flex-col bg-[#1E271D] dark:bg-[#030712] relative">
            <div class="flex items-center justify-between mb-2">
              <span class="text-[10px] font-mono text-emerald-400 uppercase tracking-widest">Python 3 Execution Artifact</span>
              <button onclick="toggleEditCode()" id="edit-code-toggle-btn" class="text-[11px] text-gray-300 hover:text-white flex items-center gap-1 px-2 py-0.5 rounded bg-white/10 hover:bg-white/20 transition">
                <i data-lucide="edit-3" class="w-3 h-3"></i>
                <span id="edit-code-label">Edit in Sandbox</span>
              </button>
            </div>

            <!-- Read-only Highlighted Code View -->
            <pre id="code-pre-container" class="flex-1 rounded-xl overflow-hidden"><code class="language-python rounded-xl h-full custom-scrollbar" id="code-display"># Generated Python solution will appear here after execution...
def solution():
    pass</code></pre>

            <!-- Editable Textarea -->
            <div id="code-editor-container" class="flex-1 hidden flex-col">
              <textarea id="code-editable-textarea" class="w-full flex-1 bg-gray-950 text-emerald-300 font-mono text-xs p-4 rounded-xl border border-gray-800 focus:outline-none focus:ring-1 focus:ring-emerald-500 custom-scrollbar resize-none"></textarea>
              <div class="flex items-center justify-end gap-2 mt-2">
                <button onclick="runEditedCodeInSandbox()" class="btn-action text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center gap-1">
                  <i data-lucide="play" class="w-3 h-3 fill-current"></i>
                  <span>Re-verify in Sandbox</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Tab 2: Test Custom Input Playground -->
          <div id="tab-content-playground" class="p-6 flex-1 hidden space-y-5 bg-white dark:bg-gray-900">
            <div class="p-4 rounded-xl border border-sageBorder dark:border-gray-800 editorial-panel-sage flex items-center justify-between gap-3">
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-full bg-olive dark:bg-emerald-600 text-white flex items-center justify-center shadow-sm">
                  <i data-lucide="terminal" class="w-4 h-4"></i>
                </div>
                <div>
                  <div class="text-xs font-bold text-oliveDark dark:text-white">Live Subprocess Playground</div>
                  <div class="text-[11px] text-olive/80 dark:text-gray-400">Execute custom inputs against the synthesized function in the sandboxed Python runner.</div>
                </div>
              </div>
            </div>

            <!-- Custom Input Execution Form -->
            <div class="space-y-3">
              <div>
                <label class="text-xs font-semibold text-oliveDark dark:text-gray-200 mb-1.5 block flex items-center justify-between">
                  <span>Enter Custom Input or Function Call:</span>
                  <span class="text-[10px] text-olive/70 dark:text-gray-400 font-normal">e.g. "racecar" or is_palindrome("radar")</span>
                </label>
                <div class="flex gap-2">
                  <input id="playground-input" type="text" 
                    class="flex-1 bg-[#FAFCF9] dark:bg-gray-800 border border-sageBorder dark:border-gray-700 rounded-xl px-3.5 py-2.5 text-xs font-mono text-mossText dark:text-gray-100 placeholder-olive/40 dark:placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                    placeholder='is_palindrome("Never odd or even")' value='is_palindrome("Never odd or even")'>
                  <button onclick="runCustomInputLive()" id="playground-run-btn"
                    class="btn-action text-xs font-bold px-4 py-2.5 rounded-xl shadow-sm flex items-center gap-1.5 transition active:scale-95 shrink-0 uppercase tracking-wider">
                    <i data-lucide="play" class="w-3.5 h-3.5 fill-current"></i>
                    <span>Run Input</span>
                  </button>
                </div>
              </div>

              <!-- Output Box -->
              <div class="p-4 rounded-xl bg-sageSurface/50 dark:bg-gray-800/60 border border-sageBorder dark:border-gray-700 space-y-3">
                <div class="flex items-center justify-between border-b border-sageBorder dark:border-gray-700 pb-2">
                  <span class="text-xs font-bold text-oliveDark dark:text-white flex items-center gap-1.5">
                    <i data-lucide="check-circle-2" class="w-3.5 h-3.5 text-olive dark:text-emerald-400"></i>
                    Execution Result
                  </span>
                  <span id="playground-time" class="text-[10px] font-mono text-olive/80 dark:text-emerald-400">-- ms</span>
                </div>

                <!-- Return Value Display -->
                <div>
                  <div class="text-[11px] font-medium text-olive/80 dark:text-gray-400 mb-1">Returned Value:</div>
                  <div id="playground-output-val" class="p-3 rounded-lg bg-white dark:bg-gray-900 border border-sageBorder dark:border-gray-700 text-sm font-mono font-bold text-oliveDark dark:text-emerald-300">
                    Awaiting execution...
                  </div>
                </div>

                <!-- Console Stdout -->
                <div id="playground-stdout-box" class="hidden">
                  <div class="text-[11px] font-medium text-olive/80 dark:text-gray-400 mb-1">Standard Output (stdout):</div>
                  <pre id="playground-stdout-val" class="p-2.5 rounded-lg bg-white dark:bg-gray-900 border border-sageBorder dark:border-gray-700 text-xs font-mono text-mossText dark:text-gray-200 overflow-x-auto"></pre>
                </div>

                <!-- Error Box -->
                <div id="playground-err-box" class="hidden">
                  <div class="text-[11px] font-medium text-rose-600 dark:text-rose-400 mb-1">Execution Error / Exception:</div>
                  <pre id="playground-err-val" class="p-2.5 rounded-lg bg-red-50 dark:bg-rose-950/40 border border-red-200 dark:border-rose-900 text-xs font-mono text-red-700 dark:text-rose-300 overflow-x-auto"></pre>
                </div>
              </div>
            </div>
          </div>

          <!-- Tab 3: Sandbox Tests & Results -->
          <div id="tab-content-tests" class="p-6 flex-1 hidden space-y-5 bg-white dark:bg-gray-900">
            <!-- Test Status Banner -->
            <div id="test-banner" class="p-4 rounded-xl border border-sageBorder dark:border-gray-800 editorial-panel-sage flex items-center gap-3">
              <div class="w-9 h-9 rounded-full bg-white dark:bg-gray-800 flex items-center justify-center text-olive dark:text-emerald-400 border border-sageBorder dark:border-gray-700" id="test-icon">
                <i data-lucide="help-circle" class="w-5 h-5"></i>
              </div>
              <div>
                <div class="text-xs font-bold text-oliveDark dark:text-white" id="test-summary-title">Awaiting Execution</div>
                <div class="text-[11px] text-olive/80 dark:text-gray-400" id="test-summary-desc">Run the pipeline to test code in the isolated subprocess sandbox.</div>
              </div>
            </div>

            <!-- Individual Executed Assertions -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-oliveDark dark:text-white flex items-center gap-1.5">
                  <i data-lucide="list-checks" class="w-4 h-4 text-olive dark:text-emerald-400"></i>
                  Individual Test Case Assertions:
                </span>
                <span id="test-count-badge" class="text-[10px] px-2.5 py-0.5 rounded-full bg-sageSurface dark:bg-gray-800 text-oliveDark dark:text-gray-200 font-mono border border-sageBorder dark:border-gray-700">0 tests</span>
              </div>
              
              <div class="space-y-2 max-h-56 overflow-y-auto custom-scrollbar" id="test-cases-list">
                <div class="text-xs text-olive/70 dark:text-gray-400 italic p-3 rounded-lg bg-[#FAFCF9] dark:bg-gray-800 border border-sageBorder dark:border-gray-700">
                  No test assertions evaluated yet.
                </div>
              </div>
            </div>

            <!-- Complete Unit Test Suite Code -->
            <div>
              <div class="text-xs font-semibold text-oliveDark dark:text-gray-300 mb-1.5">Complete Unit Test Suite:</div>
              <pre class="bg-[#1E271D] dark:bg-gray-950 p-3.5 rounded-xl text-xs font-mono text-[#D8E4D5] dark:text-gray-300 overflow-x-auto border border-sageBorder dark:border-gray-800 custom-scrollbar max-h-40" id="test-code-display"># Test code will appear here...</pre>
            </div>

            <!-- Sandbox Execution Log Output -->
            <div>
              <div class="text-xs font-semibold text-oliveDark dark:text-gray-300 mb-1.5">Sandbox Execution Log (Stdout):</div>
              <pre class="bg-[#FAFCF9] dark:bg-gray-950 p-2.5 rounded-xl text-xs font-mono text-mossText dark:text-gray-300 overflow-x-auto border border-sageBorder dark:border-gray-800 custom-scrollbar max-h-24" id="test-stdout-display">No stdout logs available.</pre>
            </div>

            <div id="test-stderr-box" class="hidden">
              <div class="text-xs font-semibold text-red-700 dark:text-rose-400 mb-1.5">Sandbox Stderr / Traceback:</div>
              <pre class="bg-red-50 dark:bg-rose-950/40 p-2.5 rounded-xl text-xs font-mono text-red-700 dark:text-rose-300 overflow-x-auto border border-red-200 dark:border-rose-900 custom-scrollbar max-h-32" id="test-stderr-display"></pre>
            </div>
          </div>

          <!-- Tab 4: Spec & Architecture Plan -->
          <div id="tab-content-plan" class="p-6 flex-1 hidden space-y-5 bg-white dark:bg-gray-900">
            <!-- Structured Requirement Section -->
            <div>
              <h4 class="text-xs font-bold text-oliveDark dark:text-white uppercase tracking-wider flex items-center gap-1.5 mb-2.5">
                <i data-lucide="file-check-2" class="w-4 h-4 text-olive dark:text-emerald-400"></i>
                <span>Structured Specification (RequirementAnalyzer)</span>
              </h4>
              <div id="spec-container" class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div class="p-3.5 rounded-xl bg-sageSurface/50 dark:bg-gray-800/60 border border-sageBorder dark:border-gray-700">
                  <div class="text-[11px] font-bold text-olive dark:text-emerald-400 mb-1">Inputs & Constraints:</div>
                  <ul id="spec-constraints" class="text-xs text-mossText dark:text-gray-300 space-y-1 font-mono">
                    <li class="italic text-olive/60 dark:text-gray-500">Awaiting analyzer execution...</li>
                  </ul>
                </div>
                <div class="p-3.5 rounded-xl bg-sageSurface/50 dark:bg-gray-800/60 border border-sageBorder dark:border-gray-700">
                  <div class="text-[11px] font-bold text-amber-700 dark:text-amber-400 mb-1">Identified Edge Cases:</div>
                  <ul id="spec-edge-cases" class="text-xs text-mossText dark:text-gray-300 space-y-1">
                    <li class="italic text-olive/60 dark:text-gray-500">Awaiting analyzer execution...</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Planning Agent Roadmap -->
            <div>
              <h4 class="text-xs font-bold text-oliveDark dark:text-white uppercase tracking-wider flex items-center gap-1.5 mb-2.5">
                <i data-lucide="layers" class="w-4 h-4 text-olive dark:text-emerald-400"></i>
                <span>Architectural Roadmap (PlanningAgent)</span>
              </h4>
              <div id="plan-list" class="space-y-2">
                <div class="text-xs text-olive/60 dark:text-gray-500 italic p-3 rounded-xl bg-sageSurface/40 dark:bg-gray-800/40 border border-sageBorder dark:border-gray-700">
                  No roadmap generated yet.
                </div>
              </div>
            </div>

            <!-- Retrieved RAG Knowledge -->
            <div id="retrieval-box" class="hidden">
              <h4 class="text-xs font-bold text-oliveDark dark:text-white uppercase tracking-wider flex items-center gap-1.5 mb-1.5">
                <i data-lucide="database" class="w-4 h-4 text-blue-600 dark:text-cyan-400"></i>
                <span>RAG Knowledge Retrieved (RetrievalAgent)</span>
              </h4>
              <pre id="retrieval-content" class="p-3 rounded-xl bg-blue-50 dark:bg-cyan-950/30 border border-blue-200 dark:border-cyan-900 text-xs font-mono text-blue-900 dark:text-cyan-200 max-h-36 overflow-y-auto custom-scrollbar"></pre>
            </div>

            <!-- Error Analysis Diagnostic -->
            <div id="error-analysis-box" class="hidden">
              <h4 class="text-xs font-bold text-rose-600 dark:text-rose-400 uppercase tracking-wider flex items-center gap-1.5 mb-1.5">
                <i data-lucide="alert-octagon" class="w-4 h-4"></i>
                <span>Diagnostic Trace (ErrorAnalysisAgent)</span>
              </h4>
              <pre id="error-analysis-content" class="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-xs font-mono text-rose-800 dark:text-rose-200 max-h-36 overflow-y-auto custom-scrollbar"></pre>
            </div>
          </div>

          <!-- Tab 5: Code Review -->
          <div id="tab-content-review" class="p-6 flex-1 hidden space-y-4 bg-white dark:bg-gray-900">
            <div class="flex items-center gap-4 p-4 rounded-xl editorial-panel-sage border border-sageBorder dark:border-gray-800">
              <div class="text-3xl font-serif font-bold text-oliveDark dark:text-emerald-400" id="review-score-gauge">0.0</div>
              <div>
                <div class="text-xs font-bold text-oliveDark dark:text-white">Quality Score Assessment</div>
                <div class="text-[11px] text-olive/80 dark:text-gray-400">Evaluates algorithmic complexity, syntax standards, edge case handling, and robustness.</div>
              </div>
            </div>

            <div>
              <div class="text-xs font-semibold text-oliveDark dark:text-gray-200 mb-2">Reviewer Recommendations & Analysis:</div>
              <ul class="space-y-2 text-xs text-mossText dark:text-gray-300" id="review-suggestions-list">
                <li class="text-olive/70 dark:text-gray-500 italic">No review suggestions yet.</li>
              </ul>
            </div>
          </div>

          <!-- Tab 6: RL Agent Trace & State Feature Visualizer -->
          <div id="tab-content-trace" class="p-6 flex-1 hidden space-y-5 bg-white dark:bg-gray-900">
            <!-- 12-Dim RL Observation Feature Vector -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-oliveDark dark:text-white uppercase tracking-wider flex items-center gap-1.5">
                  <i data-lucide="gauge" class="w-4 h-4 text-olive dark:text-emerald-400"></i>
                  12-Dimensional State Feature Vector
                </span>
                <span class="text-[10px] text-olive/70 dark:text-gray-400 font-mono">Box(shape=(12,), [0.0 - 1.0])</span>
              </div>

              <div class="grid grid-cols-2 sm:grid-cols-3 gap-2" id="rl-features-grid">
                <!-- Dynamically populated feature bars -->
              </div>
            </div>

            <!-- 8 Action Space Masking Status -->
            <div class="pt-2 border-t border-sageBorder/60 dark:border-gray-800">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-oliveDark dark:text-white uppercase tracking-wider flex items-center gap-1.5">
                  <i data-lucide="shield" class="w-4 h-4 text-olive dark:text-emerald-400"></i>
                  Action Space Masking Validity (8 Actions)
                </span>
                <span class="text-[10px] text-olive/70 dark:text-gray-400">Invalid actions strictly prohibited</span>
              </div>
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono" id="action-masks-grid">
                <!-- Dynamically populated action mask chips -->
              </div>
            </div>

            <!-- Sequential Decision Timeline -->
            <div class="pt-2 border-t border-sageBorder/60 dark:border-gray-800">
              <div class="text-xs text-oliveDark dark:text-gray-300 mb-2.5 font-bold uppercase tracking-wider flex items-center gap-1.5">
                <i data-lucide="git-commit" class="w-4 h-4 text-olive dark:text-emerald-400"></i>
                Sequential Decision Timeline:
              </div>
              <div class="space-y-2 max-h-52 overflow-y-auto custom-scrollbar" id="trace-timeline">
                <div class="text-xs text-olive/70 dark:text-gray-500 italic">No steps recorded yet.</div>
              </div>
            </div>

          </div>

        </div>

      </div>
    </main>

  </div>

  <!-- Problem Benchmark Library Modal -->
  <div id="problem-modal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="editorial-panel rounded-2xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
      
      <!-- Modal Header -->
      <div class="p-5 border-b border-sageBorder dark:border-gray-800 flex items-center justify-between bg-sageSurface/50 dark:bg-gray-900/60">
        <div>
          <h3 class="font-serif text-xl font-bold text-oliveDark dark:text-white flex items-center gap-2">
            <i data-lucide="library" class="w-5 h-5 text-olive dark:text-emerald-400"></i>
            Benchmark Problem Library
          </h3>
          <p class="text-xs text-olive/80 dark:text-gray-400 mt-0.5">Explore curated coding challenges across multiple algorithmic paradigms.</p>
        </div>
        <button onclick="closeProblemModal()" class="p-2 rounded-xl text-oliveDark dark:text-gray-400 hover:bg-sageBorder dark:hover:bg-gray-800 transition">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <!-- Search & Category Filters -->
      <div class="p-4 border-b border-sageBorder/60 dark:border-gray-800 bg-white dark:bg-gray-900 space-y-3">
        <div class="flex gap-2">
          <div class="relative flex-1">
            <i data-lucide="search" class="w-4 h-4 absolute left-3 top-3 text-olive/40 dark:text-gray-500"></i>
            <input id="modal-search-input" type="text" oninput="filterProblems()" 
              class="w-full bg-[#FAFCF9] dark:bg-gray-800 border border-sageBorder dark:border-gray-700 rounded-xl pl-9 pr-3.5 py-2 text-xs text-mossText dark:text-gray-100 placeholder-olive/40 dark:placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              placeholder="Search problems by name, keyword or category...">
          </div>
          
          <select id="modal-difficulty-filter" onchange="filterProblems()" 
            class="bg-[#FAFCF9] dark:bg-gray-800 border border-sageBorder dark:border-gray-700 rounded-xl px-3 py-2 text-xs text-mossText dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-emerald-500">
            <option value="All">All Difficulties</option>
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
          </select>
        </div>

        <!-- Category Pills -->
        <div class="flex flex-wrap gap-1.5" id="modal-category-chips">
          <button onclick="setCategoryFilter('All')" class="category-chip px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-olive dark:bg-emerald-600 text-white shadow-sm transition">All</button>
          <button onclick="setCategoryFilter('String')" class="category-chip px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-sageSurface dark:bg-gray-800 text-oliveDark dark:text-gray-300 hover:bg-sageBorder dark:hover:bg-gray-700 transition">String</button>
          <button onclick="setCategoryFilter('Array')" class="category-chip px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-sageSurface dark:bg-gray-800 text-oliveDark dark:text-gray-300 hover:bg-sageBorder dark:hover:bg-gray-700 transition">Array</button>
          <button onclick="setCategoryFilter('Math')" class="category-chip px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-sageSurface dark:bg-gray-800 text-oliveDark dark:text-gray-300 hover:bg-sageBorder dark:hover:bg-gray-700 transition">Math</button>
          <button onclick="setCategoryFilter('Tree')" class="category-chip px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-sageSurface dark:bg-gray-800 text-oliveDark dark:text-gray-300 hover:bg-sageBorder dark:hover:bg-gray-700 transition">Tree</button>
          <button onclick="setCategoryFilter('Dynamic Programming')" class="category-chip px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-sageSurface dark:bg-gray-800 text-oliveDark dark:text-gray-300 hover:bg-sageBorder dark:hover:bg-gray-700 transition">DP</button>
        </div>
      </div>

      <!-- Problem Cards List -->
      <div class="p-5 flex-1 overflow-y-auto custom-scrollbar bg-sageSurface/30 dark:bg-gray-950 space-y-2.5" id="modal-problems-list">
        <div class="text-center py-10 text-xs text-olive/60 dark:text-gray-400">
          <i data-lucide="loader-2" class="w-6 h-6 animate-spin mx-auto mb-2 text-olive dark:text-emerald-400"></i>
          <span>Loading problem benchmark repository...</span>
        </div>
      </div>

    </div>
  </div>

  <!-- Toast Notification Container -->
  <div id="toast-container" class="fixed bottom-5 right-5 z-50 space-y-2 pointer-events-none"></div>

  <!-- Main JavaScript Engine -->
  <script>
    // State
    let currentView = 'landing';
    let currentMode = 'rl';
    let latestGeneratedCode = '';
    let isExecuting = false;
    let allProblems = [];
    let selectedCategory = 'All';
    let isEditingCode = false;

    // Feature and Action Constants
    const FEATURE_NAMES = [
      "Requirements Analyzed", "Plan Formulated", "Context Retrieved", 
      "Code Synthesized", "Code Reviewed", "Quality Score", 
      "Tests Present", "All Tests Passed", "Pass Ratio", 
      "Error Diagnostic Done", "Step Progress", "Recent Self-Repair"
    ];

    const ACTION_NAMES = [
      "PlanningAgent", "RetrievalAgent", "CodingAgent", 
      "ReviewAgent", "TestingAgent", "ErrorAnalysisAgent", 
      "SelfRepairAgent", "Terminate"
    ];

    // Quick Templates
    const templates = {
      is_palindrome: {
        req: "Write a python function `is_palindrome(s: str) -> bool` that checks if a string is a palindrome, ignoring casing and non-alphanumeric characters.",
        tests: "assert is_palindrome('A man, a plan, a canal: Panama') == True\\nassert is_palindrome('race a car') == False\\nassert is_palindrome('') == True\\nassert is_palindrome('0P') == False",
        playground: 'is_palindrome("Never odd or even")'
      },
      two_sum: {
        req: "Write a python function `two_sum(nums: list[int], target: int) -> list[int]` that returns the 0-based indices of two numbers that add up to target.",
        tests: "assert two_sum([2, 7, 11, 15], 9) == [0, 1]\\nassert two_sum([3, 2, 4], 6) == [1, 2]\\nassert two_sum([3, 3], 6) == [0, 1]",
        playground: 'two_sum([2, 7, 11, 15], 9)'
      },
      is_prime: {
        req: "Write a python function `is_prime(n: int) -> bool` that checks if an integer n is prime in O(sqrt(n)) time.",
        tests: "assert is_prime(2) == True\\nassert is_prime(7) == True\\nassert is_prime(10) == False\\nassert is_prime(1) == False\\nassert is_prime(17) == True",
        playground: 'is_prime(97)'
      },
      longest_consecutive: {
        req: "Write a python function `longest_consecutive(nums: list[int]) -> int` that finds the length of longest consecutive elements sequence in O(n) time.",
        tests: "assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4\\nassert longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9\\nassert longest_consecutive([]) == 0",
        playground: 'longest_consecutive([100, 4, 200, 1, 3, 2])'
      },
      sum_of_digits: {
        req: "Write a python function `sum_of_digits(n: int) -> int` that calculates the sum of digits of a given number.",
        tests: "assert sum_of_digits(123) == 6\\nassert sum_of_digits(0) == 0\\nassert sum_of_digits(999) == 27\\nassert sum_of_digits(-45) == 9",
        playground: 'sum_of_digits(98765)'
      }
    };

    // View Navigation with View Transitions API
    function navigateTo(viewName) {
      if (currentView === viewName) return;
      currentView = viewName;

      function updateDOM() {
        const landing = document.getElementById('view-landing');
        const studio = document.getElementById('view-studio');
        const navLanding = document.getElementById('nav-btn-landing');
        const navStudio = document.getElementById('nav-btn-studio');
        const headerCta = document.getElementById('header-cta-btn');

        if (viewName === 'landing') {
          studio.classList.add('hidden');
          landing.classList.remove('hidden');
          window.location.hash = 'home';
          
          if (navLanding) navLanding.className = "px-3.5 py-1.5 rounded-full transition text-oliveDark dark:text-white bg-sageSurface dark:bg-gray-800 shadow-sm border border-sageBorder dark:border-gray-700";
          if (navStudio) navStudio.className = "px-3.5 py-1.5 rounded-full transition text-olive/70 dark:text-gray-400 hover:text-oliveDark dark:hover:text-white";
          if (headerCta) headerCta.classList.remove('hidden');
        } else {
          landing.classList.add('hidden');
          studio.classList.remove('hidden');
          window.location.hash = 'studio';

          if (navStudio) navStudio.className = "px-3.5 py-1.5 rounded-full transition text-oliveDark dark:text-white bg-sageSurface dark:bg-gray-800 shadow-sm border border-sageBorder dark:border-gray-700";
          if (navLanding) navLanding.className = "px-3.5 py-1.5 rounded-full transition text-olive/70 dark:text-gray-400 hover:text-oliveDark dark:hover:text-white";
          if (headerCta) headerCta.classList.add('hidden');
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
        lucide.createIcons();
      }

      if (document.startViewTransition) {
        document.startViewTransition(updateDOM);
      } else {
        updateDOM();
      }
    }

    function scrollToArchitecture() {
      if (currentView !== 'landing') {
        navigateTo('landing');
        setTimeout(() => {
          document.getElementById('architecture-section')?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      } else {
        document.getElementById('architecture-section')?.scrollIntoView({ behavior: 'smooth' });
      }
    }

    function launchQuickProblem(key) {
      setTemplate(key);
      navigateTo('studio');
      showToast(`Ready to synthesize: ${key}`, "info");
    }

    // Hash change handler for browser back/forward
    window.addEventListener('hashchange', () => {
      const hash = window.location.hash.replace('#', '');
      if (hash === 'studio') {
        navigateTo('studio');
      } else {
        navigateTo('landing');
      }
    });

    // Theme Management
    function applyTheme(theme) {
      const root = document.documentElement;
      const icon = document.getElementById('theme-icon');
      if (theme === 'dark') {
        root.classList.add('dark');
        if (icon) icon.setAttribute('data-lucide', 'sun');
        localStorage.setItem('theme', 'dark');
      } else {
        root.classList.remove('dark');
        if (icon) icon.setAttribute('data-lucide', 'moon');
        localStorage.setItem('theme', 'light');
      }
      lucide.createIcons();
    }

    function toggleTheme() {
      const isDark = document.documentElement.classList.contains('dark');
      applyTheme(isDark ? 'light' : 'dark');
    }

    // Toast Alerts
    function showToast(msg, type = 'info') {
      const container = document.getElementById('toast-container');
      const toast = document.createElement('div');
      const colors = {
        success: 'bg-emerald-600 text-white',
        error: 'bg-rose-600 text-white',
        warning: 'bg-amber-600 text-white',
        info: 'bg-olive dark:bg-gray-800 text-white'
      };
      toast.className = `px-4 py-2.5 rounded-xl shadow-xl text-xs font-medium flex items-center gap-2 transform transition-all duration-300 pointer-events-auto ${colors[type] || colors.info}`;
      toast.innerHTML = `<span>${msg}</span>`;
      container.appendChild(toast);
      setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
      }, 3200);
    }

    // Mode Selector
    function setMode(mode) {
      currentMode = mode;
      const rlBtn = document.getElementById('mode-rl');
      const baseBtn = document.getElementById('mode-baseline');
      if (mode === 'rl') {
        rlBtn.className = "px-3 py-1 rounded-full font-semibold transition bg-olive dark:bg-emerald-600 text-white shadow-sm";
        baseBtn.className = "px-3 py-1 rounded-full font-medium transition text-mossText dark:text-gray-400 hover:text-oliveDark dark:hover:text-white";
      } else {
        baseBtn.className = "px-3 py-1 rounded-full font-semibold transition bg-olive dark:bg-emerald-600 text-white shadow-sm";
        rlBtn.className = "px-3 py-1 rounded-full font-medium transition text-mossText dark:text-gray-400 hover:text-oliveDark dark:hover:text-white";
      }
      showToast(`Switched mode to ${mode === 'rl' ? 'RL Orchestrator' : 'Deterministic Baseline'}`, "info");
    }

    // Set Template
    function setTemplate(key) {
      if (templates[key]) {
        document.getElementById('req-input').value = templates[key].req;
        document.getElementById('custom-tests-input').value = templates[key].tests;
        document.getElementById('playground-input').value = templates[key].playground || '';
      }
    }

    // Tab Switcher
    function switchTab(tab) {
      const tabs = ['code', 'playground', 'tests', 'plan', 'review', 'trace'];
      tabs.forEach(t => {
        const btn = document.getElementById(`tab-btn-${t}`);
        const content = document.getElementById(`tab-content-${t}`);
        if (t === tab) {
          btn.className = "px-3 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-olive dark:border-emerald-400 text-oliveDark dark:text-white flex items-center gap-1.5 transition";
          content.classList.remove('hidden');
        } else {
          btn.className = "px-3 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-olive/70 dark:text-gray-400 hover:text-oliveDark dark:hover:text-white flex items-center gap-1.5 transition";
          content.classList.add('hidden');
        }
      });
      lucide.createIcons();
    }

    // Copy Code Helper
    function copyCode() {
      const code = latestGeneratedCode || document.getElementById('code-display').innerText;
      navigator.clipboard.writeText(code);
      const copyBtn = document.getElementById('copy-btn');
      copyBtn.innerHTML = '<i data-lucide="check" class="w-3 h-3 text-emerald-500"></i><span class="text-emerald-500 font-bold">Copied!</span>';
      lucide.createIcons();
      showToast("Code copied to clipboard!", "success");
      setTimeout(() => {
        copyBtn.innerHTML = '<i data-lucide="copy" class="w-3 h-3 text-olive dark:text-emerald-400"></i><span>Copy</span>';
        lucide.createIcons();
      }, 2000);
    }

    // Editable Code Toggle
    function toggleEditCode() {
      isEditingCode = !isEditingCode;
      const pre = document.getElementById('code-pre-container');
      const editor = document.getElementById('code-editor-container');
      const textarea = document.getElementById('code-editable-textarea');
      const label = document.getElementById('edit-code-label');

      if (isEditingCode) {
        pre.classList.add('hidden');
        editor.classList.remove('hidden');
        textarea.value = latestGeneratedCode || document.getElementById('code-display').innerText;
        label.textContent = "View Highlighted";
      } else {
        editor.classList.add('hidden');
        pre.classList.remove('hidden');
        label.textContent = "Edit in Sandbox";
      }
      lucide.createIcons();
    }

    async function runEditedCodeInSandbox() {
      const editedCode = document.getElementById('code-editable-textarea').value.trim();
      if (!editedCode) return;
      latestGeneratedCode = editedCode;
      document.getElementById('code-display').textContent = editedCode;
      hljs.highlightElement(document.getElementById('code-display'));
      toggleEditCode();
      showToast("Updated code applied to workspace", "info");
      switchTab('playground');
    }

    // Agent Node Highlighting
    function resetAgentHighlights() {
      document.querySelectorAll('.agent-node').forEach(node => {
        node.classList.remove('agent-running', 'agent-done');
        const badge = node.querySelector('.status-badge');
        if (badge) {
          badge.textContent = "IDLE";
          badge.className = "status-badge text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-white/70 dark:bg-gray-700 text-oliveDark dark:text-gray-300";
        }
      });
      const statusText = document.getElementById('live-agent-status');
      if (statusText) {
        statusText.textContent = "Pool Idle";
        statusText.className = "text-[10px] uppercase font-bold tracking-widest px-2.5 py-0.5 rounded-full bg-sageSurface dark:bg-gray-800 text-olive dark:text-emerald-400 border border-sageBorder dark:border-gray-700";
      }
    }

    function highlightAgent(agentName, state = 'running') {
      const node = document.getElementById(`node-${agentName}`);
      const statusText = document.getElementById('live-agent-status');
      if (node) {
        const badge = node.querySelector('.status-badge');
        if (state === 'running') {
          node.classList.remove('agent-done');
          node.classList.add('agent-running');
          if (badge) {
            badge.textContent = "ACTIVE";
            badge.className = "status-badge text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-emerald-500 text-white font-bold animate-pulse";
          }
          if (statusText) {
            statusText.textContent = `${agentName} Active`;
            statusText.className = "text-[10px] uppercase font-bold tracking-widest px-2.5 py-0.5 rounded-full bg-emerald-500 text-white border border-emerald-400 animate-pulse";
          }
        } else {
          node.classList.remove('agent-running');
          node.classList.add('agent-done');
          if (badge) {
            badge.textContent = "DONE";
            badge.className = "status-badge text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-emerald-700 text-white font-semibold";
          }
        }
      }
    }

    // RL State & Feature Vector Visualizer
    function renderRLFeatures(features) {
      const container = document.getElementById('rl-features-grid');
      if (!container || !features) return;
      container.innerHTML = '';
      features.forEach((val, idx) => {
        const name = FEATURE_NAMES[idx] || `Feature ${idx}`;
        const pct = Math.min(100, Math.max(0, Math.round(val * 100)));
        const card = document.createElement('div');
        card.className = "p-2 rounded-lg bg-sageSurface/50 dark:bg-gray-800/60 border border-sageBorder dark:border-gray-700";
        card.innerHTML = `
          <div class="flex justify-between items-center text-[10px] mb-1">
            <span class="truncate font-medium text-oliveDark dark:text-gray-200" title="${name}">${name}</span>
            <span class="font-mono font-bold text-olive dark:text-emerald-400 ml-1">${val.toFixed(2)}</span>
          </div>
          <div class="w-full h-1.5 rounded-full bg-sageBorder dark:bg-gray-700 overflow-hidden">
            <div class="h-full bg-emerald-500 transition-all duration-300" style="width: ${pct}%"></div>
          </div>
        `;
        container.appendChild(card);
      });
    }

    // Action Masking Visualizer
    function renderActionMasks(masks, chosenAction = null) {
      const container = document.getElementById('action-masks-grid');
      if (!container || !masks) return;
      container.innerHTML = '';
      ACTION_NAMES.forEach((action, idx) => {
        const isValid = masks[idx];
        const isChosen = (chosenAction === idx || chosenAction === action);
        const chip = document.createElement('div');
        chip.className = `p-2 rounded-lg border text-center transition ${isValid ? (isChosen ? 'bg-emerald-600 text-white border-emerald-400 font-bold shadow-md ring-2 ring-emerald-400' : 'bg-sageSurface dark:bg-gray-800 text-oliveDark dark:text-gray-200 border-sageBorder dark:border-gray-700') : 'bg-gray-100 dark:bg-gray-900/50 text-gray-400 border-gray-200 dark:border-gray-800 opacity-40 line-through'}`;
        chip.innerHTML = `
          <div class="text-[10px] truncate">${action}</div>
          <div class="text-[9px] uppercase tracking-wider font-semibold mt-0.5">${isValid ? (isChosen ? 'DISPATCHED' : 'VALID') : 'MASKED'}</div>
        `;
        container.appendChild(chip);
      });
    }

    // Clear Previous Results
    function clearPreviousResults() {
      document.getElementById('metric-status').textContent = "Running...";
      document.getElementById('metric-tests-ratio').textContent = "-- / --";
      document.getElementById('metric-score').textContent = "-- / 1.0";
      document.getElementById('metric-reward').textContent = "--";
      document.getElementById('trace-timeline').innerHTML = '';
      document.getElementById('test-cases-list').innerHTML = '<div class="text-xs text-olive/60 dark:text-gray-400 italic p-3">Executing test suite in isolated sandbox...</div>';
      document.getElementById('code-display').textContent = "# Synthesizing code through multi-agent orchestration...";
      hljs.highlightElement(document.getElementById('code-display'));
    }

    // Streaming Event Listener
    function handleStreamEvent(data) {
      if (data.event === 'started') {
        showToast(`Pipeline started in ${data.mode.toUpperCase()} mode`, "info");
      } 
      else if (data.event === 'step_start') {
        highlightAgent(data.agent, 'running');
        if (data.observation_vector) {
          renderRLFeatures(data.observation_vector);
        }
        if (data.action_mask) {
          renderActionMasks(data.action_mask, data.action_idx);
        }
      } 
      else if (data.event === 'step_done') {
        highlightAgent(data.agent, 'done');
        
        // Append to sequential timeline
        const timeline = document.getElementById('trace-timeline');
        const card = document.createElement('div');
        card.className = "p-3 rounded-xl bg-sageSurface/50 dark:bg-gray-800/60 border border-sageBorder dark:border-gray-700 flex items-center justify-between";
        card.innerHTML = `
          <div class="flex items-center gap-3">
            <span class="w-5 h-5 rounded-full bg-olive dark:bg-emerald-600 text-white font-bold text-[10px] flex items-center justify-center shadow-sm">${data.step}</span>
            <div>
              <div class="font-semibold text-xs text-oliveDark dark:text-white">${data.agent}</div>
              <div class="text-[10px] text-olive/70 dark:text-gray-400">${data.summary}</div>
            </div>
          </div>
          <span class="text-xs font-mono font-semibold ${data.reward >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600'}">${data.reward >= 0 ? '+' : ''}${data.reward}</span>
        `;
        timeline.appendChild(card);

        if (data.intermediate) {
          if (data.intermediate.code) {
            latestGeneratedCode = data.intermediate.code;
            document.getElementById('code-display').textContent = data.intermediate.code;
            hljs.highlightElement(document.getElementById('code-display'));
          }
          if (data.intermediate.total_reward !== undefined) {
            document.getElementById('metric-reward').innerHTML = `<span class="text-olive dark:text-emerald-400 font-bold">${data.intermediate.total_reward > 0 ? '+' : ''}${data.intermediate.total_reward}</span>`;
          }
          if (data.intermediate.structured_requirement) {
            renderSpec(data.intermediate.structured_requirement);
          }
          if (data.intermediate.plan) {
            renderPlan(data.intermediate.plan);
          }
        }
      } 
      else if (data.event === 'complete') {
        latestGeneratedCode = data.data.code;
        renderResults(data.data);
        if (data.data.test_passed) {
          confetti({
            particleCount: 90,
            spread: 75,
            origin: { y: 0.6 },
            colors: ['#10B981', '#06B6D4', '#8B5CF6', '#F59E0B']
          });
          showToast("Execution completed successfully! All unit tests passed.", "success");
        } else {
          showToast(`Execution finished with failures: ${data.data.error_type || 'Test failure'}`, "warning");
        }
      } 
      else if (data.event === 'error') {
        showToast(`Server execution error: ${data.error}`, "error");
      }
    }

    // Execute Pipeline via Real-Time SSE Stream
    async function executePipelineStream() {
      const reqText = document.getElementById('req-input').value.trim();
      const testCode = document.getElementById('custom-tests-input').value.trim();
      const runBtn = document.getElementById('run-btn');

      if (!reqText) {
        showToast("Please enter a software requirement!", "warning");
        return;
      }

      isExecuting = true;
      runBtn.disabled = true;
      runBtn.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Streaming Orchestrator...</span>';
      lucide.createIcons();
      resetAgentHighlights();
      clearPreviousResults();

      try {
        const response = await fetch('/api/run/stream', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            requirement: reqText,
            test_code: testCode,
            mode: currentMode
          })
        });

        if (!response.ok) throw new Error(await response.text());

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\\n\\n");
          buffer = lines.pop();

          for (const block of lines) {
            const line = block.trim();
            if (!line.startsWith("data: ")) continue;
            const jsonStr = line.replace(/^data:\\s*/, "");
            try {
              const payload = JSON.parse(jsonStr);
              handleStreamEvent(payload);
            } catch (e) {
              console.error("Failed to parse SSE payload", jsonStr, e);
            }
          }
        }
      } catch (err) {
        console.warn("SSE Streaming failed, falling back to synchronous /api/run:", err);
        showToast("Streaming disconnected, switching to direct execution...", "info");
        await executePipelineFallback(reqText, testCode);
      } finally {
        isExecuting = false;
        runBtn.disabled = false;
        runBtn.innerHTML = '<i data-lucide="play" class="w-3.5 h-3.5 fill-current"></i><span>Execute Multi-Agent System</span>';
        const statusText = document.getElementById('live-agent-status');
        if (statusText) {
          statusText.textContent = "Execution Finished";
          statusText.className = "text-[10px] uppercase font-bold tracking-widest px-2.5 py-0.5 rounded-full bg-sageSurface dark:bg-gray-800 text-olive dark:text-emerald-400 border border-sageBorder dark:border-gray-700";
        }
        lucide.createIcons();
      }
    }

    // Fallback Execution
    async function executePipelineFallback(reqText, testCode) {
      try {
        const response = await fetch('/api/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            requirement: reqText,
            test_code: testCode,
            mode: currentMode
          })
        });

        if (!response.ok) throw new Error(await response.text());
        const data = await response.json();
        latestGeneratedCode = data.code;
        renderResults(data);
      } catch (e) {
        showToast(`Execution Error: ${e.message}`, "error");
      }
    }

    // Render Spec Helper
    function renderSpec(spec) {
      if (!spec) return;
      const constraintsList = document.getElementById('spec-constraints');
      const edgeCasesList = document.getElementById('spec-edge-cases');
      
      constraintsList.innerHTML = '';
      if (spec.constraints && spec.constraints.length > 0) {
        spec.constraints.forEach(c => {
          const li = document.createElement('li');
          li.className = "flex items-center gap-1.5";
          li.innerHTML = `<i data-lucide="chevron-right" class="w-3 h-3 text-olive dark:text-emerald-400 shrink-0"></i><span>${c}</span>`;
          constraintsList.appendChild(li);
        });
      } else {
        constraintsList.innerHTML = '<li class="italic text-olive/60 dark:text-gray-500">No explicit constraints parsed.</li>';
      }

      edgeCasesList.innerHTML = '';
      if (spec.edge_cases && spec.edge_cases.length > 0) {
        spec.edge_cases.forEach(e => {
          const li = document.createElement('li');
          li.className = "flex items-center gap-1.5";
          li.innerHTML = `<i data-lucide="alert-circle" class="w-3 h-3 text-amber-600 dark:text-amber-400 shrink-0"></i><span>${e}</span>`;
          edgeCasesList.appendChild(li);
        });
      } else {
        edgeCasesList.innerHTML = '<li class="italic text-olive/60 dark:text-gray-500">Standard test coverage applies.</li>';
      }
      lucide.createIcons();
    }

    // Render Plan Helper
    function renderPlan(plan) {
      const planList = document.getElementById('plan-list');
      if (!planList || !plan) return;
      planList.innerHTML = '';
      if (Array.isArray(plan) && plan.length > 0) {
        plan.forEach((step, idx) => {
          const item = document.createElement('div');
          item.className = "p-3 rounded-xl bg-sageSurface/50 dark:bg-gray-800/60 border border-sageBorder dark:border-gray-700 flex items-start gap-2.5 text-xs text-mossText dark:text-gray-200";
          item.innerHTML = `
            <span class="w-5 h-5 rounded-full bg-amber-600 dark:bg-amber-500 text-white font-bold text-[10px] flex items-center justify-center shrink-0 mt-0.5">${idx + 1}</span>
            <div class="leading-relaxed">${step}</div>
          `;
          planList.appendChild(item);
        });
      } else {
        planList.innerHTML = '<div class="text-xs text-olive/60 dark:text-gray-500 italic p-3">No modular roadmap generated.</div>';
      }
    }

    // Render Full Results
    function renderResults(data) {
      // 1. Code Display
      const codeDisplay = document.getElementById('code-display');
      codeDisplay.textContent = data.code || "# No code synthesized.";
      hljs.highlightElement(codeDisplay);

      // 2. Header Metrics
      const metricStatus = document.getElementById('metric-status');
      if (data.test_passed) {
        metricStatus.innerHTML = '<span class="text-emerald-600 dark:text-emerald-400 font-bold">ALL PASSED</span>';
      } else {
        metricStatus.innerHTML = `<span class="text-rose-600 font-bold">FAILED (${data.error_type || 'Error'})</span>`;
      }

      document.getElementById('metric-tests-ratio').innerHTML = `<span class="${data.test_passed ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600'} font-bold">${data.passed_tests} / ${data.total_tests}</span>`;
      document.getElementById('metric-score').innerHTML = `<span class="text-emerald-600 dark:text-emerald-400 font-bold">${data.review_score.toFixed(2)} / 1.0</span>`;
      document.getElementById('metric-reward').innerHTML = `<span class="text-oliveDark dark:text-gray-100 font-bold">${data.total_reward > 0 ? '+' : ''}${data.total_reward}</span>`;

      // 3. Tests Tab Banner
      const testBanner = document.getElementById('test-banner');
      const testTitle = document.getElementById('test-summary-title');
      const testDesc = document.getElementById('test-summary-desc');
      const testIcon = document.getElementById('test-icon');

      if (data.test_passed) {
        testBanner.className = "p-4 rounded-xl border border-emerald-300 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-950/30 flex items-center gap-3";
        testIcon.className = "w-9 h-9 rounded-full bg-white dark:bg-gray-800 text-emerald-600 dark:text-emerald-400 flex items-center justify-center border border-emerald-200 dark:border-emerald-700 shadow-sm";
        testIcon.innerHTML = '<i data-lucide="check-circle" class="w-5 h-5"></i>';
        testTitle.textContent = `All ${data.total_tests} Test Cases Passed`;
        testDesc.textContent = `100% of assertions passed in the isolated Python sandbox.`;
      } else {
        testBanner.className = "p-4 rounded-xl border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/30 flex items-center gap-3";
        testIcon.className = "w-9 h-9 rounded-full bg-rose-100 dark:bg-rose-900 text-rose-700 dark:text-rose-300 flex items-center justify-center border border-rose-200 shadow-sm";
        testIcon.innerHTML = '<i data-lucide="alert-triangle" class="w-5 h-5"></i>';
        testTitle.textContent = `Tests Failed (${data.error_type || 'Execution Error'})`;
        testDesc.textContent = `${data.failed_tests} out of ${data.total_tests} assertions failed during sandbox execution.`;
      }

      // 4. Test Assertions List
      const testCasesList = document.getElementById('test-cases-list');
      const testCountBadge = document.getElementById('test-count-badge');
      testCasesList.innerHTML = '';
      testCountBadge.textContent = `${data.passed_tests}/${data.total_tests} passed`;

      if (data.test_details && data.test_details.length > 0) {
        data.test_details.forEach(t => {
          const item = document.createElement('div');
          item.className = `p-3 rounded-xl border flex items-center justify-between gap-3 text-xs ${t.passed ? 'bg-sageSurface/60 dark:bg-gray-800/60 border-sageBorder dark:border-gray-700' : 'bg-red-50/70 dark:bg-rose-950/40 border-red-200 dark:border-rose-900'}`;
          item.innerHTML = `
            <div class="flex items-center gap-2.5 min-w-0">
              <span class="p-1 rounded-full ${t.passed ? 'bg-white dark:bg-gray-800 text-emerald-600 dark:text-emerald-400 border border-sageBorder dark:border-gray-700' : 'bg-red-100 dark:bg-rose-900 text-red-700 dark:text-rose-300 border border-red-200'} shrink-0">
                <i data-lucide="${t.passed ? 'check' : 'x'}" class="w-3.5 h-3.5"></i>
              </span>
              <span class="font-mono text-xs ${t.passed ? 'text-oliveDark dark:text-gray-200' : 'text-red-700 dark:text-rose-400'} truncate">${t.assertion}</span>
            </div>
            <span class="text-[10px] uppercase tracking-wider font-bold px-2.5 py-0.5 rounded-full ${t.passed ? 'bg-white dark:bg-gray-800 text-emerald-600 dark:text-emerald-400 border border-sageBorder dark:border-gray-700' : 'bg-red-100 dark:bg-rose-900 text-red-700 dark:text-rose-300 border border-red-200'} shrink-0">
              ${t.passed ? 'Passed' : 'Failed'}
            </span>
          `;
          if (!t.passed && t.error) {
            const errDiv = document.createElement('div');
            errDiv.className = "text-[10px] text-red-700 dark:text-rose-400 font-mono mt-1 pl-7";
            errDiv.textContent = t.error;
            item.appendChild(errDiv);
          }
          testCasesList.appendChild(item);
        });
      } else {
        testCasesList.innerHTML = `<div class="text-xs text-olive/70 dark:text-gray-400 p-3 rounded-lg bg-[#FAFCF9] dark:bg-gray-800 border border-sageBorder dark:border-gray-700">No individual assertions parsed.</div>`;
      }

      // 5. Test Code & Stdout
      document.getElementById('test-code-display').textContent = data.test_code || "# No test code generated.";
      document.getElementById('test-stdout-display').textContent = data.test_stdout || "No stdout captured.";
      
      const stderrBox = document.getElementById('test-stderr-box');
      if (data.test_stderr) {
        stderrBox.classList.remove('hidden');
        document.getElementById('test-stderr-display').textContent = data.test_stderr;
      } else {
        stderrBox.classList.add('hidden');
      }

      // 6. Review Tab
      document.getElementById('review-score-gauge').textContent = `${data.review_score.toFixed(2)}`;
      const suggList = document.getElementById('review-suggestions-list');
      suggList.innerHTML = '';
      if (data.review_suggestions && data.review_suggestions.length > 0) {
        data.review_suggestions.forEach(sug => {
          const li = document.createElement('li');
          li.className = "flex items-start gap-2 bg-sageSurface/50 dark:bg-gray-800/60 p-3 rounded-lg border border-sageBorder dark:border-gray-700";
          li.innerHTML = `<i data-lucide="check" class="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5"></i><span>${sug}</span>`;
          suggList.appendChild(li);
        });
      } else {
        suggList.innerHTML = '<li class="text-emerald-600 dark:text-emerald-400 font-medium">Code satisfies all syntax standards, edge case handling, and complexity benchmarks.</li>';
      }

      // 7. Spec & Plan Tab
      if (data.structured_requirement) {
        renderSpec(data.structured_requirement);
      }
      if (data.plan) {
        renderPlan(data.plan);
      }
      if (data.retrieved_context) {
        document.getElementById('retrieval-box').classList.remove('hidden');
        document.getElementById('retrieval-content').textContent = data.retrieved_context;
      }
      if (data.error_analysis) {
        document.getElementById('error-analysis-box').classList.remove('hidden');
        document.getElementById('error-analysis-content').textContent = data.error_analysis;
      }

      // 8. RL State & Action Masks
      if (data.observation_vector) {
        renderRLFeatures(data.observation_vector);
      }
      if (data.action_mask) {
        renderActionMasks(data.action_mask);
      }

      // 9. Node highlights
      resetAgentHighlights();
      data.steps.forEach(s => highlightAgent(s.agent, 'done'));

      lucide.createIcons();
    }

    // Run Custom Input Live
    async function runCustomInputLive() {
      const code = latestGeneratedCode || document.getElementById('code-display').innerText;
      const customInput = document.getElementById('playground-input').value.trim();
      const btn = document.getElementById('playground-run-btn');

      const outVal = document.getElementById('playground-output-val');
      const errBox = document.getElementById('playground-err-box');
      const errVal = document.getElementById('playground-err-val');
      const stdoutBox = document.getElementById('playground-stdout-box');
      const stdoutVal = document.getElementById('playground-stdout-val');

      if (!customInput) {
        showToast("Please enter an input argument or function call!", "warning");
        return;
      }

      btn.disabled = true;
      btn.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Running...</span>';
      lucide.createIcons();
      errBox.classList.add('hidden');
      stdoutBox.classList.add('hidden');

      try {
        const response = await fetch('/api/run_custom_input', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code: code, custom_input: customInput })
        });

        if (!response.ok) throw new Error(await response.text());
        const res = await response.json();
        
        document.getElementById('playground-time').textContent = `${res.execution_time_ms} ms`;
        
        if (res.success) {
          outVal.textContent = res.return_value !== null ? res.return_value : "(Function returned None)";
          outVal.className = "p-3 rounded-lg bg-white dark:bg-gray-900 border border-emerald-500/40 text-sm font-mono font-bold text-emerald-600 dark:text-emerald-400";
        } else {
          outVal.textContent = "Execution Failed";
          outVal.className = "p-3 rounded-lg bg-red-50 dark:bg-rose-950/40 border border-red-200 dark:border-rose-900 text-sm font-mono font-bold text-red-700 dark:text-rose-400";
        }

        if (res.stdout) {
          stdoutBox.classList.remove('hidden');
          stdoutVal.textContent = res.stdout;
        }

        if (res.error || res.stderr) {
          errBox.classList.remove('hidden');
          errVal.textContent = res.error || res.stderr;
        }

      } catch (err) {
        outVal.textContent = "Execution Failed";
        outVal.className = "p-3 rounded-lg bg-red-50 dark:bg-rose-950/40 border border-red-200 dark:border-rose-900 text-sm font-mono font-bold text-red-700 dark:text-rose-400";
        errBox.classList.remove('hidden');
        errVal.textContent = err.message;
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="play" class="w-3.5 h-3.5 fill-current"></i><span>Run Input</span>';
        lucide.createIcons();
      }
    }

    // Problem Benchmark Modal Management
    function openProblemModal() {
      const modal = document.getElementById('problem-modal');
      modal.classList.remove('hidden');
      if (allProblems.length === 0) {
        loadBenchmarkProblems();
      } else {
        filterProblems();
      }
      lucide.createIcons();
    }

    function closeProblemModal() {
      document.getElementById('problem-modal').classList.add('hidden');
    }

    // Close modal on escape
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeProblemModal();
    });

    async function loadBenchmarkProblems() {
      try {
        const res = await fetch('/api/problems');
        if (!res.ok) throw new Error("Failed to load problems");
        allProblems = await res.json();
        document.getElementById('nav-lib-count').textContent = `${allProblems.length}+`;
        filterProblems();
      } catch (e) {
        document.getElementById('modal-problems-list').innerHTML = `
          <div class="text-center py-8 text-xs text-rose-500">
            Failed to load problems dataset. (${e.message})
          </div>
        `;
      }
    }

    function setCategoryFilter(cat) {
      selectedCategory = cat;
      document.querySelectorAll('#modal-category-chips button').forEach(btn => {
        if (btn.textContent.trim() === (cat === 'Dynamic Programming' ? 'DP' : cat)) {
          btn.className = "category-chip px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-olive dark:bg-emerald-600 text-white shadow-sm transition";
        } else {
          btn.className = "category-chip px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-sageSurface dark:bg-gray-800 text-oliveDark dark:text-gray-300 hover:bg-sageBorder dark:hover:bg-gray-700 transition";
        }
      });
      filterProblems();
    }

    function filterProblems() {
      const query = (document.getElementById('modal-search-input').value || '').toLowerCase().trim();
      const diff = document.getElementById('modal-difficulty-filter').value;
      const list = document.getElementById('modal-problems-list');

      const filtered = allProblems.filter(p => {
        const matchesCat = (selectedCategory === 'All') || (p.category === selectedCategory);
        const matchesDiff = (diff === 'All') || (p.difficulty === diff);
        const matchesQuery = !query || (p.name.toLowerCase().includes(query)) || (p.requirement.toLowerCase().includes(query)) || ((p.category || '').toLowerCase().includes(query));
        return matchesCat && matchesDiff && matchesQuery;
      });

      list.innerHTML = '';
      if (filtered.length === 0) {
        list.innerHTML = '<div class="text-center py-8 text-xs text-olive/60 dark:text-gray-400 italic">No matching benchmark problems found.</div>';
        return;
      }

      filtered.forEach(p => {
        const card = document.createElement('div');
        const diffColor = p.difficulty === 'Easy' ? 'text-emerald-600 bg-emerald-100 dark:bg-emerald-950 dark:text-emerald-400' : (p.difficulty === 'Medium' ? 'text-amber-700 bg-amber-100 dark:bg-amber-950 dark:text-amber-400' : 'text-rose-700 bg-rose-100 dark:bg-rose-950 dark:text-rose-400');
        
        card.className = "p-4 rounded-xl bg-white dark:bg-gray-900 border border-sageBorder dark:border-gray-800 hover:border-olive dark:hover:border-emerald-500 transition cursor-pointer shadow-sm group";
        card.innerHTML = `
          <div class="flex items-center justify-between gap-3 mb-1.5">
            <div class="flex items-center gap-2">
              <span class="font-bold text-xs text-oliveDark dark:text-white font-mono group-hover:text-olive dark:group-hover:text-emerald-400 transition">${p.name}</span>
              <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold ${diffColor}">${p.difficulty || 'Easy'}</span>
              <span class="text-[10px] px-2 py-0.5 rounded-full bg-sageSurface dark:bg-gray-800 text-oliveDark dark:text-gray-300 border border-sageBorder dark:border-gray-700 font-medium">${p.category || 'Algorithm'}</span>
            </div>
            <button class="btn-action text-[11px] font-semibold px-3 py-1 rounded-lg opacity-90 group-hover:opacity-100 transition shadow-sm">
              Load Problem
            </button>
          </div>
          <p class="text-xs text-mossText/80 dark:text-gray-400 line-clamp-2 leading-relaxed font-sans">${p.requirement}</p>
        `;
        card.onclick = () => selectProblem(p);
        list.appendChild(card);
      });
      lucide.createIcons();
    }

    function selectProblem(p) {
      document.getElementById('req-input').value = p.requirement;
      document.getElementById('custom-tests-input').value = p.test_code || '';
      
      if (p.function_name && p.test_cases && p.test_cases.length > 0) {
        const firstInput = p.test_cases[0].input;
        document.getElementById('playground-input').value = `${p.function_name}(${firstInput})`;
      } else if (p.function_name) {
        document.getElementById('playground-input').value = `${p.function_name}()`;
      }

      closeProblemModal();
      navigateTo('studio');
      showToast(`Loaded benchmark: ${p.name}`, "success");
    }

    // Load System Configuration on Startup
    async function loadSystemConfig() {
      try {
        const res = await fetch('/api/config');
        if (!res.ok) return;
        const cfg = await res.json();
        
        if (cfg.active_provider) {
          document.getElementById('backend-provider-name').textContent = cfg.active_provider;
        }
        if (cfg.total_benchmark_problems) {
          document.getElementById('nav-lib-count').textContent = `${cfg.total_benchmark_problems}+`;
        }
      } catch (e) {
        console.warn("Could not load backend config:", e);
      }
    }

    // Initialize Page
    document.addEventListener('DOMContentLoaded', () => {
      lucide.createIcons();
      hljs.highlightAll();
      loadSystemConfig();
      renderRLFeatures(new Array(12).fill(0.0));
      renderActionMasks(new Array(8).fill(true));

      // Handle Initial View based on hash
      const hash = window.location.hash.replace('#', '');
      if (hash === 'studio') {
        navigateTo('studio');
      } else {
        navigateTo('landing');
      }
    });
  </script>
</body>
</html>
'''

target_path = r"d:\Multi-Agent-Coding-System\frontend\static\index.html"
with open(target_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully wrote {len(html_content)} characters to {target_path}")
