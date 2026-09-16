/**
 * Synthetix - Multi-Agent Coding System
 * Hero Background Shader Animation
 * 
 * Recreates the visual aesthetic of Reference Image 2:
 * - Dark foundation (#050505 / #080808)
 * - Parallel diagonal slatted bands (flowing at ~-35°)
 * - Radiant energy ring / lens slicing across the bands
 * - Intersecting light: electric cyan, brilliant blue, white core, warm solar orange accents
 * - Asymmetric falloff: full intensity on right half, calm & dark on left for text readability
 * - WebGL with Canvas 2D fallback, performance-conscious, auto-pausing & reduced-motion aware
 */

(function () {
  'use strict';

  class HeroShaderBackground {
    constructor(canvasId = 'hero-shader-canvas') {
      this.canvasId = canvasId;
      this.canvas = null;
      this.gl = null;
      this.ctx2d = null;
      this.program = null;
      this.animationFrameId = null;
      this.startTime = performance.now();
      this.isVisible = true;
      this.isStudioActive = false;
      this.useFallback = false;
      this.pointer = { x: 0.7, y: 0.45, targetX: 0.7, targetY: 0.45 };
      this.dpr = Math.min(window.devicePixelRatio || 1, 2);

      this.init();
    }

    init() {
      this.canvas = document.getElementById(this.canvasId);
      if (!this.canvas) return;

      // Check prefers-reduced-motion
      this.reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      // Initialize WebGL
      try {
        const glOpts = { alpha: true, antialias: true, depth: false, stencil: false, powerPreference: 'high-performance' };
        this.gl = this.canvas.getContext('webgl', glOpts) || this.canvas.getContext('experimental-webgl', glOpts);
      } catch (e) {
        this.gl = null;
      }

      if (this.gl && !this.reducedMotion) {
        const success = this.setupWebGL();
        if (!success) {
          this.setup2DFallback();
        }
      } else {
        this.setup2DFallback();
      }

      this.bindEvents();
      this.resize();
      this.start();
    }

    setupWebGL() {
      const gl = this.gl;

      const vsSource = `
        attribute vec2 a_position;
        varying vec2 v_uv;
        void main() {
          v_uv = (a_position + 1.0) * 0.5;
          gl_Position = vec4(a_position, 0.0, 1.0);
        }
      `;

      // Fragment shader creating diagonal slats + radiant chromatic energy arc
      const fsSource = `
        precision highp float;
        varying vec2 v_uv;
        uniform vec2 u_resolution;
        uniform float u_time;
        uniform vec2 u_mouse;

        void main() {
          vec2 st = gl_FragCoord.xy / u_resolution.xy;
          float aspect = u_resolution.x / u_resolution.y;
          
          // Coordinate space centered towards right side (where IDE sits)
          vec2 p = st;
          p.x *= aspect;
          vec2 center = vec2(aspect * 0.72, 0.48);
          center += (u_mouse - 0.5) * 0.04;

          // Diagonal coordinate for slatted bands (~-35 degrees)
          float angle = -0.62;
          float cosA = cos(angle);
          float sinA = sin(angle);
          vec2 rotP = vec2(p.x * cosA - p.y * sinA, p.x * sinA + p.y * cosA);

          // Slat parameters
          float slatFreq = 34.0;
          float slatPhase = rotP.x * slatFreq;
          float slatFrac = fract(slatPhase);
          
          // Slat profile: clean dark slots between solid bands
          float slatMask = smoothstep(0.06, 0.18, slatFrac) * (1.0 - smoothstep(0.84, 0.96, slatFrac));
          float slatFacet = smoothstep(0.12, 0.5, slatFrac) * (1.0 - smoothstep(0.5, 0.88, slatFrac));

          // Radiant Energy Torus / Ellipse
          vec2 dP = p - center;
          // Elliptical distortion
          float ellipseDist = length(vec2(dP.x * 0.95, dP.y * 1.35));
          
          // Breathing animated radius
          float radius = 0.44 + 0.02 * sin(u_time * 0.85);
          float ringDist = abs(ellipseDist - radius);

          // Core energy intensity
          float ringGlow = exp(-ringDist * 12.0);
          float ringWide = exp(-ringDist * 4.2) * 0.75;
          float ringIntense = exp(-ringDist * 34.0);

          // Angular coordinates for chromatic variation around ring
          float ringAngle = atan(dP.y, dP.x);
          
          // Warm solar orange highlights along lower-left and top-right tangents
          float orangeFactor = pow(0.5 + 0.5 * sin(ringAngle * 2.0 - 0.6 + u_time * 0.2), 2.0);
          float cyanFactor = pow(0.5 + 0.5 * cos(ringAngle + 1.2 - u_time * 0.15), 1.6);
          float blueFactor = pow(0.5 + 0.5 * sin(ringAngle - 1.8), 1.4);

          // Color components matching Reference 2
          vec3 colCyan = vec3(0.0, 0.94, 1.0);        // Electric Cyan
          vec3 colBlue = vec3(0.18, 0.48, 1.0);       // Electric Blue
          vec3 colOrange = vec3(1.0, 0.58, 0.12);     // Warm Solar Orange
          vec3 colWhite = vec3(1.0, 1.0, 1.0);        // Hot Core
          vec3 colPurple = vec3(0.48, 0.24, 0.92);    // Deep Violet accent

          // Energy composite
          vec3 arcColor = mix(colBlue, colCyan, cyanFactor);
          arcColor = mix(arcColor, colOrange, orangeFactor * 0.68);
          arcColor = mix(arcColor, colPurple, blueFactor * 0.35);
          arcColor += colWhite * ringIntense * 0.95;

          // Modulate arc by diagonal slats
          float totalGlow = (ringGlow + ringWide * 0.6);
          vec3 finalColor = arcColor * totalGlow * (0.28 + 0.88 * slatMask);
          
          // Add subtle ambient slat illumination across the whole right side
          vec3 slatAmbient = mix(vec3(0.04, 0.06, 0.10), vec3(0.02, 0.03, 0.06), slatFacet);
          finalColor += slatAmbient * slatMask * 0.45;

          // Vignette around edges to blend with #050505 page background
          float edgeVignette = smoothstep(0.0, 0.12, st.x) * (1.0 - smoothstep(0.88, 1.0, st.x))
                             * smoothstep(0.0, 0.08, st.y) * (1.0 - smoothstep(0.92, 1.0, st.y));

          finalColor *= edgeVignette;

          // Output color with controlled alpha
          float alpha = clamp(length(finalColor) * 1.35, 0.0, 0.92);
          gl_FragColor = vec4(finalColor, alpha);
        }
      `;

      const vs = this.createShader(gl, gl.VERTEX_SHADER, vsSource);
      const fs = this.createShader(gl, gl.FRAGMENT_SHADER, fsSource);
      if (!vs || !fs) return false;

      const program = gl.createProgram();
      gl.attachShader(program, vs);
      gl.attachShader(program, fs);
      gl.linkProgram(program);

      if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.warn('HeroShader program link error:', gl.getProgramInfoLog(program));
        return false;
      }

      this.program = program;
      gl.useProgram(program);

      // Fullscreen quad
      const posBuffer = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, posBuffer);
      gl.bufferData(
        gl.ARRAY_BUFFER,
        new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]),
        gl.STATIC_DRAW
      );

      const aPosLoc = gl.getAttribLocation(program, 'a_position');
      gl.enableVertexAttribArray(aPosLoc);
      gl.vertexAttribPointer(aPosLoc, 2, gl.FLOAT, false, 0, 0);

      this.uResolutionLoc = gl.getUniformLocation(program, 'u_resolution');
      this.uTimeLoc = gl.getUniformLocation(program, 'u_time');
      this.uMouseLoc = gl.getUniformLocation(program, 'u_mouse');

      return true;
    }

    createShader(gl, type, source) {
      const shader = gl.createShader(type);
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.warn('HeroShader compile error:', gl.getShaderInfoLog(shader));
        gl.deleteShader(shader);
        return null;
      }
      return shader;
    }

    setup2DFallback() {
      this.useFallback = true;
      this.ctx2d = this.canvas.getContext('2d');
    }

    bindEvents() {
      window.addEventListener('pointermove', (e) => {
        if (!this.canvas) return;
        const rect = this.canvas.getBoundingClientRect();
        if (e.clientY < rect.bottom && e.clientY > rect.top) {
          this.pointer.targetX = (e.clientX - rect.left) / rect.width;
          this.pointer.targetY = 1.0 - (e.clientY - rect.top) / rect.height;
        }
      }, { passive: true });

      window.addEventListener('resize', () => this.resize(), { passive: true });

      if ('IntersectionObserver' in window) {
        this.observer = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            this.isVisible = entry.isIntersecting;
            if (this.isVisible && !this.animationFrameId) {
              this.start();
            }
          });
        }, { threshold: 0.05 });
        this.observer.observe(this.canvas);
      }
    }

    resize() {
      if (!this.canvas) return;
      const rect = this.canvas.getBoundingClientRect();
      const w = Math.max(Math.floor(rect.width * this.dpr), 300);
      const h = Math.max(Math.floor(rect.height * this.dpr), 200);

      if (this.canvas.width !== w || this.canvas.height !== h) {
        this.canvas.width = w;
        this.canvas.height = h;

        if (this.gl) {
          this.gl.viewport(0, 0, w, h);
        }
      }
    }

    renderWebGL(time) {
      const gl = this.gl;
      if (!gl || !this.program) return;

      gl.useProgram(this.program);
      gl.uniform2f(this.uResolutionLoc, this.canvas.width, this.canvas.height);
      gl.uniform1f(this.uTimeLoc, time * 0.001);

      this.pointer.x += (this.pointer.targetX - this.pointer.x) * 0.05;
      this.pointer.y += (this.pointer.targetY - this.pointer.y) * 0.05;
      gl.uniform2f(this.uMouseLoc, this.pointer.x, this.pointer.y);

      gl.drawArrays(gl.TRIANGLES, 0, 6);
    }

    render2DFallback(time) {
      const ctx = this.ctx2d;
      if (!ctx) return;
      const w = this.canvas.width;
      const h = this.canvas.height;

      ctx.clearRect(0, 0, w, h);

      const spacing = 28 * this.dpr;
      const cx = w * 0.70;
      const cy = h * 0.48;
      const radius = Math.min(w, h) * 0.32;

      ctx.save();
      ctx.lineWidth = 14 * this.dpr;

      for (let x = -w; x < w * 2; x += spacing) {
        ctx.beginPath();
        const x1 = x;
        const y1 = 0;
        const x2 = x + Math.tan(0.62) * h;
        const y2 = h;

        const midX = (x1 + x2) * 0.5;
        const midY = h * 0.5;
        const dist = Math.hypot(midX - cx, midY - cy);
        const ringDist = Math.abs(dist - radius);

        const glow = Math.exp(-ringDist / (60 * this.dpr));

        if (glow > 0.02 && midX > w * 0.22) {
          const alpha = glow * Math.min(1.0, (midX - w * 0.2) / (w * 0.35));
          const grad = ctx.createLinearGradient(x1, y1, x2, y2);
          grad.addColorStop(0, `rgba(0, 240, 255, ${alpha * 0.8})`);
          grad.addColorStop(0.5, `rgba(59, 130, 246, ${alpha * 0.9})`);
          grad.addColorStop(1, `rgba(245, 158, 11, ${alpha * 0.7})`);

          ctx.strokeStyle = grad;
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.stroke();
        }
      }
      ctx.restore();
    }

    start() {
      const loop = (timestamp) => {
        if (!this.isVisible || this.isStudioActive) {
          this.animationFrameId = null;
          return;
        }

        const elapsed = timestamp - this.startTime;
        if (this.useFallback) {
          this.render2DFallback(elapsed);
        } else {
          this.renderWebGL(elapsed);
        }

        this.animationFrameId = requestAnimationFrame(loop);
      };

      if (!this.animationFrameId) {
        this.animationFrameId = requestAnimationFrame(loop);
      }
    }

    stop() {
      if (this.animationFrameId) {
        cancelAnimationFrame(this.animationFrameId);
        this.animationFrameId = null;
      }
    }

    setStudioMode(inStudio) {
      this.isStudioActive = inStudio;
      if (inStudio) {
        this.stop();
      } else {
        this.start();
      }
    }
  }

  window.HeroShaderBackground = HeroShaderBackground;
})();
