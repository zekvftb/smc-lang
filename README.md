# 📺 SMC (Saturday Morning Cartoons) Programming Language
**The Biologically-Inspired, Bytecode-Compiled State Machine Language**

[![Pytest Status](https://img.shields.io/badge/tests-64%20passed-brightgreen.svg)](tests/)
[![Architecture](https://img.shields.io/badge/engine-Linear%20Bytecode%20VM-blue.svg)](src/smc/bytecode_vm.py)
[![Standard Library](https://img.shields.io/badge/stdlib-math%20%7C%20fsm%20%7C%20sequence-orange.svg)](std/)
[![License: MIT/Fair-Source](https://img.shields.io/badge/License-Fair--Source%201.0-purple.svg)](LICENSE)

**SMC (Saturday Morning Cartoons)** is a dual-profile programming language and fast linear bytecode virtual machine. It combines the multi-threaded information density and fault-tolerance of **biological genomes** with clean Go-inspired developer ergonomics and nostalgic Saturday morning pop culture!

---

## 🌐 Interactive Web Playground
🎮 **[Try SMC Live in Your Browser](https://zekvftb.github.io/smc-lang/)** *(Zero install required — runs client-side on mobile & desktop)*

---

## 📖 Master Documentation & Guides
* 👉 **[`docs/SMC_MADE_SIMPLE.md`](docs/SMC_MADE_SIMPLE.md)** *(The fun, plain-English "Made Simple" beginner tutorial!)*  
* 👉 **[`SMC_MASTER_HANDBOOK.md`](SMC_MASTER_HANDBOOK.md)** *(The exhaustive guide with real-world production blueprints)*  
* 👉 **[`docs/SPECIFICATION.md`](docs/SPECIFICATION.md)** *(The formal language specification and EBNF grammar)*  
* 👉 **[`docs/GUIDE.md`](docs/GUIDE.md)** *(The complete technical step-by-step tutorial)*  

---

## ⚡ Key Architectural Features (v0.8.0)

### 1. 🚀 Linear Bytecode Compiler & Stack VM (Fast Default Engine)
SMC compiles AST trees into flat arrays of linear bytecode instructions (`LOAD_CONST`, `STORE_VAR`, `BINARY_OP`, `JUMP`, `CALL_BUILTIN`, `HALT`), executing on a high-throughput stack virtual machine with an integer program counter (`pc`).
```powershell
smc run script.smc
```

### 2. 🛡️ Strict Mode (`--strict`)
Disable fuzzy Levenshtein repairs for zero-tolerance production software development:
```powershell
smc run --strict script.smc
```

### 3. 🔍 Linear Bytecode Disassembler (`smc dis`)
Inspect compiled bytecode instructions, memory offsets, and operands:
```powershell
smc dis examples/rover_state_machine.smc
```

### 4. 🐞 Interactive Step Debugger CLI (`smc debug`)
Step through execution instruction-by-instruction, examine active variables, and evaluate expressions in real time:
```powershell
smc debug examples/rover_state_machine.smc
```

### 5. 📦 Modular Standard Library (`std/`)
* **`std/math.smc`:** `mean()`, `variance()`, `min_val()`, `max_val()`, `moving_average()`, `clamp()`.
* **`std/fsm.smc`:** State machine verification (`validate_fsm`) and deterministic simulation (`simulate_fsm`).
* **`std/sequence.smc`:** Sequence analysis (`gc_content_pct()`, `extract_codons()`, `count_motifs()`).

---

## 🧬 Biological Principles to SMC Software Architecture

| Real Biological Mechanism | Computer Science Problem | SMC Language Solution |
| :--- | :--- | :--- |
| **Codon Degeneracy** (64 codons map to 20 amino acids) | Rigid syntax: a single missing letter or typo halts the compiler. | **Degenerate Opcode Synonyms & Wobble Tolerance**: Multiple keywords map to the exact same opcode (`var`, `let`, `set` $\rightarrow$ `STORE_VAR`). |
| **HexaPhase Overlapping Reading Frames** | 1D sequential execution: every routine requires its own separate memory. | **HexaPhase Multiplexing**: Slices any stream into 6 concurrent execution channels (`+0, +1, +2, -0, -1, -2`) for massive space savings. |
| **Programmed Ribosomal Frameshifting** (Slipping tracks at stress points) | Hard-coded branching requiring bloated if/else logic trees. | **`slip_branch(prob, funcA, funcB)`**: Dynamically slips the runtime execution track into emergency subroutines under system load. |
| **G-Quadruplex & Attenuator Gates** (Thermodynamic physical barriers) | Uncontrolled execution floods and runaway infinite loops. | **`g4_latch(stress, threshold)`**: Built-in thermodynamic molecular circuit breaker that stalls execution when thresholds are exceeded. |
| **mRNA Half-Life Decay** (Poly-A tail shortens until transcript dissolves) | Memory leaks in C/C++; periodic CPU freezes from Garbage Collectors in Java/Python. | **Acme Anvil TTL (`acme(ttl=N)`)**: Ephemeral variables carry an auto-decrementing timer. Once expired, it vaporizes from RAM with 0% GC pauses. |
| **Lock-and-Key Receptors** (Proteins find targets by 3D physical pocket shape) | Fragile numeric memory pointers (`0x7FFF`) and hard-coded network IP endpoints. | **Planetary Shape Dispatch**: Functions bind to elemental rings (`MARS`, `MOON`). Callers emit ring keys to trigger matching handlers. |
| **p53 DNA Repair Checkpoint** ("Guardian of the genome") | Unhandled exceptions and crash cascades. | **Tuxedo Mask Watchdog (`fallback { ... }`)**: Catches unrouted dispatches with a graceful fallback block ("My work here is done!"). |

---

## ⚡ Quickstart

### 1. Installation (Free & MIT/Fair-Source)
```powershell
pip install -e D:\smc_lang\
```

### 2. Launching the Interactive REPL
```powershell
smc
# or: python -m smc.cli repl
```

### 3. Running an SMC Script (Fast Bytecode Default)
```powershell
smc run examples/rover_state_machine.smc
```

### 4. Running in Strict Mode
```powershell
smc run --strict examples/rover_state_machine.smc
```

### 5. Step-Debugging an SMC Script
```powershell
smc debug examples/rover_state_machine.smc
```

---

## 🤖 Mars Planetary Rover Example (`examples/rover_state_machine.smc`)

```smc
# 1. Define Discrete FSM Transition Matrix
var rover_fsm = {
    "SLEEP": { "SUNRISE": "CHARGING", "EMERGENCY": "SAFE_MODE" },
    "CHARGING": { "BATTERY_FULL": "SCIENCE_OPERATIONS", "SUNSET": "SLEEP" },
    "SCIENCE_OPERATIONS": { "TASK_COMPLETE": "DRIVING", "BATTERY_LOW": "SLEEP" },
    "DRIVING": { "DESTINATION_REACHED": "SCIENCE_OPERATIONS", "SUNSET": "SLEEP" }
}

# 2. Simulate Mission Event Stream
var mission_events = ["SUNRISE", "BATTERY_FULL", "TASK_COMPLETE", "DESTINATION_REACHED", "SUNSET"]
var mission_result = fsm_run("SLEEP", mission_events, rover_fsm)

print "Execution Path: " + to_json(mission_result["history"])
print "Final Rover State: " + mission_result["final_state"]

# 3. Built-in Data & Math Toolkit
var raw_solar_voltage = 142.5
var safe_voltage = clamp(raw_solar_voltage, 0.0, 100.0) # Returns 100.0

var sensor_stream = [22.1, 23.4, 21.9, 25.6, 28.0, 24.1]
var smoothed_windows = window(sensor_stream, 3, 1)      # Slices 3-point rolling windows
print "Windows: " + to_json(smoothed_windows)
```

---

## 🌐 Full-Stack Dynamic Web Servers (`serve_http`)

```smc
experiment "My_Web_App"

fn handle_request(req) {
    let p = req["path"]

    if (p == "/") {
        return {
            "status": 200,
            "content_type": "text/html",
            "body": "<h1>Welcome to SMC Full-Stack Web!</h1>"
        }
    }

    if (p == "/login") {
        acme(ttl=5) user_auth = "Jason_Token"
        return "<h2>Logged in! Session auto-expires via Acme TTL.</h2>"
    }

    return { "status": 404, "body": "404: Not Found" }
}

print "Server online at http://localhost:3000..."
serve_http(3000, "handle_request")
```

---

## 🧬 Python Ecosystem Bridge (FFI)

```smc
# 1. Direct Python function calling
let root = py_call("math.sqrt", 256)
let dice = py_call("random.randint", 1, 6)

# 2. Native Python module import with alias
py_import "datetime" as dt
let stamp = py_call("datetime.datetime.now")

# 3. Dynamic Python evaluation
let total = py_eval("sum([10, 20, 30, 40])")
```

---

## 🧪 Automated Testing
Run the full test suite:
```powershell
python -m pytest D:\smc_lang\tests/
```
**All 64 tests pass with 100% test coverage (Bytecode VM, Strict Mode, Standard Library, Web Sockets, FSM engine, and Biological Primitives)!**

---

## 📜 License & Enterprise Terms
Distributed under the **SMC Fair-Source License 1.0**:
* 🎓 **100% Free for Individuals, Students, Researchers, & Non-Commercial Use.**
* 🚀 **Small Business Safe Harbor:** 100% free for startups with **gross annual revenues under $1,000,000 USD** and fewer than 10 employees.
* 🏢 **Enterprise Commercial License:** Contact Jason Rezek (`zekvftb@gmail.com`).
