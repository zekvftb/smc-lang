# 🚀 Release Notes: SMC (Saturday Morning Cartoons) v1.0.0
**The Biologically-Inspired, Bytecode-Compiled Multi-Phase Language & Virtual Machine**

**Release Version:** `v1.0.0`  
**Date:** 2026-08-31  
**License:** Fair-Source 1.0 (Free for Individuals & Research, Commercial for Enterprise)  
**Automated Tests:** ✅ **91 / 91 Unit & Integration Tests Passing**  
**Live Web Playground:** [zekvftb.github.io/smc-lang/docs/playground](https://zekvftb.github.io/smc-lang/docs/playground/)

---

## 🌟 Highlights & Major Capabilities

### 1. ⚡ High-Throughput Linear Bytecode Compiler & Stack VM
* Compiles AST programs into compact linear bytecode instructions (`LOAD_CONST`, `STORE_VAR`, `BINARY_OP`, `JUMP`, `CALL_BUILTIN`, `HALT`).
* Sub-millisecond execution speeds exceeding **5,000 ops/ms**.
* Strict mode (`--strict`) enforcing exact keyword grammar, explicit `ZeroDivisionError`, `NameError`, and `IndexError` traps.

### 2. 🐞 Interactive Step Debugger (`smc debug`)
* Step through SMC programs interactively with breakpoints (`b <step>`), variable watchlists (`w <var>`), expression evaluator (`eval <expr>`), and active reading phase diagrams (`p`).

### 3. 🌐 Interactive Zero-Dependency Web Playground
* Standalone browser runtime with a real-time **3-track conveyor belt animation** for Reading Phase Register shifts ($\Phi = 0, 1, 2$), live stack inspector, and Acme TTL countdown cards.

### 4. 🧬 Genetic Programming (GP) Evolution Engine (`smc.evolution`)
* Evolve SMC AST programs toward arbitrary objective mathematical or algorithmic targets using native `mutate`, `slip`, and `attenuator` primitives with 100% seeded deterministic reproducibility.

### 5. 🛡️ Ephemeral Acme TTL State Machines & Chaos Resilience (`smc.chaos`)
* First-class ephemeral variables (`acme(ttl=k)`) that automatically decay and drop an anvil on expiration.
* Chaos fault-injection harness with Tuxedo Mask fallback handlers achieving 100% fault recovery.

---

## 🚀 Quickstart Installation
```powershell
pip install smc-lang
```
or install locally:
```powershell
git clone https://github.com/zekvftb/smc-lang.git
cd smc-lang
pip install -e .
smc --version
```
Launch interactive REPL:
```powershell
smc
```
Launch interactive step debugger:
```powershell
smc debug examples/bubble_sort.smc
```
