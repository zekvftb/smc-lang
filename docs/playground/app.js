/**
 * SMC DexterVM Multi-Phase Playground Client Logic.
 * Consumes execution trace JSON events and renders step-by-step state animations.
 */

const SAMPLES = {
  dual_slip: `experiment 'ribosomal_frameshift' {
    let viral_gag = 100
    print \`[F0: Primary Gag Expression] Gag=\${viral_gag}\`

    # Programmed Ribosomal Frameshifting (-1 / +2 slip)
    slip(1)
    let pol_overlap = viral_gag + 50
    print \`[F1: Slipped Pol Expression] Pol=\${pol_overlap}\`

    slip(1)
    let env_overlap = pol_overlap * 2
    print \`[F2: Slipped Env Expression] Env=\${env_overlap}\`
}`,

  acme_ttl: `experiment 'acme_token_decay' {
    # Ephemeral session auth key valid for 3 steps
    acme(ttl=3) auth_token = 9999
    let session_active = 1
    print \`Auth token issued: \${auth_token}\`

    slip(1)
    let step1_val = auth_token
    
    slip(1)
    let step2_val = auth_token
    
    slip(1)
    # Auth token drops anvil and zeroes out here!
    let step3_val = auth_token
}`,

  bubble_sort: `experiment 'bubble_sort_demo' {
    let arr = [5, 2, 8, 1, 9]
    let n = len(arr)
    
    for i in range(0, n) {
        for j in range(0, n - i - 1) {
            if (arr[j] > arr[j + 1]) {
                let tmp = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = tmp
            }
        }
    }
    print \`Sorted Array: \${arr}\`
}`,

  genetic_sieve: `experiment 'prime_sieve' {
    let primes = []
    let limit = 20
    
    for num in range(2, limit) {
        let is_prime = 1
        for factor in range(2, num) {
            if (num % factor == 0) {
                is_prime = 0
            }
        }
        if (is_prime == 1) {
            primes.push(num)
        }
    }
    print \`Primes up to 20: \${primes}\`
}`
};

let currentTrace = [];
let currentStepIdx = 0;

// Elements
const editor = document.getElementById("code-editor");
const sampleSelect = document.getElementById("sample-select");
const btnRun = document.getElementById("btn-run");
const btnStep = document.getElementById("btn-step");
const btnReset = document.getElementById("btn-reset");
const stepInfo = document.getElementById("step-info");
const varsContainer = document.getElementById("variables-list");
const ttlContainer = document.getElementById("ttl-container");
const consoleBox = document.getElementById("console-output");

// Load Initial Sample
editor.value = SAMPLES.dual_slip;

sampleSelect.addEventListener("change", (e) => {
  const key = e.target.value;
  if (SAMPLES[key]) {
    editor.value = SAMPLES[key];
    resetSimulation();
  }
});

btnRun.addEventListener("click", () => {
  simulateTraceFromCode(editor.value);
});

btnStep.addEventListener("click", () => {
  stepForward();
});

btnReset.addEventListener("click", () => {
  resetSimulation();
});

function simulateTraceFromCode(code) {
  // Parse lines to build simulated trace events
  const lines = code.split("\n").map(l => l.trim()).filter(l => l.length > 0 && !l.startsWith("#"));
  currentTrace = [];
  let phase = 0;
  let vars = {};
  let ttls = {};
  let logs = [];

  let stepCounter = 1;
  for (const line of lines) {
    if (line.includes("slip(")) {
      const match = line.match(/slip\((\d+)\)/);
      const shift = match ? parseInt(match[1]) : 1;
      phase = (phase + shift) % 3;
    } else if (line.includes("let ")) {
      const match = line.match(/let\s+([a-zA-Z0-9_]+)\s*=\s*(.*)/);
      if (match) {
        vars[match[1]] = match[2];
      }
    } else if (line.includes("acme(")) {
      const match = line.match(/acme\(ttl=(\d+)\)\s+([a-zA-Z0-9_]+)\s*=\s*(.*)/);
      if (match) {
        const ttlVal = parseInt(match[1]);
        const varName = match[2];
        ttls[varName] = ttlVal;
        vars[varName] = match[3];
      }
    } else if (line.includes("print ")) {
      logs.push(`[OUT] ${line.replace("print ", "")}`);
    }

    currentTrace.push({
      step_index: stepCounter++,
      active_phase: phase,
      instruction_desc: line,
      variables_snapshot: { ...vars },
      acme_ttl_snapshot: { ...ttls },
      console_log: [...logs]
    });
  }

  currentStepIdx = 0;
  btnStep.disabled = false;
  renderStep(currentTrace[0]);
}

function stepForward() {
  if (currentStepIdx < currentTrace.length - 1) {
    currentStepIdx++;
    renderStep(currentTrace[currentStepIdx]);
  } else {
    btnStep.disabled = true;
    stepInfo.textContent += " (Complete)";
  }
}

function renderStep(step) {
  if (!step) return;

  // 1. Update Phase Conveyor Belt
  [0, 1, 2].forEach(p => {
    const track = document.getElementById(`track-${p}`);
    if (p === step.active_phase) {
      track.classList.add("active");
    } else {
      track.classList.remove("active");
    }
  });

  // 2. Update Step Info
  stepInfo.textContent = `Step: ${step.step_index} / ${currentTrace.length} | Op: ${step.instruction_desc}`;

  // 3. Update Variables
  const varKeys = Object.keys(step.variables_snapshot);
  if (varKeys.length === 0) {
    varsContainer.innerHTML = '<span class="empty-hint">No active variables</span>';
  } else {
    varsContainer.innerHTML = varKeys.map(k => `
      <div class="var-tag">
        <span class="var-name">${k}:</span>
        <span class="var-val">${step.variables_snapshot[k]}</span>
      </div>
    `).join("");
  }

  // 4. Update TTLs
  const ttlKeys = Object.keys(step.acme_ttl_snapshot);
  if (ttlKeys.length === 0) {
    ttlContainer.innerHTML = '<span class="empty-hint">No active ephemeral TTL boxes</span>';
  } else {
    ttlContainer.innerHTML = ttlKeys.map(k => `
      <div class="ttl-card">
        ⏳ <strong>${k}</strong> (TTL: ${step.acme_ttl_snapshot[k]} steps remaining)
      </div>
    `).join("");
  }

  // 5. Update Console Log
  if (step.console_log && step.console_log.length > 0) {
    consoleBox.textContent = step.console_log.join("\n");
  }
}

function resetSimulation() {
  currentTrace = [];
  currentStepIdx = 0;
  btnStep.disabled = true;
  stepInfo.textContent = "Step: 0 / 0 | Current Op: IDLE";
  varsContainer.innerHTML = '<span class="empty-hint">No active variables</span>';
  ttlContainer.innerHTML = '<span class="empty-hint">No active ephemeral TTL boxes</span>';
  consoleBox.textContent = "[SYSTEM READY] Enter an SMC experiment or load a sample above.";
  [0, 1, 2].forEach(p => {
    const track = document.getElementById(`track-${p}`);
    if (p === 0) track.classList.add("active");
    else track.classList.remove("active");
  });
}
