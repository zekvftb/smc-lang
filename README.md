# 📺 SMC (Saturday Morning Cartoons) Programming Language

**SMC (Saturday Morning Cartoons)** is a biologically inspired, fault-tolerant programming language and standalone virtual machine. 

It translates the fundamental computational principles of **DNA and RNA** into modern, license-free software architecture, paired with subtle 90s cartoon and anime nostalgia!

---

## 🌐 Interactive Web Playground
🎮 **[Try SMC Live in Your Browser](https://zekvftb.github.io/smc-lang/)** *(Zero install required — runs client-side on mobile & desktop)*

---

## 📖 Master Handbook, Specification & Beginner's Guide
👉 **[docs/SMC_MADE_SIMPLE.md](docs/SMC_MADE_SIMPLE.md)** *(The fun, plain-English "Made Simple" beginner tutorial!)*  
👉 **[SMC_MASTER_HANDBOOK.md](SMC_MASTER_HANDBOOK.md)** *(The exhaustive guide with 7 real-world production blueprints!)*  
👉 **[docs/SPECIFICATION.md](docs/SPECIFICATION.md)** *(The formal language specification and operator precedence table)*  
👉 **[docs/GUIDE.md](docs/GUIDE.md)** *(The complete technical step-by-step tutorial)*  


---

## 🧬 Biological Principles to SMC Software Architecture

| Real Biological Mechanism (DNA/RNA) | Computer Science Problem | SMC Language Solution |
| :--- | :--- | :--- |
| **Codon Degeneracy** (64 codons map to 20 amino acids; 3rd base wobble absorbs mutations) | Rigid syntax: a single missing letter or typo halts the compiler with a fatal error. | **Wobble Typo-Tolerance**: Synonyms map to identical opcodes. Minor spelling mistakes are smoothly repaired via Levenshtein edit-distance without halting. |
| **HexaPhase Overlapping Genes** (Reading 6 concurrent phases from the same sequence) | 1D sequential execution: every routine requires its own separate memory footprint. | **HexaPhase Multiplexing**: Slices any stream into 6 concurrent execution channels (`+0, +1, +2, -0, -1, -2`) for massive space savings. |
| **Programmed Ribosomal Frameshifting** (Ribosomes slipping tracks at mechanical stress points) | Hard-coded branching requiring bloated if/else logic trees. | **PRF Slipping (`slip(+1)`)**: Dynamically slips the runtime execution track into emergency / alternate subroutines under system load. |
| **Palindromic Attenuator Hairpins** (Thermodynamic stem-loop mechanical pause gates) | Uncontrolled execution floods and runaway infinite loops. | **Attenuator Gates (`attenuator(threshold)`)**: Built-in thermodynamic rate-limiting and backpressure throttling. |
| **mRNA Half-Life Decay** (Poly-A tail shortens on each translation until transcript dissolves) | Memory leaks in C/C++; periodic CPU freezes from Garbage Collectors in Java/Python. | **Acme Anvil TTL**: Ephemeral variables carry an auto-decrementing `acme(ttl=N)` timer. Once expired, it vaporizes from RAM with zero memory leaks and 0% GC pauses. |
| **Lock-and-Key Receptors** (Proteins find targets by 3D physical pocket shape, not pointers) | Fragile numeric memory pointers (`0x7FFF`) and hard-coded network IP endpoints. | **Planetary Shape Dispatch**: Functions bind to elemental and planetary rings (`MERCURY`, `MARS`, `JUPITER`, `VENUS`, `MOON`). Callers emit ring keys to trigger matching handlers. |
| **p53 DNA Repair Checkpoint** ("Guardian of the genome" catching unrouted sequences) | Unhandled exceptions and crash cascades. | **Tuxedo Mask Watchdog**: Catches unrouted dispatches with a graceful fallback block ("My work here is done!"). |
| **Cellular Differentiation** (Stem cells differentiating into specialized tissue states) | State evolution and polymorphic typing. | **Sailor Moon MPP (Moon Prism Power)**: `mpp` (or `transform`) explicitly evolves an entity into its specialized form with dedicated behavior. |

---

## ⚡ Quickstart

### 1. Installation (100% Free & MIT/Public Domain)
```powershell
pip install -e D:\smc_lang\
```

### 2. Launching the Live Interactive REPL
```powershell
smc
# or: python -m smc.cli repl
```

### 3. Running an SMC Script
```powershell
python -m smc.cli run D:\smc_lang\examples\advanced_functions.smc
```

### 4. Running CatDog Dual-Frame Overlapping Code
```powershell
python -m smc.cli catdog D:\smc_lang\examples\catdog_dual_frame.smc
```

### 5. Inspecting Repaired Mutations & Tokens
```powershell
python -m smc.cli tokens D:\smc_lang\examples\sailor_moon_battle.smc
```

---

## 🎨 Modern Professional Syntax (with Degenerate Aliases)

SMC prioritizes clean, modern, professional keywords, while preserving nostalgic aliases under the hood:

```smc
experiment "Planetary_Defense"

# 1. Full arithmetic expressions with order of operations (* and / before + and -)
let enemy_hp = 100
let attack_power = (15 * 2) - 5   # Evaluates to 25

# 2. Tuxedo Mask watchdog fallback
fallback {
    print "Tuxedo Mask throws a red rose! (Graceful fallback executed)"
}

# 3. Planetary Senshi ring binding
bind(ring="MARS") {
    print "Sailor Mars: Flame blast triggered!"
}

# 4. Turn-based combat loop (while loop & conditionals)
while (enemy_hp > 0) {
    # Acme Anvil ephemeral shield (auto-vaporizes after 2 cycles without GC pauses)
    acme(ttl=2) defense_shield = "Active_Barrier"

    dispatch "MARS"
    let enemy_hp = enemy_hp - attack_power
}

# 5. Cellular Differentiation via MPP (Moon Prism Power)
let guardian = "Usagi_Tsukino"
mpp guardian = "Princess_Serenity" {
    print "State transformed to royal tier!"
}

halt
```

---

## 🎭 Why the Names Match the Functions

Every cartoon and anime namesake in SMC was intentionally chosen because its nostalgic pop-culture behavior precisely mirrors its computer science and biological function:

* 📦 **`acme` (Time-To-Live Memory Drop = mRNA Decay)**: In Looney Tunes, Wile E. Coyote orders from Acme Corporation, and an anvil inevitably drops on him from the sky. In SMC, `acme(ttl=N)` sets a countdown timer where an anvil literally drops on your variable, vaporizing it from RAM when its time is up with zero garbage collection pauses.
* 🌙 **`mpp` (Moon Prism Power = Cellular Differentiation)**: In Sailor Moon, shouting *"Moon Prism Power, Make Up!"* transforms Usagi from a normal schoolgirl into Sailor Moon. In SMC, `mpp var = new_state { ... }` permanently evolves an entity into its higher specialized form with dedicated behavior.
* 🌹 **`tuxedo` (Tuxedo Mask = Watchdog Fallback)**: In Sailor Moon, whenever a battle goes off-script and danger strikes, Tuxedo Mask mysteriously arrives, throws a red rose to intercept the attack, says *"My work here is done,"* and departs. In SMC, `tuxedo` / `fallback` intercepts unrouted dispatches to prevent crashes.
* 💍 **`rings` / `dispatch` (Planeteers = Lock-and-Key Receptors)**: In Captain Planet, Kwame, Wheeler, Linka, Gi, and Ma-Ti combine their elemental rings (*"Earth! Fire! Wind! Water! Heart!"*). In SMC, functions bind to receptor rings and dispatch by shape rather than fragile memory pointers.
* 🐱🐶 **`catdog` (Dual Reading Frames = Overlapping Genes)**: In CatDog, two completely different animals share a single body. In SMC, `catdog` interleaves two completely different programs on the exact same line of code for 2x memory density.
* 🔴 **`dee_dee` (Mutation Engine = Genetic Mutation Stress Testing)**: Dexter's sister Dee Dee sneaks into the lab asking *"Oooooh, what does THIS button do?!"* In SMC, `dee_dee` blocks inject non-destructive mutations to prove your system's codon wobble fault-tolerance.

---

## 🌐 Building Full-Stack Websites in SMC (`serve_http`)

SMC includes a native, high-performance HTTP web server built directly into DexterVM. You can build and host full dynamic websites and REST APIs written 100% in `.smc`:

```smc
experiment "My_Web_App"

fn handle_request(req) {
    let p = req["path"]

    # 1. Homepage with Template Strings
    if (p == "/") {
        let title = "SMC Web Server"
        return {
            "status": 200,
            "content_type": "text/html",
            "body": `<h1>Welcome to ${title}!</h1><p>Full-stack dynamic web in .smc!</p>`
        }
    }

    # 2. Ephemeral login session: Zero-Redis session state!
    if (p == "/login") {
        acme(ttl=5) user_auth = "Jason_Token"
        return "<h2>Logged in! Session auto-expires via Acme TTL.</h2>"
    }

    # 3. 1-line JSON API
    if (p == "/api/status") {
        return {
            "status": 200,
            "content_type": "application/json",
            "body": to_json({ "status": "ONLINE", "active": true })
        }
    }

    return { "status": 404, "body": "404: Tuxedo Mask could not find page" }
}

print "Server online at http://localhost:3000..."
serve_http(3000, "handle_request")
```

Run it with:
```powershell
python -m smc.cli run examples/smc_web_server.smc
```

---

## ✨ v0.4.0 Developer Ergonomics & Toolkit

* 🪄 **Template Strings:** Interpolate variables and expressions seamlessly using backticks:
  ```smc
  let msg = `Hello ${user["name"]}! Level: ${user["lvl"] + 1}`
  ```
* ⚡ **Native JSON:** Instant serialization and parsing with `to_json(dict)` and `from_json(str)`.
* 🎯 **Booleans & Logic:** First-class `true`, `false`, `null`, and logical operators `&&` (`and`), `||` (`or`).
* 🔢 **Effortless Loops:** `for i in range(1, 10) { ... }`
* ✂️ **Collection Utilities:** `split(str, sep)`, `join(list, sep)`, `keys(dict)`, `values(dict)`, `contains(coll, item)`.
* 📁 **Static File Serving:** `serve_file("path/to/asset.css")` with automatic MIME-type detection.

---

## 📦 Modular Multi-File Projects (`import`)

Split your codebase into reusable modules, libraries, and route controllers:

```smc
# In main.smc
import "modules/math_utils.smc"

let area = circle_area(5)
print `Area from imported module: ${area}`
```

SMC handles nested dependencies and features **cycle-safe import guards** to prevent duplicate execution or recursion loops.

---

## 🧬 Python Ecosystem Bridge (FFI)

SMC has native access to the **entire Python standard library and 500,000+ PyPI packages**:

```smc
# 1. Direct Python function calling
let root = py_call("math.sqrt", 256)
let dice = py_call("random.randint", 1, 6)

# 2. Native Python module import with alias
py_import "datetime" as dt
let stamp = py_call("datetime.datetime.now")

# 3. Dynamic Python evaluation
let total = py_eval("sum([10, 20, 30, 40])")

# 4. Ephemeral Acme TTL + Cryptography
acme(ttl=3) auth_token = py_call("secrets.token_hex", 16)
```

Fault-tolerant error handling guarantees that missing modules or exceptions log diagnostics without crashing the biological DexterVM process!

---

## 🎮 Interactive Live Web Playground
Experience SMC live in your browser with zero installation:
👉 **[https://zekvftb.github.io/smc-lang/](https://zekvftb.github.io/smc-lang/)**

Includes a **Virtual Web Browser** inspector where you can click `GET /`, `GET /login`, and `GET /api/status` to test dynamic HTTP servers directly inside the browser playground!

---

## 🛠️ Instant Project Scaffolding (`smc init`)

Create a full-stack, modular project in one command:

```powershell
smc init my_web_app
cd my_web_app
smc run main.smc
```

Generates a clean project structure with web routes, imported modules, static HTML assets, and documentation.

---

## 🧪 Automated Testing
Run the comprehensive test suite:
```powershell
python -m pytest D:\smc_lang\tests/
```
**All 42 tests pass in 6.7 seconds (including live HTTP socket tests, Python FFI bridge, and modular imports)!**

---

## 🎨 VS Code Syntax Highlighting Extension (`.vsix`)

SMC includes an official VS Code extension for full syntax coloring!

### ⚡ 1-Click Install with `.vsix`:
```powershell
code --install-extension editors/vscode/smc-lang-0.6.0.vsix
```

Or copy the extension folder manually:
```powershell
Copy-Item -Recurse D:\smc_lang\editors\vscode "$HOME\.vscode\extensions\smc-lang"
```
Reload VS Code (`Ctrl+Shift+P` -> "Developer: Reload Window") and `.smc` files will light up with syntax highlighting.

---

## 📜 License & Enterprise Commercial Terms

SMC is distributed under the **SMC Fair-Source License 1.0**:

* 🎓 **100% Free for Individuals, Students, & Non-Commercial Use:** You can learn, play, modify, and build personal or academic projects completely free forever.
* 🚀 **Small Business Safe Harbor:** 100% free for startups and companies with **gross annual revenues under $1,000,000 USD** and fewer than 10 employees.
* 🏢 **Enterprise Commercial License:** Commercial use by large entities exceeding the threshold, or use as a paid hosted cloud service, requires an Enterprise Commercial License.

For commercial licensing agreements and enterprise integration inquiries, contact:  
**Jason Rezek** — [`zekvftb@gmail.com`](mailto:zekvftb@gmail.com)
