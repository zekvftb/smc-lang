# 📺 The Official Guide to the SMC ("Saturday Morning Cartoons") Language

Welcome to **SMC (Saturday Morning Cartoons)**! 

SMC is an experimental, biological-inspired programming language and virtual machine runtime. It translates the fundamental computational principles of **DNA and RNA** into practical software architecture, wrapped in the nostalgic fun of 90s Saturday morning cartoons.

---

## 🔬 Table of Contents
1. [The Philosophy: Why Saturday Morning Cartoons?](#1-the-philosophy)
2. [Installation & Setup](#2-installation--setup)
3. [Your First SMC Script ("Hello Toon!")](#3-your-first-smc-script)
4. [Variables & The Powerpuff Girls State Machine](#4-variables--chemical-state)
5. [Control Flow & Arithmetic](#5-control-flow--arithmetic)
6. [Modular Multi-File Architecture (`import`)](#6-modular-multi-file-architecture-import)
7. [The Interactive Live Lab Shell (REPL)](#7-the-interactive-live-lab-shell-repl)
8. [The Biological Superpowers](#8-the-biological-superpowers)
   - [Superpower 1: Wobble Typo-Tolerance (Codon Degeneracy)](#superpower-1-wobble-typo-tolerance)
   - [Superpower 2: Acme Anvil Ephemeral Memory (mRNA Decay)](#superpower-2-acme-anvil-ephemeral-memory)
   - [Superpower 3: Sailor Moon Transformations (`mpp`)](#superpower-3-sailor-moon-transformations-mpp--moon_prism_power)
   - [Superpower 4: Planetary Senshi & Captain Planet Dispatch](#superpower-4-planetary-senshi--captain-planet-dispatch)
   - [Superpower 5: Tuxedo Mask Watchdog Fallback](#superpower-5-tuxedo-mask-watchdog-fallback)
   - [Superpower 6: HexaPhase Multiplexing & Ribosomal Slipping](#superpower-6-hexaphase-multiplexing--ribosomal-slipping-v070)
9. [Python Ecosystem FFI Bridge & Web Server](#9-python-ecosystem-ffi-bridge--web-server)
10. [Formal Language Specification](#10-formal-language-specification)
11. [Running & Debugging Your Code](#11-running--debugging-your-code)
12. [Visual Studio Code Extension](#12-visual-studio-code-extension)

---

## 1. The Philosophy

Traditional human programming languages (like C, Python, or Rust) are **rigid and fragile**:
* If you misplace a single semicolon or misspell one keyword, your program crashes with a `SyntaxError`.
* If a single cosmic ray flips one bit in memory, your program crashes with a `Segmentation Fault`.
* Programs require massive "Garbage Collectors" that freeze the CPU to clean up old memory.

**DNA doesn't work that way.**
DNA has been running continuously on planet Earth for 3.8 billion years without crashing. It achieves this because:
1. It uses **synonyms** (multiple codons mean the same instruction).
2. It has **built-in expiration dates** on messages (mRNA naturally dissolves).
3. It uses **shape matching** instead of hard-coded numeric memory pointers.

In SMC, we packaged these principles inside the world of **Dexter's Laboratory, The Powerpuff Girls, CatDog, Captain Planet, and Looney Tunes**.

---

## 2. Installation & Setup

SMC runs 100% locally on your PC using Python 3.11+. It has zero external dependencies and requires zero cloud access.

To install the SMC command-line tool:
```powershell
pip install smc-lang
# or from source:
pip install -e D:\smc_lang\
```

Verify that it works:
```powershell
python -m pytest D:\smc_lang\tests/
```
*(All 47 tests should pass in less than 7 seconds!)*

---

## 3. Your First SMC Script

Create a file called `hello.smc`:

```smc
# Every great program begins in Dexter's Secret Lab!
DEXTER_LAB_EXPERIMENT "My_First_Toon_Program"

# Output a message to the console
KAMEHAMEHA "Hello from Saturday Morning Cartoons!"

# Safely terminate the program
THATS_ALL_FOLKS
```

### Run it from your terminal:
```powershell
smc run hello.smc
```

### Output:
```
--- DEXTER_VM EXECUTION OUTPUT ---
[DEXTER_VM] [LAB_INIT] Initializing experiment 'My_First_Toon_Program'...
Hello from Saturday Morning Cartoons!
[THATS_ALL_FOLKS] [HALT] Program reached clean termination.
----------------------------------
Steps: 2 | Anvils Dropped: 0 | Mutations Survived: 0
```

---

## 4. Variables & Chemical State

In SMC, variables represent chemical ingredients mixed in Dexter's lab:

```smc
DEXTER_LAB_EXPERIMENT "Chemical_Concoction"

# Declare variables using any Powerpuff Girls ingredient:
SUGAR speed = 100
SPICE power = 500
EVERYTHING_NICE defense = 250

# Print values
KAMEHAMEHA speed
KAMEHAMEHA power

THATS_ALL_FOLKS
```

---

## 5. Control Flow & Arithmetic

SMC supports full mathematical expressions and standard control flow:

### Arithmetic & Precedence
Standard order of operations (`*`, `/`, `%` before `+`, `-`) with parentheses support:
```smc
let damage = (base_attack * 2) - 5
let remainder = 17 % 5
```

### Conditionals (`if` / `else`)
```smc
if (damage > 50) {
    print "Critical hit!"
} else {
    print "Normal strike."
}
```

### Iteration (`while` loops)
```smc
let counter = 0
while (counter < 5) {
    let counter = counter + 1
    print counter
}
```

### User Functions (`fn` & `return`)
Declare reusable subroutines with arguments and isolated local variable scopes:
```smc
fn calculate_power(base, multiplier) {
    let boosted = (base * multiplier) + 10
    return boosted
}

let result = calculate_power(20, 3)   # 70
print result
```

### First-Class Lists / Arrays
Store ordered collections and access items by 0-based index (including negative indices):
```smc
let team = ["Blossom", "Bubbles", "Buttercup"]
let scores = [100, 250, (50 * 8)]

print team[0]       # "Blossom"
print team[-1]      # "Buttercup" (negative index)
```

### First-Class Dictionaries / Key-Value Objects
Model entities and structured state:
```smc
let hero = {
    "name": "Sailor_Mars",
    "hp": 100,
    "element": "FIRE"
}

print hero["name"]      # "Sailor_Mars"
hero["hp"] -= 20        # Compound indexed assignment
hero["status"] = "Ready"
```

### For-In Loops
Iterate directly over collections without manual index counters:
```smc
for member in team {
    print "Roster: " + member
}
```

### Compound Assignment
Support `+=`, `-=`, `*=`, `/=`:
```smc
let power = 50
power += 25     # 75
power *= 2      # 150
```

### Standard Built-in Library Functions
* **`len(x)`**: Returns length of list, dictionary, or string.
* **`push(list, item)`**: Appends an item to the end of a list.
* **`pop(list)`**: Removes and returns the last element of a list.
* **`str(val)`**: Converts number or boolean to string.
* **`int(val)`**: Parses string to integer.
* **`to_json(data)`**: Serializes dictionaries, lists, and primitives into JSON strings.
* **`from_json(json_str)`**: Parses JSON strings directly into native SMC data structures.
* **`range(start, end[, step])`**: Generates number sequences for `for-in` loops.
* **`split(text, sep)`**: Splits string into a list by delimiter.
* **`join(list, sep)`**: Combines list of items into a single string.
* **`keys(dict)`**: Returns all keys from a dictionary.
* **`values(dict)`**: Returns all values from a dictionary.
* **`contains(collection, target)`**: Checks membership in lists, dictionaries, and strings.
* **`serve_file(path)`**: Serves static files with automatic MIME-type detection in web servers.
* **`serve_http(port, handler_fn)`**: Launches a native high-performance HTTP web server.

```smc
let user = { "name": "Dexter", "level": 10 }
let json_str = to_json(user)
let back = from_json(json_str)
print `User: ${back["name"]} (Lvl ${back["level"]})`
```

---

## 6. Modular Multi-File Architecture (`import`)

SMC projects can be modularized across multiple `.smc` files:

```smc
# In main.smc
import "modules/math_utils.smc"
import "routes/api.smc"

let area = circle_area(10)
print `Computed area: ${area}`
```

* **Relative Resolution:** Paths resolve relative to the importing file.
* **Cycle Prevention:** A built-in import registry guarantees modules are only executed once, preventing circular reference lockups.
* **Codon Wobble:** Synonyms like `include`, `require`, and `load_module` are automatically supported.

---

## 7. The Interactive Live Lab Shell (REPL)

Experiment in a live, interactive DexterVM shell:

```powershell
smc repl
```

```text
=================================================================
  DEXTER_VM v0.7.0 - Interactive Saturday Lab Shell
  100% License-Free & Standalone Engine
  Commands: 'exit' to quit, 'clear' to reset, 'vars' to inspect
=================================================================

smc> let x = (10 * 5) + 2
smc> print x
52
smc> acme(ttl=2) token = "VanishSoon"
smc> print token
VanishSoon
smc> print "Cycle"
[ACME_ANVIL] *ANVIL DROPPED* on 'token'! Ephemeral variable dissolved.
Cycle
```

---

## 8. The Biological Superpowers

### Superpower 1: Wobble Typo-Tolerance
*Biological Principle: Codon Degeneracy*

In DNA, multiple codons mean the same thing. In SMC, keywords have synonym clusters and Levenshtein edit-distance repair. If you type `prnt` or `whle`, the compiler smoothly repairs the typo without crashing!

### Superpower 2: Acme Anvil Ephemeral Memory
*Biological Principle: mRNA Half-Life Decay*

In biology, transcripts naturally degrade after being read. In SMC, variables carry an auto-drop timer:
```smc
acme(ttl=2) session_token = "TEMP_KEY_123"
```
After 2 execution cycles, an Acme anvil drops and the variable vaporizes from RAM with zero memory leaks and zero garbage collection pauses.

### Superpower 3: Sailor Moon Transformations (`mpp` / `MOON_PRISM_POWER`)
*Biological Principle: Cellular Differentiation*

Cells differentiate from stem cells into specialized tissues. Just as Usagi shouts *"Moon Prism Power!"* to transform into Sailor Moon, you can evolve state using the punchy **`mpp`** keyword:
```smc
let guardian = "Usagi_Tsukino"
mpp guardian = "Princess_Serenity" {
    print "State evolved to royal tier!"
}
```

### Superpower 4: Planetary Senshi & Captain Planet Dispatch
*Biological Principle: Lock-and-Key Receptors*

Instead of numeric memory pointers (`0x7FFF`), functions bind to elemental/planetary shapes (`MERCURY`, `MARS`, `JUPITER`, `VENUS`, `MOON`):
```smc
bind(ring="MARS") {
    print "Mars Flame Sniper triggered!"
}
dispatch "MARS"
```

### Superpower 5: Tuxedo Mask Watchdog Fallback
*Biological Principle: p53 DNA Repair Checkpoint*

If code dispatches to a ring that has not been bound in the system, Tuxedo Mask steps in as a safe watchdog handler:
```smc
fallback {
    print "Tuxedo Mask throws a red rose! (Graceful fallback executed)"
}
dispatch "UNBOUND_SERVICE"
```

### Superpower 6: HexaPhase Multiplexing & Ribosomal Slipping (v0.7.0)
*Biological Principle: 6-Phase Reading Frames & Programmed Frameshifting (PRF)*

Slice any stream into 6 concurrent reading phases (`+0, +1, +2, -0, -1, -2`) and dynamically shift execution tracks under load:
```smc
experiment "HexaPhase_Demo"

# 1. HexaPhase Multiplexing Block
hexaphase "ABCDEF" {
    let p0 = hexaphase_channels["+0"] # "AD"
    let p1 = hexaphase_channels["+1"] # "BE"
}

# 2. Programmed Ribosomal Frameshift (PRF)
slip(1) # Shifts execution track into Phase +1

# 3. Thermodynamic Attenuator Rate-Limiting Gate
attenuator(threshold = 500) {
    print "Attenuator active: Backpressure throttled."
}

halt
```

---

## 7. Python Ecosystem FFI Bridge & Web Server

### Python FFI Bridge (`py_call`, `py_eval`, `py_import`)
Access all of Python's standard library and scientific packages:
```smc
let root = py_call("math.sqrt", 256)
py_import "datetime" as dt
let now = py_call("datetime.datetime.now")
print `Square root: ${root}, Timestamp: ${now}`
```

### Full-Stack Web Server (`serve_http`)
```smc
fn handle_request(req) {
    let path = req["path"]
    if (path == "/") {
        return { "status": 200, "content_type": "text/html", "body": "<h1>SMC Laboratory Online</h1>" }
    }
    return { "status": 404, "body": "Not Found" }
}

serve_http(3000, "handle_request")
```

---

## 8. Formal Language Specification
👉 **For complete operator precedence tables, lexical grammar, and edge-case policies, see [docs/SPECIFICATION.md](SPECIFICATION.md)**!

---

## 9. Running & Debugging Your Code

### Run an SMC program:
```powershell
smc run path/to/script.smc
# or: python -m smc.cli run path/to/script.smc
```

### Launch the interactive REPL:
```powershell
smc repl
```

### Initialize a new project scaffold:
```powershell
smc init my_app
```

### Inspect repaired mutations & tokens:
```powershell
smc tokens path/to/script.smc
```

---

## 10. Visual Studio Code Extension

To install syntax highlighting and language support:
```powershell
code --install-extension editors/vscode/smc-lang-0.7.0.vsix
```

Have fun experimenting in Dexter's Laboratory! 🧪
