# 📺 SMC (Saturday Morning Cartoons) Programming Language

**SMC (Saturday Morning Cartoons)** is a biologically inspired, fault-tolerant programming language and standalone virtual machine. 

It translates the fundamental computational principles of **DNA and RNA** into modern, license-free software architecture, paired with subtle 90s cartoon and anime nostalgia!

---

## 🌐 Interactive Web Playground
🎮 **[Try SMC Live in Your Browser](https://zekvftb.github.io/smc-lang/)** *(Zero install required — runs client-side on mobile & desktop)*

---

## 📖 Complete Documentation & Tutorial
👉 **Read the comprehensive guide and manual in [docs/GUIDE.md](docs/GUIDE.md)**!

---

## 🧬 Biological Principles to SMC Software Architecture

| Real Biological Mechanism (DNA/RNA) | Computer Science Problem | SMC Language Solution |
| :--- | :--- | :--- |
| **Codon Degeneracy** (64 codons map to 20 amino acids; 3rd base wobble absorbs mutations) | Rigid syntax: a single missing letter or typo halts the compiler with a fatal error. | **Wobble Typo-Tolerance**: Synonyms map to identical opcodes. Minor spelling mistakes are smoothly repaired via Levenshtein edit-distance without halting. |
| **Overlapping Genes** (PhiX174 reading two different proteins from the same sequence) | 1D sequential execution: every routine requires its own separate memory footprint. | **CatDog Multi-Framing**: Interleave two complete programs on the exact same line of code; read at offset 0 (Cat) or offset 1 (Dog) for 2x memory density. |
| **mRNA Half-Life Decay** (Poly-A tail shortens on each translation until transcript dissolves) | Memory leaks in C/C++; periodic CPU freezes from Garbage Collectors in Java/Python. | **Acme Anvil TTL**: Ephemeral variables carry an auto-decrementing `acme(ttl=N)` timer. Once expired, it vaporizes from RAM with zero memory leaks and 0% GC pauses. |
| **Lock-and-Key Receptors** (Proteins find targets by 3D physical pocket shape, not pointers) | Fragile numeric memory pointers (`0x7FFF`) and hard-coded network IP endpoints. | **Planetary Shape Dispatch**: Functions bind to elemental and planetary rings (`MERCURY`, `MARS`, `JUPITER`, `VENUS`, `MOON`). Callers emit ring keys to trigger matching handlers. |
| **p53 DNA Repair Checkpoint** ("Guardian of the genome" catching unrouted sequences) | Unhandled exceptions and crash cascades. | **Tuxedo Mask Watchdog**: Catches unrouted dispatches with a graceful fallback block ("My work here is done!"). |
| **Cellular Differentiation** (Stem cells differentiating into specialized tissue states) | State evolution and polymorphic typing. | **Sailor Moon Transformation**: `transform` / `MOON_PRISM_POWER` blocks explicitly evolve state objects. |

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

# 5. Sailor Moon State Transformation (Cellular Differentiation)
let guardian = "Usagi_Tsukino"
transform guardian = "Princess_Serenity" {
    print "State transformed to royal tier!"
}

halt
```

---

## 🧪 Automated Testing
Run the comprehensive test suite:
```powershell
python -m pytest D:\smc_lang\tests/
```
**All 24 tests pass in 0.13 seconds!**

---

## 🎨 VS Code Syntax Highlighting Extension

SMC includes an official VS Code extension for full syntax coloring!

To install it:
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
