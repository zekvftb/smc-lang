# 📺 The Official Guide to the SMC ("Saturday Morning Cartoons") Language

Welcome to **SMC (Saturday Morning Cartoons)**! 

SMC is an experimental, biological-inspired programming language and virtual machine runtime. It translates the 4 most ingenious information tricks of **DNA and RNA** into practical software architecture, wrapped in the nostalgic fun of 90s Saturday morning cartoons.

---

## 🔬 Table of Contents
1. [The Philosophy: Why Saturday Morning Cartoons?](#1-the-philosophy)
2. [Installation & Setup](#2-installation--setup)
3. [Your First SMC Script ("Hello Toon!")](#3-your-first-smc-script)
4. [Variables & The Powerpuff Girls State Machine](#4-variables--chemical-state)
5. [The Biological Superpowers](#5-the-biological-superpowers)
   - [Superpower 1: Wobble Typo-Tolerance (Codon Degeneracy)](#superpower-1-wobble-typo-tolerance)
   - [Superpower 2: Acme Anvil Ephemeral Memory (mRNA Decay)](#superpower-2-acme-anvil-ephemeral-memory)
   - [Superpower 3: Captain Planet Content-Addressable Calling](#superpower-3-captain-planet-dispatch)
   - [Superpower 4: CatDog Overlapping Bytecode (2 Programs in 1)](#superpower-4-catdog-overlapping-bytecode)
6. [The Complete Cartoon Opcode Dictionary](#6-the-complete-cartoon-opcode-dictionary)
7. [Running & Debugging Your Code](#7-running--debugging-your-code)

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
pip install -e D:\smc_lang\
```

Verify that it works:
```powershell
python -m pytest D:\smc_lang\tests/
```
*(All 6 tests should pass in less than 0.1 seconds!)*

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
python -m smc.cli run hello.smc
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

## 5. Control Flow & Arithmetic (Python Parity)

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
* **`type(val)`**: Returns `"dict"`, `"list"`, `"string"`, or `"number"`.
* **`read_file(path)`**: Reads text from a local file.
* **`write_file(path, content)`**: Writes text to a local file.

```smc
let inventory = ["Potion"]
push(inventory, "Shield")
print "Inventory count: " + str(len(inventory))
let used = pop(inventory)
```

---

## 6. The Interactive Live Lab Shell (REPL)

Instead of running files, you can experiment in a live, interactive DexterVM shell:

```powershell
smc
# or: python -m smc.cli repl
```

```text
=================================================================
  DEXTER_VM v0.3.0 - Interactive Saturday Lab Shell
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

Interactive commands:
* `vars`: Inspect all persistent variables and remaining Acme TTL timers.
* `clear`: Wipe state and re-initialize a fresh laboratory.
* `exit`: Cleanly quit the session.

---

## 6. The Sailor Moon & Cartoon Superpowers

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

### Superpower 6: CatDog Overlapping Bytecode (2 Programs in 1)
*Biological Principle: Multi-Frame Reading Frames*

Write two distinct routines on the exact same line of code and execute with `smc catdog` for 2x memory density.

---

## 7. The Complete Cartoon Opcode Dictionary

| Canonical Opcode | Sailor Moon & Cartoon Synonyms | What It Does |
| :--- | :--- | :--- |
| **`LET`** | `SET`, `VAR`, `SUGAR`, `SPICE`, `EVERYTHING_NICE` | Assigns a persistent variable |
| **`ACME(ttl=N)`** | `ACME_ANVIL_BOX`, `EPHEMERAL`, `ANVIL_BOX` | Ephemeral variable with auto-drop timer |
| **`IF` / `ELSE`** | `WHEN` / `OTHERWISE` | Conditional branching |
| **`WHILE`** | `LOOP`, `CYCLE`, `ROAD_RUNNER_LOOP` | Iteration loop |
| **`TRANSFORM`** | `MOON_PRISM_POWER`, `DIFFERENTIATE`, `EVOLVE` | Sailor Moon state transformation |
| **`FALLBACK`** | `TUXEDO_MASK`, `CATCH`, `ROSE_THROW` | Watchdog fallback handler |
| **`BIND`** | `SUMMON_PLANETEER`, `CAPTAIN_PLANET`, `RING_BIND` | Binds a function to a planetary ring shape |
| **`DISPATCH`** | `CALL`, `POWERS_COMBINED`, `I_CHOOSE_YOU` | Shape-based lock-and-key function calling |
| **`PRINT`** | `EMIT`, `KAMEHAMEHA`, `SAY`, `HADOUKEN` | Prints expression to stdout |
| **`HALT`** | `EXIT`, `RETURN`, `THATS_ALL_FOLKS`, `COWABUNGA` | Halts execution cleanly |

---

## 7. Running & Debugging Your Code

### Run normally:
```powershell
python -m smc.cli run path/to/script.smc
```

### Inspect repaired mutations & tokens:
```powershell
python -m smc.cli tokens path/to/script.smc
```
This will print every token in your file and highlight any typos that were repaired via codon degeneracy:
```
Line 02:01 | KEYWORD | 'KAMAHAMEHA' -> Opcode.PRINT [MUTATION REPAIRED!]
```

---

## 8. Visual Studio Code Syntax Highlighting

To give your `.smc` files syntax highlighting in VS Code:

```powershell
# Copy the included extension to your local VS Code extensions folder:
Copy-Item -Recurse D:\smc_lang\editors\vscode "$HOME\.vscode\extensions\smc-lang"
```

Reload VS Code (`Ctrl+Shift+P` -> "Developer: Reload Window"), and all keywords, Acme boxes, and Sailor Moon transformations will glow in full color!

Have fun experimenting in the laboratory!
