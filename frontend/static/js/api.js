/**
 * Synthetix - Multi-Agent Coding System
 * API Service Client
 * 
 * Interacts with backend FastAPI endpoints:
 * - GET  /api/config
 * - GET  /api/problems
 * - POST /api/run/stream (SSE)
 * - POST /api/run (REST fallback)
 * - POST /api/run_custom_input
 */

const ApiClient = {
  /**
   * Fetches backend provider status, active LLM model, RL model status.
   */
  async getConfig() {
    try {
      const response = await fetch('/api/config');
      if (!response.ok) throw new Error(`Config fetch failed: ${response.status}`);
      return await response.json();
    } catch (err) {
      console.warn('ApiClient.getConfig warning:', err);
      return null;
    }
  },

  /**
   * Fetches benchmark problems library.
   */
  async getProblems() {
    try {
      const response = await fetch('/api/problems');
      if (!response.ok) throw new Error(`Problems fetch failed: ${response.status}`);
      return await response.json();
    } catch (err) {
      console.error('ApiClient.getProblems error:', err);
      throw err;
    }
  },

  /**
   * Runs the full multi-agent pipeline with real-time Server-Sent Events (SSE).
   */
  async runPipelineStream(payload, callbacks = {}) {
    const { onStarted, onStepStart, onStepDone, onComplete, onError } = callbacks;

    try {
      const response = await fetch('/api/run/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          requirement: payload.requirement,
          test_code: payload.test_code || '',
          mode: payload.mode || 'rl'
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Stream error: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop(); // Keep unfinished fragment

        for (const block of lines) {
          const trimmed = block.trim();
          if (!trimmed.startsWith('data: ')) continue;
          const jsonStr = trimmed.replace(/^data:\s*/, '');

          try {
            const data = JSON.parse(jsonStr);

            if (data.event === 'started' && onStarted) {
              onStarted(data);
            } else if (data.event === 'step_start' && onStepStart) {
              onStepStart(data);
            } else if (data.event === 'step_done' && onStepDone) {
              onStepDone(data);
            } else if (data.event === 'complete' && onComplete) {
              onComplete(data.data);
            } else if (data.event === 'error' && onError) {
              onError(data.error);
            }
          } catch (jsonErr) {
            console.error('Failed to parse SSE payload:', jsonStr, jsonErr);
          }
        }
      }
    } catch (streamErr) {
      console.warn('SSE stream failed, falling back to direct REST /api/run:', streamErr);
      try {
        const fallbackResult = await this.runPipeline(payload);
        if (onComplete) onComplete(fallbackResult);
      } catch (fallbackErr) {
        if (onError) onError(fallbackErr.message || String(fallbackErr));
      }
    }
  },

  /**
   * Direct synchronous /api/run fallback endpoint.
   */
  async runPipeline(payload) {
    const response = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        requirement: payload.requirement,
        test_code: payload.test_code || '',
        mode: payload.mode || 'rl'
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `Pipeline execution failed with status ${response.status}`);
    }

    return await response.json();
  },

  /**
   * Executes custom user code input expression in isolated Python sandbox.
   */
  async runCustomInput(code, customInput) {
    const response = await fetch('/api/run_custom_input', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: code,
        custom_input: customInput
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `Execution failed with status ${response.status}`);
    }

    return await response.json();
  }
};

window.ApiClient = ApiClient;
